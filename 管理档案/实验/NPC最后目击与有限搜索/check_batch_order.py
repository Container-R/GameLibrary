"""One toy-game visual sensor; reducers commit current and last positive separately."""
import json
from itertools import permutations

def choose(packet, active_generation, committed=None):
    watermark, current, last_seen = committed or (None, None, None)
    eligible = [p for p in packet if p[0] == active_generation
                and (watermark is None or p[1:3] > watermark)]
    by_key = {}
    for p in eligible:
        key = p[:3]
        if key in by_key and by_key[key] != p:
            return "conflicting_same_key"
        by_key[key] = p
    for k in sorted(by_key):
        p = by_key[k]
        watermark, current = p[1:3], p[3]
        if current:
            last_seen = p[1:3], p[4]
    return watermark, current, last_seen

# (target generation, capture tick, source sequence, current sight, sample point)
old_loss = (7, 14, 4, False, None)
fresh_see = (7, 14, 5, True, (8, 1))
old_generation_see = (6, 15, 99, True, (90, 70))
case = [old_loss, fresh_see, old_generation_see]

naive = {p[-1][3:] for p in permutations(case)}
stable = {choose(p, 7) for p in permutations(case)}
assert naive == {(False, None), (True, (8, 1)), (True, (90, 70))}
assert stable == {((14,5), True, ((14,5),(8,1)))}
assert choose([fresh_see, fresh_see], 7) == next(iter(stable))
assert choose([fresh_see, (7,14,5,False,None)], 7) == "conflicting_same_key"
assert choose([old_generation_see], 7) == (None, None, None)

earlier_positive = (7,20,1,True,(23,12))
later_loss = (7,20,2,False,None)
committed = choose([later_loss, earlier_positive],7)
assert committed == ((20,2),False,((20,1),(23,12)))
assert choose([fresh_see, old_loss],7,committed) == committed
print(json.dumps({
    "permutations": 6, "naive_possible_final_states": sorted(naive, key=repr),
    "committed_final_states": sorted(stable, key=repr),
    "positive_then_loss_same_tick": committed,
    "late_older_batch_does_not_revert": True, "same_record_again": "no change",
    "conflicting_same_key": "diagnostic; not treated as a fresh observation",
    "previous_generation_only": "ignored"}, indent=2))
