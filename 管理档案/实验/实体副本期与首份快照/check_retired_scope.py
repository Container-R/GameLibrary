import itertools
import json

# Fixed session and birth generation; messages are local records, not packets.
OLD = ("full", 8, 10, None, {"lift_height": 20, "door": "closed"})
HIDE8 = ("hide", 8, None, None, {})
FULL9 = ("full", 9, 19, None, {"lift_height": 72, "door": "open"})
STEP9 = ("delta", 9, 20, 19, {"lift_height": 75})
HIDE9 = ("hide", 9, None, None, {})


def receive(receiver, msg, retain_retirement=True):
    retired, view = receiver
    typ, scope, tick, base, fields = msg
    active = view[0] if view else -1
    if typ == "hide":
        retired = max(retired, scope) if retain_retirement else -1
        # A confirmed cut for N retires all older episodes of this entity too.
        return (retired, None if active <= scope else view), "retired"
    if scope <= retired or scope < active:
        return receiver, "stale scope"
    if typ == "delta" and (active != scope or view[1] != base):
        return receiver, "need baseline"
    if active == scope and tick <= view[1]:
        return receiver, "duplicate or old sample"
    new_fields = view[2] | fields if typ == "delta" else fields.copy()
    return (retired, (scope, tick, new_fields)), "applied"


def play(messages, retain=True):
    receiver = (-1, None)
    for msg in messages:
        receiver, _ = receive(receiver, msg, retain)
    return receiver


late_old = (OLD, HIDE8, OLD)
late_same = (OLD, HIDE8, FULL9, HIDE9, FULL9)
late_hide = (OLD, FULL9, HIDE8, STEP9, FULL9)
assert play(late_old) == (8, None)
assert play(late_same) == (9, None)
assert play(late_old, False)[1] == (8, 10, OLD[4])
assert play(late_same, False)[1] == (9, 19, FULL9[4])
assert play(late_hide) == (8, (9, 20, {"lift_height": 75, "door": "open"}))
receiver, status = receive(play((OLD, HIDE8)), STEP9)
assert status == "need baseline" and receiver == (8, None)
# No packet drops in these permutations. Each includes Hide(9);
# subsequent steps may not revive episode 8 or 9 under the specified local rule.
orders = list(itertools.permutations((OLD, HIDE8, FULL9, STEP9, HIDE9)))
assert all(play(order) == (9, None) for order in orders)
print(json.dumps({
    "late_old_full_without_retirement": play(late_old, False)[1],
    "late_old_full_with_retirement": play(late_old)[1],
    "same_scope_full_retry_without_retirement": play(late_same, False)[1],
    "same_scope_full_retry_with_retirement": play(late_same)[1],
    "late_older_hide_and_duplicate_full": play(late_hide)[1],
    "delta_before_initial_state": status,
    "no_loss_delivery_orders_ending_with_retired_view": len(orders)
}, indent=2))
