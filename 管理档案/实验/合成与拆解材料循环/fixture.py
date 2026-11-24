"""Exact reachability for bounded, synthetic game-recipe configurations."""
from collections import deque
from dataclasses import dataclass

# State positions: scrap, parts (measured output), slag, station charge.
@dataclass(frozen=True)
class Case:
    name: str
    seed: tuple[int, int, int, int]
    refund: int = 3
    metered: bool = False
    bag: int | None = None


def transitions(case, state):
    # Each recipe is one atomic transformation: consume requirements first,
    # then test post-operation inventory space. No discard/commerce/refresh.
    recipes = (
        ("craft", (3, 0, 0, 0), (0, 2, 1, 0)),
        ("disassemble", (0, 1, 1, int(case.metered)), (case.refund, 0, 0, 0)),
    )
    for name, required, output in recipes:
        if not all(have >= need for have, need in zip(state, required)):
            continue
        nxt = tuple(have - need + got for have, need, got in zip(state, required, output))
        if case.bag is None or sum(nxt[:3]) <= case.bag:
            yield name, nxt


def reachable(case, max_steps):
    # Discover each complete state at its shortest depth. Continue through
    # max_steps; detect omitted successors to distinguish cutoff from closure.
    root = case.seed
    seen = {root: (0, None, None)}
    queue = deque([root])
    while queue:
        state = queue.popleft()
        depth = seen[state][0]
        if depth == max_steps:
            continue
        for name, nxt in transitions(case, state):
            if nxt not in seen:
                seen[nxt] = (depth + 1, state, name)
                queue.append(nxt)
    closed = all(nxt in seen for state in seen for _, nxt in transitions(case, state))
    return seen, closed


def trace(seen, state):
    steps = []
    while seen[state][1] is not None:
        _, before, name = seen[state]
        steps.append((name, state))
        state = before
    return list(reversed(steps))


def growth(case, seen):
    # Target rises and every other tracked coordinate exactly returns to seed.
    return [state for state in seen if state[1] > case.seed[1]
            and all(state[i] == case.seed[i] for i in (0, 2, 3))]


cases = (
    Case("baseline", (3, 0, 0, 0)),
    Case("no_seed", (0, 0, 0, 0)),
    Case("refund_two", (3, 0, 0, 0), refund=2),
    Case("one_station_charge", (3, 0, 0, 1), metered=True),
    Case("bag_three", (3, 0, 0, 0), bag=3),
    Case("bag_four", (3, 0, 0, 0), bag=4),
)

expected = (
    (9, False, 4, (3, 4, 0, 0)),
    (1, True, 0, (0, 0, 0, 0)),
    (3, True, 0, (2, 1, 0, 0)),
    (4, True, 0, (0, 3, 1, 0)),
    (2, True, 0, (0, 2, 1, 0)),
    (4, True, 1, (3, 1, 0, 0)),
)

print("state=(scrap, parts, slag, station_charge); action horizon=8")
for case, (count, closure, witness_count, point) in zip(cases, expected):
    states, closed = reachable(case, 8)
    wins = growth(case, states)
    assert (len(states), closed, len(wins)) == (count, closure, witness_count), (case.name, states, wins)
    assert point in states
    print(f"{case.name}: states={len(states)} closed={closed} restored_growth_states={len(wins)}")
    print(f"  example: {case.seed} -> " + (" -> ".join(f"{a}:{s}" for a, s in trace(states, point)) or "(none)"))

# Independent replay check: after one successful round, can the exact same
# two actions immediately be applied once more?
for case in (cases[0], cases[-1]):
    def try_round(state):
        for action in ("craft", "disassemble"):
            state = dict(transitions(case, state)).get(action)
            if state is None:
                return None
        return state
    one = try_round(case.seed)
    assert one is not None
    two = try_round(one)
    assert two == ((3, 2, 0, 0) if case.name == "baseline" else None)
    print(f"{case.name}: after one round={one}, replay same round={two}")
