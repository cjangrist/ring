# Guided, mode-grouped physical trials; report bytes remain separate from user labels.


def plan() -> list:
    buttons = [('upper', 13, 16), ('middle', 14, 17), ('lower', 15, 18)]
    actions = [
        ('single', 5, 'Tap {button} five times, about two seconds apart.'),
        ('double', 3, 'Double-tap {button} three times, pausing about two seconds between each double.'),
        ('triple', 3, 'Triple-tap {button} three times, pausing about two seconds between each triple.'),
        ('hold', 3, 'Hold {button} for about two seconds, release, and repeat three times; pause between holds.'),
    ]
    return [
        {'mode': mode, 'button': button, 'action': action, 'repetitions': repetitions,
         'checklist_id': (t_id if mode == 'T' else c_id) if action == 'single' else {'double': 29, 'triple': 31, 'hold': 34}[action],
         'instruction': instruction.format(button=button)}
        for mode in ('T', 'C') for action, repetitions, instruction in actions
        for button, t_id, c_id in buttons
    ]


def prompt_mode(mode: str) -> None:
    print(f'\nSet the ring switch to {mode} mode. Press Enter when ready (q quits).', flush=True)


def start_trial(state: dict, emit: object, events: object) -> None:
    trial = state['plan'][state['index']]
    state['trial'] = trial
    state['report_count'] = 0
    state['attempt'] += 1
    identifier = f"{trial['mode']}-{trial['button']}-{trial['action']}-{state['attempt']}"
    state['trial_id'] = identifier
    emit(events, 'trial_start', trial_id=identifier, trial=trial, physical_timing='not independently measured')
    print(f"\n[{state['index'] + 1}/{len(state['plan'])}] Checklist #{trial['checklist_id']} | "
          f"Mode {trial['mode']} | {trial['button']} | {trial['action']}", flush=True)
    print(trial['instruction'], flush=True)
    print('When finished, wait one second, then press Enter. Type r + Enter to repeat, s + Enter to skip, or q + Enter to quit.', flush=True)


def advance(state: dict, line: str, emit: object, events: object) -> bool:
    choice = line.strip()
    if choice.lower() == 'q':
        if state.get('trial'):
            emit(events, 'trial_interrupted', trial_id=state['trial_id'], reason='user_quit', received_reports=state['report_count'])
            state['trial'] = None
        return False
    if state['waiting_for_mode']:
        emit(events, 'physical_mode_confirmation', user_selected_mode=state['mode'], note=choice or None)
        state['waiting_for_mode'] = False
        start_trial(state, emit, events)
        return True
    outcome = 'skipped' if choice.lower() == 's' else 'repeat_requested' if choice.lower() == 'r' else 'user_finished'
    emit(events, 'trial_end', trial_id=state['trial_id'], outcome=outcome,
         received_reports=state['report_count'], note=choice if outcome == 'user_finished' and choice else None,
         verified=False)
    state['trial'] = None
    if outcome != 'repeat_requested':
        state['index'] += 1
    if state['index'] == len(state['plan']):
        emit(events, 'guided_plan_complete', trials=len(state['plan']), results_verified=False)
        print('\nGuided capture complete. The raw data still needs review.', flush=True)
        return False
    new_mode = state['plan'][state['index']]['mode']
    if new_mode != state['mode']:
        state['mode'], state['waiting_for_mode'] = new_mode, True
        prompt_mode(new_mode)
    else:
        start_trial(state, emit, events)
    return True
