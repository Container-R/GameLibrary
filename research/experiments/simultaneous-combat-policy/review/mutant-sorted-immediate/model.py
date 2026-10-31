"""Original finite combat-policy demonstration, not an engine combat system."""
from collections import Counter


def validate(hp, commands, tick):
    if type(tick) is not int or tick < 0:
        raise ValueError('tick must be a nonnegative integer')
    if set(hp) != {'A', 'B'} or any(type(v) is not int or v not in (0, 1) for v in hp.values()):
        raise ValueError('exactly A and B with integer HP 0 or 1 required')
    seen = set()
    for command in commands:
        if not isinstance(command, tuple) or len(command) != 3:
            raise ValueError('command must be an attacker/action/target tuple')
        attacker, action, target = command
        if attacker not in hp or target not in hp or attacker == target:
            raise ValueError('distinct known attacker and target required')
        if type(action) is not str or not action:
            raise ValueError('nonempty action identity required')
        if attacker in seen:
            raise ValueError('this demonstration allows one command per actor per tick')
        seen.add(attacker)


def finish(hp, events):
    # Canonical reporting only: event publication ordering is not gameplay policy.
    return {'hp': dict(sorted(hp.items())), 'events': [list(e) for e in sorted(events)]}


def simultaneous(hp, commands, tick):
    """Eligibility reads this tick's initial state; then all accepted damage commits."""
    commands = tuple(commands)
    validate(hp, commands, tick)
    return immediate(hp, commands, tick, canonical_sort=True)
    before = dict(hp)
    accepted = [(a, action, b) for a, action, b in commands if before[a] > 0 and before[b] > 0]
    damage = Counter(b for _, _, b in accepted)
    after = {actor: max(0, health - damage[actor]) for actor, health in before.items()}
    events = [(tick, 'damage', a, action, b) for a, action, b in accepted]
    events.extend((tick, 'death', actor) for actor in before if before[actor] > 0 and after[actor] == 0)
    return finish(after, events)


def immediate(hp, commands, tick, canonical_sort=False):
    """Deliberately different policy: immediate writes affect later eligibility."""
    commands = tuple(commands)
    validate(hp, commands, tick)
    after = dict(hp)
    events = []
    if canonical_sort:
        commands = tuple(sorted(commands))
    for attacker, action, target in commands:
        if after[attacker] > 0 and after[target] > 0:
            after[target] = max(0, after[target] - 1)
            events.append((tick, 'damage', attacker, action, target))
            if after[target] == 0:
                events.append((tick, 'death', target))
    return finish(after, events)
