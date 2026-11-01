# Part two: one attempt per prompt, timed cues, controls, and explicit timing uncertainty.


def plan() -> list:
    cases = []
    for mode in ('T', 'C'):
        for button in ('upper', 'middle', 'lower'):
            block = [('single', 1, 0, 'control_before'), ('double', 2, 250, 'quick'),
                     ('double', 2, 1000, 'spaced'), ('triple', 3, 250, 'quick_1'),
                     ('triple', 3, 250, 'quick_2')]
            if mode == 'C' and button in ('middle', 'lower'):
                block += [('hold', 1, 0, 'hold_1'), ('hold', 1, 0, 'hold_2')]
            block += [('single', 1, 0, 'control_after')]
            cases.extend({'mode': mode, 'button': button, 'action': action, 'tap_count': count,
                          'cue_onset_interval_ms': interval, 'variant': variant, 'repetitions': 1,
                          'requested_hold_ms': 2000 if action == 'hold' else None,
                          'block_id': f'{mode}-{button}'} for action, count, interval, variant in block)
    return cases


def create_state() -> dict:
    return {'plan': plan(), 'index': 0, 'mode': 'T', 'phase': 'mode', 'trial': None,
            'attempt': 0, 'report_count': 0, 'timing_valid': True}


def prompt(state: dict) -> None:
    trial = state['plan'][state['index']]
    if trial['mode'] != state['mode'] or state['phase'] == 'mode':
        state['mode'], state['phase'] = trial['mode'], 'mode'
        print(f"\nSwitch to {trial['mode']} mode; leave it there until asked. Enter when ready, q to quit.", flush=True)
        return
    state['phase'] = 'ready'
    print(f"\n[{state['index'] + 1}/{len(state['plan'])}] {trial['mode']} / {trial['button'].upper()} / "
          f"{trial['action']} ({trial['variant']})", flush=True)
    if trial['action'] == 'hold':
        print('ONE hold: press on HOLD, keep holding, release on RELEASE (about 2 seconds).', flush=True)
    else:
        print(f"ONE attempt: {trial['tap_count']} short tap(s), one per TAP cue. "
              f"Cue spacing: {trial['cue_onset_interval_ms']} ms between starts." if trial['tap_count'] > 1
              else 'ONE short tap on the TAP cue.', flush=True)
    print('Enter to start the countdown; s skips; q quits. Release fully between taps.', flush=True)


def schedule(trial: dict) -> list:
    cues = [(0, 'Ready: 2'), (1, 'Ready: 1')]
    if trial['action'] == 'hold':
        cues += [(2, 'HOLD'), (4, 'RELEASE')]
    else:
        cues += [(2 + index * trial['cue_onset_interval_ms'] / 1000, f"TAP {index + 1}/{trial['tap_count']}")
                 for index in range(trial['tap_count'])]
    return cues + [(cues[-1][0] + 2, 'FINISHED')]


def arm(state: dict, emit: object, events: object, now_ns: int) -> None:
    state['attempt'] += 1
    state['trial'] = state['plan'][state['index']]
    trial = state['trial']
    state['trial_id'] = f"part2-{state['index'] + 1:02d}-attempt{state['attempt']}"
    state.update(phase='cues', report_count=0, timing_valid=True, cue_index=0, started_ns=now_ns)
    state['cues'] = schedule(trial)
    emit(events, 'trial_start', trial_id=state['trial_id'], trial=trial,
         physical_timing='unmeasured; cue timestamps are instructions, not observed physical presses')


def tick(state: dict, emit: object, events: object, now_ns: int) -> None:
    if state['phase'] != 'cues':
        return
    offset, label = state['cues'][state['cue_index']]
    scheduled_ns = state['started_ns'] + round(offset * 1_000_000_000)
    if now_ns < scheduled_ns:
        return
    lateness_ms = (now_ns - scheduled_ns) / 1_000_000
    if lateness_ms > 150:
        state.update(timing_valid=False, phase='review')
        emit(events, 'cue_timing_invalid', trial_id=state['trial_id'], lateness_ms=lateness_ms,
             intended_cue=label, scheduled_monotonic_ns=scheduled_ns)
        print('\nCue timing was delayed. Release the ring. Type r + Enter to retry.', flush=True)
        return
    emit(events, 'physical_action_cue', trial_id=state['trial_id'], cue=label,
         scheduled_monotonic_ns=scheduled_ns, emitted_monotonic_ns=now_ns, lateness_ms=lateness_ms)
    print(f'  >>> {label}', flush=True)
    state['cue_index'] += 1
    if label == 'FINISHED':
        state['phase'] = 'review'
        print(f"Received {state['report_count']} raw reports (NOT a count of presses).", flush=True)
        if not state['report_count']:
            print('No reports observed. This is saved as an uncertain result, not a failed test.', flush=True)
        print('Enter = attempt followed cues; r = timing/count was off, redo; s = skip; q = quit.', flush=True)
        print('Or type a note + Enter to keep an uncertain attempt and move on.', flush=True)


def finish(state: dict, choice: str, emit: object, events: object) -> bool:
    outcome = 'repeat_requested' if choice == 'r' else 'skipped' if choice == 's' else 'user_finished'
    emit(events, 'trial_end', trial_id=state['trial_id'], outcome=outcome,
         received_reports=state['report_count'], cue_timing_valid=state['timing_valid'],
         user_reports_followed_cues=not choice, note=choice if choice not in ('', 'r', 's') else None,
         verified=False)
    state['trial'] = None
    if choice != 'r':
        state['index'] += 1
    return next_prompt(state, emit, events)


def next_prompt(state: dict, emit: object, events: object) -> bool:
    if state['index'] == len(state['plan']):
        emit(events, 'guided_plan_complete', plan_version=2, trials=len(state['plan']), results_verified=False)
        print('\nPart two complete. Saved for review; no action mappings were enabled.', flush=True)
        return False
    prompt(state)
    return True


def advance(state: dict, line: str, emit: object, events: object, now_ns: int) -> bool:
    choice = line.strip()
    if choice == 'q':
        if state.get('trial'):
            emit(events, 'trial_interrupted', trial_id=state['trial_id'], reason='user_quit', received_reports=state['report_count'])
            state['trial'] = None
        return False
    if state['phase'] == 'mode':
        if choice:
            print('Use Enter to confirm the switch position, or q to quit.', flush=True)
            return True
        emit(events, 'physical_mode_confirmation', user_selected_mode=state['mode'])
        state['phase'] = 'ready'
        prompt(state)
    elif state['phase'] == 'ready':
        if choice == 's':
            emit(events, 'trial_skipped', plan_index=state['index'], trial=state['plan'][state['index']])
            state['index'] += 1
            return next_prompt(state, emit, events)
        if choice:
            print('Press Enter to start, s to skip, or q to quit.', flush=True)
        else:
            arm(state, emit, events, now_ns)
    elif state['phase'] == 'cues':
        emit(events, 'premature_completion_ignored', trial_id=state['trial_id'], entered_text=choice)
        print('Keep following the cues. Wait for FINISHED before confirming (q quits).', flush=True)
    else:
        return finish(state, choice, emit, events)
    return True
