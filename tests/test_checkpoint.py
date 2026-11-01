# Verify durable session records, callback byte preservation, and seizure failure handling.
import ctypes
import json
import queue
import threading
import unittest
from pathlib import Path
from unittest.mock import patch

from ring_diagnostics import cli, confirmation, guided, journal


class FakeCoreFoundation:
    def CFRunLoopGetCurrent(self):
        return 17


class FakeIOKit:
    def __init__(self, results):
        self.results = iter(results)
        self.closed = []
        self.callbacks = []

    def IOHIDDeviceOpen(self, device, options):
        return next(self.results)

    def IOHIDDeviceRegisterInputReportCallback(self, device, buffer, length, callback, context):
        self.callbacks.append(callback)

    def IOHIDDeviceRegisterRemovalCallback(self, *arguments):
        pass

    def IOHIDDeviceScheduleWithRunLoop(self, *arguments):
        pass

    def IOHIDDeviceUnscheduleFromRunLoop(self, *arguments):
        pass

    def IOHIDDeviceClose(self, device, options):
        self.closed.append(device)
        return 0


class CheckpointTests(unittest.TestCase):
    def test_guided_plan_covers_basic_matrix_and_groups_modes(self):
        plan = guided.plan()
        self.assertEqual(len(plan), 24)
        self.assertEqual([case['mode'] for case in plan], ['T'] * 12 + ['C'] * 12)
        self.assertEqual(len({(case['mode'], case['button'], case['action']) for case in plan}), 24)

    def test_guided_repeat_and_skip_are_recorded(self):
        events = queue.Queue()
        state = {'plan': guided.plan(), 'index': 0, 'mode': 'T', 'waiting_for_mode': True, 'trial': None, 'attempt': 0}
        self.assertTrue(guided.advance(state, '\n', cli.emit, events))
        state['report_count'] = 2
        self.assertTrue(guided.advance(state, 'r\n', cli.emit, events))
        self.assertEqual(state['index'], 0)
        self.assertTrue(guided.advance(state, 's\n', cli.emit, events))
        self.assertEqual(state['index'], 1)
        ends = [fields for event, fields in events.queue if event == 'trial_end']
        self.assertEqual([item['outcome'] for item in ends], ['repeat_requested', 'skipped'])
        self.assertEqual(ends[0]['received_reports'], 2)

    def test_journal_preserves_order_and_bytes(self):
        stream, session_id, path = journal.create_session(Path('tmp/20261101_checkpoint_tests'))
        journal.record(stream, session_id, 1, 'input_report', raw_hex='030000ff', report_id=3)
        stream.close()
        data = json.loads(path.read_text())
        self.assertEqual((data['sequence'], data['raw_hex'], data['report_id']), (1, '030000ff', 3))
        self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_partial_seize_fails_and_closes_first_device(self):
        events = queue.Queue()
        io = FakeIOKit([0, -1])
        with patch.object(cli.native, 'describe', return_value={'MaxInputReportSize': 5}), patch.object(cli.ctypes.c_void_p, 'in_dll', return_value=ctypes.c_void_p(9)):
            result = cli.run_capture(FakeCoreFoundation(), io, [1, 2], events, [])
        self.assertEqual(result, 1)
        self.assertEqual(io.closed, [1])
        recorded = list(events.queue)
        self.assertTrue(any(event == 'capture_not_ready' for event, _ in recorded))
        self.assertFalse(any(event == 'capture_ready' for event, _ in recorded))

    def test_callback_preserves_actual_bytes_and_id(self):
        events = queue.Queue()
        io = FakeIOKit([0])
        with patch.object(cli.native, 'describe', return_value={'MaxInputReportSize': 5}), patch.object(cli.ctypes.c_void_p, 'in_dll', return_value=ctypes.c_void_p(9)):
            opened = cli.open_devices(FakeCoreFoundation(), io, [1], events, threading.Event())
        data = (ctypes.c_uint8 * 3)(2, 64, 0)
        io.callbacks[0](None, 0, None, 0, 2, data, 3)
        event, fields = list(events.queue)[-1]
        self.assertEqual((event, fields['report_id'], fields['raw_hex'], fields['length']), ('input_report', 2, '024000', 3))
        self.assertEqual(len(opened), 1)


class ConfirmationTests(unittest.TestCase):
    def setUp(self):
        self.state = confirmation.create_state()
        self.events = queue.Queue()

    def advance(self, line, now=0):
        return confirmation.advance(self.state, line, cli.emit, self.events, now)

    def tick(self, now):
        confirmation.tick(self.state, cli.emit, self.events, now)

    def test_plan_controls_and_single_mode_change(self):
        plan = self.state['plan']
        self.assertEqual(len(plan), 8)
        self.assertEqual([case['mode'] for case in plan], ['T'] * 2 + ['C'] * 6)
        self.assertTrue(all(case['repetitions'] == 1 for case in plan))

    def test_tail_reports_stay_in_trial_and_extra_enter_does_not_skip(self):
        self.advance('\n')
        self.advance('\n')
        self.advance('\n')
        self.assertEqual(self.state['phase'], 'settling')
        self.assertFalse(any(event == 'trial_end' for event, _ in self.events.queue))
        self.state['report_count'] = 3
        self.tick(999_999_999)
        self.assertEqual(self.state['index'], 0)
        self.tick(1_000_000_000)
        endings = [fields for event, fields in self.events.queue if event == 'trial_end']
        self.assertEqual(endings[0]['received_reports'], 3)
        self.assertFalse(endings[0]['verified'])
        self.assertEqual((self.state['index'], self.state['phase']), (1, 'action'))

    def test_repeat_preserves_rejected_attempt(self):
        self.advance('\n')
        first_id = self.state['trial_id']
        self.advance('r\n')
        self.tick(1_000_000_000)
        self.assertEqual(self.state['index'], 0)
        self.assertNotEqual(self.state['trial_id'], first_id)
        ending = [fields for event, fields in self.events.queue if event == 'trial_end'][0]
        self.assertEqual(ending['outcome'], 'repeat_requested')

    def test_complete_flow_has_eight_attempts_and_no_timing_claim(self):
        self.advance('\n')
        for index in range(8):
            if self.state['phase'] == 'mode':
                self.advance('\n', index * 2_000_000_000)
            self.advance('\n', index * 2_000_000_000)
            self.tick(index * 2_000_000_000 + 1_000_000_000)
        self.assertTrue(self.state['finished'])
        self.assertIsNone(self.state['trial'])
        endings = [fields for event, fields in self.events.queue if event == 'trial_end']
        self.assertEqual(len(endings), 8)
        self.assertTrue(all(not ending['verified'] for ending in endings))
        self.assertFalse(any(event == 'physical_action_cue' for event, _ in self.events.queue))


if __name__ == '__main__':
    unittest.main()
