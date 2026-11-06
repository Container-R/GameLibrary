"""Original teaching checks. No Box2D binding, engine execution, or geometry solver.

Callback inputs below are explicitly stipulated as already returned by the engine.
Only application role/owner aggregation and finite arithmetic are exercised.
"""
from dataclasses import dataclass
from itertools import permutations
from math import cos, sin, pi, isclose, sqrt
import json

@dataclass(frozen=True)
class Key:
    slot: int
    generation: int

@dataclass(frozen=True)
class Entity:
    key: Key
    team: str
    alive: bool = True
    receives: bool = True

@dataclass(frozen=True)
class CallbackItem:
    name: str
    owner: Key | None
    role: str
    sensor: bool = False

E, F, O, A, L = [Key(i, 1) for i in range(1, 6)]
entities = {
    E: Entity(E, "enemy"), F: Entity(F, "enemy"), O: Entity(O, "source"),
    A: Entity(A, "source"), L: Entity(L, "enemy"),
}
# These six shapes have stipulated engine acceptance. E0/G/J never enter
# this callback input list. This is not an emulation of Box2D overlap.
callbacks = (
    CallbackItem("E1", E, "Perception", True),
    CallbackItem("F0", F, "Hurtbox"),
    CallbackItem("O0", O, "Hurtbox"),
    CallbackItem("E2", E, "Hurtbox"),
    CallbackItem("A0", A, "Hurtbox"),
    CallbackItem("F1", F, "Hurtbox"),
)

def collect(items, capacity, registry=entities):
    accepted = set()
    failed = None
    responses = []
    for item in items:
        responses.append(True)
        if failed:
            continue
        if item.owner is None:
            failed = "MissingBinding"
            continue
        if item.role != "Hurtbox" or item.sensor:
            continue
        entity = registry.get(item.owner)
        if entity is None:
            failed = "StaleBinding"
            continue
        if item.owner == O or entity.team == "source":
            continue
        if not entity.alive or not entity.receives:
            continue
        if item.owner in accepted:
            continue
        if len(accepted) == capacity:
            failed = "InsufficientStorage"
            continue
        accepted.add(item.owner)
    # Whole attempt fails; no partial accepted set is exposed for effects.
    if failed:
        return failed, set(), responses
    return "Success", accepted, responses

success_orders = 0
failure_orders = 0
for order in permutations(callbacks):
    status, keys, responses = collect(order, 2)
    assert status == "Success" and keys == {E, F}
    assert all(responses) and len(responses) == len(callbacks)
    success_orders += 1
    status, keys, responses = collect(order, 1)
    assert status == "InsufficientStorage" and keys == set()
    assert all(responses)
    failure_orders += 1

# A third distinct eligible entity overflows a two-key set. A fresh retry
# using unchanged inputs and sufficient capacity contains all three keys.
more = callbacks + (CallbackItem("L0", L, "Hurtbox"),)
assert collect(more, 2)[:2] == ("InsufficientStorage", set())
assert collect(more, 3)[:2] == ("Success", {E, F, L})
assert collect(callbacks + (CallbackItem("bad", None, "Hurtbox"),), 3)[0] == "MissingBinding"
assert collect(callbacks + (CallbackItem("stale", Key(1, 99), "Hurtbox"),), 3)[0] == "StaleBinding"

# Order trace printed in the article.
trace = [set()]
for n in range(1, len(callbacks) + 1):
    trace.append(collect(callbacks[:n], 2)[1])
assert trace == [set(), set(), {F}, {F}, {E, F}, {E, F}, {E, F}]

# Intentionally faulty policy: mark owner seen before checking role.
def wrong_first_shape(items):
    seen, accepted = set(), set()
    for item in items:
        if item.owner in seen:
            continue
        seen.add(item.owner)
        if item.role == "Hurtbox" and not item.sensor:
            if item.owner in (E, F):
                accepted.add(item.owner)
    return accepted
assert wrong_first_shape(callbacks) == {F}

# AABB teaching sequence with given geometry decisions; no geometry API.
aabb_items = ((E, False), (E, True))
seen, wrong, correct = set(), set(), set()
for key, passes_geometry in aabb_items:
    if key not in seen:
        seen.add(key)
        if passes_geometry:
            wrong.add(key)
    if passes_geometry:
        correct.add(key)
assert wrong == set() and correct == {E}

# Bidirectional filter arithmetic and group-priority contrast only.
def query_pass(sc, sm, qc, qm):
    return (sc & qm) != 0 and (sm & qc) != 0

def shape_pair(ac, am, ag, bc, bm, bg):
    if ag == bg and ag != 0:
        return ag > 0
    return (ac & bm) != 0 and (bc & am) != 0

assert query_pass(0x02, 0x10, 0x10, 0x02)
assert not query_pass(0x02, 0, 0x10, 0x02)
assert not query_pass(0x02, 0x10, 0x10, 0)
assert not shape_pair(0x1, 0x2, -7, 0x2, 0x1, -7)
assert query_pass(0x2, 0x1, 0x1, 0x2)
assert shape_pair(0x1, 0, +7, 0x2, 0, +7)
assert not query_pass(0x2, 0, 0x1, 0)

# Exact known geometric relationships are expressed as scalar arithmetic.
local = [(-2, -.5), (2, -.5), (2, .5), (-2, .5)]
c, s = cos(pi/2), sin(pi/2)
rotated = [(c*x-s*y, s*x+c*y) for x, y in local]
expected_relative = [(.5, -2), (.5, 2), (-.5, 2), (-.5, -2)]
expected_world = [(10.5, 3), (10.5, 7), (9.5, 7), (9.5, 3)]
for p, q, w in zip(rotated, expected_relative, expected_world):
    assert all(isclose(a, b, abs_tol=1e-12) for a, b in zip(p, q))
    assert all(isclose(a, b, abs_tol=1e-12) for a, b in zip((p[0]+10, p[1]+5), w))
triangle_nearest = (2, 2)
box_nearest = (3, 3)
separation = sqrt(sum((a-b)**2 for a, b in zip(triangle_nearest, box_nearest)))
assert isclose(separation, sqrt(2))
assert triangle_nearest[0] + triangle_nearest[1] == 4
assert box_nearest[0] + box_nearest[1] == 6
assert isclose(.1*.005*1, .0005)

# Old application key cannot resolve to a new entity in reused slot.
new_E = Key(E.slot, E.generation + 1)
reused_registry = {new_E: Entity(new_E, "enemy")}
assert reused_registry.get(E) is None
assert reused_registry.get(new_E).key == new_E

print(json.dumps({
    "kind": "Original application-set model and scalar arithmetic; not Box2D execution",
    "callback_orders_with_success": success_orders,
    "callback_orders_with_capacity_failure": failure_orders,
    "expected_success_keys": [[E.slot, E.generation], [F.slot, F.generation]],
    "additional_checks": [
        "third distinct key fails whole attempt; same-input larger-capacity retry succeeds",
        "missing and stale bindings fail whole attempt",
        "article callback-order trace",
        "wrong early role dedup and wrong early AABB dedup counterexamples",
        "both query filter directions and same-group -7/+7 contrast",
        "rotated box coordinates and origin translation",
        "triangle separation and source-threshold arithmetic",
        "generation-key reuse protection",
    ],
    "limits": [
        "Callback input acceptance is stipulated; no Box2D query is executed",
        "No GJK, tree traversal, native floating-point boundary, physics, performance, or concurrency validation",
        "Set model verifies the stated application policy, not every possible implementation",
    ],
}, ensure_ascii=False, indent=2))
