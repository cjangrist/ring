# Logger-only macOS F3 checkpoint: inventory, exclusive open, and raw report capture.
import argparse
import ctypes
import datetime
import os
import queue
import select
import signal
import sys
import threading
import time
from pathlib import Path

from f3_ring import confirmation, guided, journal, native


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Inventory and exclusively capture the paired F3 HID device on macOS.')
    parser.add_argument('--product', default='F3', help='Exact HID product name (default: F3).')
    parser.add_argument('--sessions', type=Path, default=Path('sessions'), help='Directory for timestamped JSONL sessions.')
    parser.add_argument('--inventory', action='store_true', help='Inventory matching devices without seizing them.')
    parser.add_argument('--request-access', action='store_true', help='Ask macOS for Input Monitoring access if needed.')
    parser.add_argument('--guided', action='store_true', help='Run the mode-grouped interactive physical tests.')
    parser.add_argument('--guided-part2', action='store_true', help='Run eight short, self-paced confirmation tests.')
    options = parser.parse_args()
    options.guided = options.guided or options.guided_part2
    if options.guided and options.inventory:
        parser.error('Choose either guided capture or inventory.')
    return options


def writer_loop(stream: object, session_id: str, events: queue.Queue, failure: list, quiet: bool = False) -> None:
    sequence = 0
    try:
        while True:
            item = events.get()
            if item is None:
                return
            sequence += 1
            event, fields = item
            journal.record(stream, session_id, sequence, event, console=not quiet or event in ('error', 'capture_not_ready'), **fields)
    except Exception as error:
        failure.append(repr(error))
        print(f'FATAL: journal writer failed: {error!r}', file=sys.stderr, flush=True)


def emit(events: queue.Queue, event: str, **fields: object) -> None:
    fields['observed_utc'] = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec='microseconds')
    fields['observed_monotonic_ns'] = time.monotonic_ns()
    events.put((event, fields))


def open_devices(cf: object, io: object, devices: list, events: queue.Queue, stopped: threading.Event, state: dict | None = None) -> list:
    opened = []
    run_loop = cf.CFRunLoopGetCurrent()
    run_mode = ctypes.c_void_p.in_dll(cf, 'kCFRunLoopDefaultMode').value
    for index, device in enumerate(devices):
        details = native.describe(cf, io, device)
        emit(events, 'device_inventory', device_index=index, details=details)
        result = io.IOHIDDeviceOpen(device, 1)
        emit(events, 'seize_result', device_index=index, result=result, result_hex=f'0x{result & 0xffffffff:08x}', success=result == 0)
        if result != 0:
            return opened
        buffer = (ctypes.c_uint8 * max(4096, details.get('MaxInputReportSize') or 0))()
        def report(context, status, sender, report_type, report_id, data, length, *, index=index):
            raw = ctypes.string_at(data, length) if length >= 0 else b''
            trial_id = state.get('trial_id') if state and state.get('trial') else None
            if trial_id:
                state['report_count'] += 1
            emit(events, 'input_report', device_index=index, status=status, report_type=report_type,
                 report_id=report_id, length=length, raw_hex=raw.hex(), connection_generation=1, trial_id=trial_id)
        def removal(context, status, sender, *, index=index):
            emit(events, 'device_removed', device_index=index, status=status)
            stopped.set()
        report_callback = native.REPORT_CALLBACK(report)
        removal_callback = native.REMOVAL_CALLBACK(removal)
        io.IOHIDDeviceRegisterInputReportCallback(device, buffer, len(buffer), report_callback, None)
        io.IOHIDDeviceRegisterRemovalCallback(device, removal_callback, None)
        io.IOHIDDeviceScheduleWithRunLoop(device, run_loop, run_mode)
        opened.append((device, buffer, report_callback, removal_callback, run_loop, run_mode))
    return opened


def capture_loop(cf: object, run_mode: int, state: dict, events: queue.Queue,
                 stopped: threading.Event, failure: list, interactive: bool, part2: bool) -> None:
    while not stopped.is_set() and not failure:
        cf.CFRunLoopRunInMode(run_mode, 0.01 if part2 else 0.1, False)
        if stopped.is_set():
            break
        if part2:
            confirmation.tick(state, emit, events, time.monotonic_ns())
            if state['finished']:
                stopped.set()
                break
        if interactive and select.select([sys.stdin], [], [], 0)[0]:
            line = sys.stdin.readline()
            active = bool(line) and (confirmation.advance(state, line, emit, events, time.monotonic_ns())
                                    if part2 else guided.advance(state, line, emit, events))
            if not active:
                stopped.set()


