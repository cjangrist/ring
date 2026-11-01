# A short, self-paced retry of silent cases; physical timing stays explicitly unknown.


def plan() -> list:
    prompts = [
        ('T', 'upper', 'triple', 'Press the TOP button three times quickly, in one little burst.'),
        ('T', 'lower', 'triple', 'Press the BOTTOM button three times quickly, in one little burst.'),
        ('C', 'upper', 'double', 'Double-click the TOP button, just like you would double-click a mouse.'),
        ('C', 'lower', 'double', 'Double-click the BOTTOM button, just like you would double-click a mouse.'),
        ('C', 'upper', 'triple', 'Press the TOP button three times quickly, in one little burst.'),
        ('C', 'lower', 'triple', 'Press the BOTTOM button three times quickly, in one little burst.'),
        ('C', 'middle', 'hold', 'Hold the MIDDLE button while you say "one, two", then let go.'),
        ('C', 'lower', 'hold', 'Hold the BOTTOM button while you say "one, two", then let go.'),
    ]
    return [{'mode': mode, 'button': button, 'action': action, 'instruction': instruction,
             'repetitions': 1, 'physical_timing': 'natural pace; not independently measured'}
            for mode, button, action, instruction in prompts]


def create_state() -> dict:
    return {'plan': plan(), 'index': 0, 'mode': 'T', 'phase': 'mode', 'trial': None,
            'attempt': 0, 'report_count': 0, 'finished': False}


def prompt(state: dict) -> None:
    print(f"\nSet the switch to {state['mode']}. Press Enter when ready.", flush=True)


def start_trial(state: dict, emit: object, events: object) -> None:
    state['attempt'] += 1
    state['trial'] = state['plan'][state['index']]
    state['trial_id'] = f"easy-{state['index'] + 1:02d}-attempt{state['attempt']}"
    state.update(phase='action', report_count=0)
    emit(events, 'trial_start', trial_id=state['trial_id'], trial=state['trial'],
         physical_timing='natural pace; not independently measured')
    print(f"\n{state['index'] + 1} of {len(state['plan'])} · {state['mode']} mode", flush=True)
    print(state['trial']['instruction'], flush=True)
    print('Do that once. Press Enter when done.', flush=True)


def tick(state: dict, emit: object, events: object, now_ns: int) -> None:
    if state['phase'] != 'settling' or now_ns < state['finish_after_ns']:
        return
    choice = state['choice']
    outcome = 'repeat_requested' if choice == 'r' else 'skipped' if choice == 's' else 'user_finished'
    emit(events, 'trial_end', trial_id=state['trial_id'], outcome=outcome,
         received_reports=state['report_count'], verified=False,
         note=choice if choice not in ('', 'r', 's') else None)
    state['trial'] = None
    print('Saved.', flush=True)
    if choice != 'r':
        state['index'] += 1
    if state['index'] == len(state['plan']):
        emit(events, 'guided_plan_complete', plan_version='2-easy', trials=len(state['plan']), results_verified=False)
        state.update(finished=True, phase='finished')
        print('\nAll done. Tell me when you are ready for me to read the log.', flush=True)
        return
    next_mode = state['plan'][state['index']]['mode']
    if next_mode != state['mode']:
        state.update(mode=next_mode, phase='mode')
        prompt(state)
    else:
        start_trial(state, emit, events)


def advance(state: dict, line: str, emit: object, events: object, now_ns: int) -> bool:
    choice = line.strip()
    if choice.lower() == 'q':
        if state.get('trial'):
            emit(events, 'trial_interrupted', trial_id=state['trial_id'], reason='user_quit', received_reports=state['report_count'])
            state['trial'] = None
        return False
    if state['phase'] == 'mode':
        if choice:
            print('Press Enter when the switch is in place, or q to quit.', flush=True)
        else:
            emit(events, 'physical_mode_confirmation', user_selected_mode=state['mode'])
            start_trial(state, emit, events)
    elif state['phase'] == 'action':
        emit(events, 'user_finished_action', trial_id=state['trial_id'], entered_text=choice)
        state.update(phase='settling', choice=choice, finish_after_ns=now_ns + 1_000_000_000)
    elif state['phase'] == 'settling':
        emit(events, 'extra_enter_ignored', trial_id=state['trial_id'], entered_text=choice)
    return True
