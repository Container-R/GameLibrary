"""Compare representations of supplied input events; no SDL or device access.

Policy: one application request for each non-repeat down. The interval starts
unheld; pressed_seen starts false and is not cleared by up. The request list
is not a combat scheduler and does not claim that attacks will execute.
"""
import json


def reduce_events(events):
    held = False
    pressed_seen = False
    requests = []
    for kind, repeat in events:
        if kind not in ('down', 'up'):
            raise ValueError('unknown event kind')
        if kind == 'up' and repeat:
            raise ValueError('repeat-up outside this example')
        held = kind == 'down'
        if kind == 'down' and not repeat:
            pressed_seen = True
            requests.append('A' + str(len(requests) + 1))
    return {'held': held, 'pressed_seen': pressed_seen, 'requests': requests}


def main():
    cases = {
        'none': [],
        'short_press': [('down', False), ('up', False)],
        'two_short_presses': [('down', False), ('up', False),
                              ('down', False), ('up', False)],
        'held_with_repeats': [('down', False), ('down', True), ('down', True)],
    }
    expected = {
        'none': (False, False, []),
        'short_press': (False, True, ['A1']),
        'two_short_presses': (False, True, ['A1', 'A2']),
        'held_with_repeats': (True, True, ['A1']),
    }
    results = {}
    for name, events in cases.items():
        result = reduce_events(events)
        assert tuple(result.values()) == expected[name], name
        results[name] = result
    final_snapshot = results['short_press']['held']
    incorrectly_guarded = [kind for kind, repeat in cases['short_press']
                           if kind == 'down' and not repeat and final_snapshot]
    assert incorrectly_guarded == []
    assert results['short_press']['requests'] == ['A1']
    print(json.dumps({'scope': 'supplied data only; no SDL, OS or hardware test',
                      'cases': results,
                      'snapshot_guard_drops_short_press': not incorrectly_guarded},
                     indent=2))


if __name__ == '__main__':
    main()