def run_capture(cf: object, io: object, devices: list, events: queue.Queue, failure: list,
                interactive: bool = False, part2: bool = False) -> int:
    stopped = threading.Event()
    previous_signal = signal.signal(signal.SIGINT, lambda *_: stopped.set())
    opened = []
    state = {'plan': guided.plan(), 'index': 0, 'mode': 'T', 'waiting_for_mode': True, 'trial': None, 'attempt': 0}
    if part2:
        state = confirmation.create_state()
    try:
        opened = open_devices(cf, io, devices, events, stopped, state if interactive else None)
        if len(opened) != len(devices):
            emit(events, 'capture_not_ready', reason='At least one matching HID entry could not be seized.')
            return 1
        emit(events, 'capture_ready', seized_entries=len(opened), suppression_verified=False,
             message='All matching entries opened exclusively. Press a button; verify native effects separately. Ctrl-C stops capture.')
        if interactive:
            print(f'Exclusive open succeeded for {len(opened)} F3 HID entry/entries. Raw capture is active.', flush=True)
            emit(events, 'guided_plan', plan_version='2-easy' if part2 else 1, trials=state['plan'])
            if part2:
                print('Just eight things to try, at your own pace. One try each is enough.', flush=True)
                print('Enter moves on. If you want a redo, type r + Enter; q quits.', flush=True)
                confirmation.prompt(state)
            else:
                guided.prompt_mode('T')
        capture_loop(cf, opened[0][5], state, events, stopped, failure, interactive, part2)
        return 1 if failure else 0
    finally:
        if interactive and state.get('trial'):
            emit(events, 'trial_interrupted', trial_id=state['trial_id'], reason='capture_stopped', received_reports=state['report_count'])
        for device, buffer, report, removal, run_loop, run_mode in reversed(opened):
            io.IOHIDDeviceUnscheduleFromRunLoop(device, run_loop, run_mode)
            result = io.IOHIDDeviceClose(device, 0)
            emit(events, 'device_closed', result=result)
        signal.signal(signal.SIGINT, previous_signal)


def execute(options: argparse.Namespace, events: queue.Queue, failure: list) -> int:
    if sys.platform != 'darwin':
        emit(events, 'error', reason='This checkpoint requires macOS.')
        return 1
    cf, io = native.libraries()
    access = io.IOHIDCheckAccess(1)
    emit(events, 'input_monitoring_access', code=access, state={0: 'granted', 1: 'denied', 2: 'unknown'}.get(access, 'unrecognized'))
    if options.request_access and access != 0:
        emit(events, 'input_monitoring_requested', granted=bool(io.IOHIDRequestAccess(1)), new_code=io.IOHIDCheckAccess(1))
    result, devices = native.inventory(cf, io, options.product)
    emit(events, 'inventory_result', product_exact=options.product, result=result,
         result_hex=f'0x{result & 0xffffffff:08x}', matching_entries=len(devices))
    try:
        if result != 0 or not devices:
            emit(events, 'capture_not_ready', reason='No matching connected HID entries or inventory failed; pair/connect the ring and retry.')
            return 1
        if options.inventory:
            [emit(events, 'device_inventory', device_index=index, details=native.describe(cf, io, device)) for index, device in enumerate(devices)]
            return 0
        return run_capture(cf, io, devices, events, failure, options.guided, options.guided_part2)
    finally:
        [cf.CFRelease(device) for device in devices]


def main() -> int:
    options = arguments()
    stream, session_id, path = journal.create_session(options.sessions)
    events, failure = queue.Queue(), []
    writer = threading.Thread(target=writer_loop, args=(stream, session_id, events, failure, options.guided), daemon=False)
    writer.start()
    exit_code = 1
    try:
        if options.guided:
            print(f'New session log: {path.resolve()}', flush=True)
        emit(events, 'session_start', environment=journal.environment(), arguments=vars(options) | {'sessions': str(options.sessions)}, journal_path=str(path.resolve()), pid=os.getpid())
        exit_code = execute(options, events, failure)
    except Exception as error:
        emit(events, 'error', exception=repr(error))
    finally:
        emit(events, 'session_end', exit_code=exit_code)
        events.put(None)
        writer.join()
        stream.close()
    return 1 if failure else exit_code


if __name__ == '__main__':
    sys.exit(main())
