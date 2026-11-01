"""Finite sequential interpreter, not a native concurrency or Noita test."""
import itertools
import json

EVENTS = ('AR', 'AW', 'BR', 'BW')
EXPECTED = {
    ('AR', 'AW', 'BR', 'BW'): (1, 1),
    ('AR', 'BR', 'AW', 'BW'): (2, 1),
    ('AR', 'BR', 'BW', 'AW'): (2, 1),
    ('BR', 'BW', 'AR', 'AW'): (2, 2),
    ('BR', 'AR', 'BW', 'AW'): (2, 1),
    ('BR', 'AR', 'AW', 'BW'): (2, 1),
}

def evaluate(schedule, snapshot=False):
    if len(schedule) != 4 or set(schedule) != set(EVENTS):
        raise ValueError('Expected each of four known events exactly once')
    state = {'x': 1, 'y': 2}
    reads = dict(state) if snapshot else state
    temporary = {}
    for event in schedule:
        actor, operation = event
        source, target = ('x', 'y') if actor == 'A' else ('y', 'x')
        if operation == 'R':
            temporary[actor] = reads[source]
        elif actor not in temporary:
            raise ValueError('Write before own read')
        else:
            state[target] = temporary[actor]
    return state['x'], state['y']

def main():
    schedules = [p for p in itertools.permutations(EVENTS)
                 if p.index('AR') < p.index('AW') and p.index('BR') < p.index('BW')]
    if set(schedules) != set(EXPECTED):
        raise RuntimeError('Enumerated schedule set differs from frozen expectation')
    rows = []
    for schedule in schedules:
        current = evaluate(schedule)
        snapshot = evaluate(schedule, snapshot=True)
        if current != EXPECTED[schedule] or snapshot != (2, 1):
            raise RuntimeError('Outcome differs from frozen expectation')
        rows.append({'events': list(schedule), 'current_state': list(current),
                     'immutable_input': list(snapshot)})
    invalid = [('AR', 'AW', 'BR'), ('AR', 'AW', 'BR', 'ZZ'),
               ('AR', 'AR', 'BR', 'BW'), ('AW', 'AR', 'BR', 'BW'),
               ('AR', 'AW', 'BW', 'BR')]
    rejected = 0
    for schedule in invalid:
        try:
            evaluate(schedule)
        except ValueError:
            rejected += 1
        else:
            raise RuntimeError('Invalid schedule accepted')
    print(json.dumps({'status': 'PASS', 'scope': 'Finite sequential event interpreter only',
                      'initial': {'x': 1, 'y': 2}, 'schedules': rows,
                      'invalid_schedules_rejected': rejected}, sort_keys=True))

if __name__ == '__main__':
    main()
