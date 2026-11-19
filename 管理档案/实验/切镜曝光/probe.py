"""Mechanism model with simplified stop-rate and exact linear checks."""
import json
from math import log2, isclose

GRAY = .18
old_l, new_l = .0225, 2.88
old_e, new_e = 8., 1/16

def advance(log_e, target, dt, speed):
    return log_e + max(-speed*dt, min(speed*dt, target-log_e))

def trace(seed, reject_wrong_shot):
    # Identical one-region linear scene after the cut. The metering results
    # from that view become valid two frames later, irrespective of framerate.
    bins = [("hall", 0, old_l), ("hall", 1, old_l), ("roof", 2, new_l),
            ("roof", 3, new_l), ("roof", 4, new_l), ("roof", 5, new_l)]
    applied = log2(new_e if seed else old_e)
    target = applied
    rows = []
    for shot, frame, l in bins:
        if not reject_wrong_shot or shot == "roof":
            target = log2(GRAY/l)
        applied = advance(applied, target, .1, 4.)
        effective = 2**applied
        rows.append({"frame":frame, "meter":shot, "current_shot":"roof",
                     "target_stops_gain":round(target,6),
                     "applied_stops_gain":round(applied,6),
                     "exposed_linear":round(new_l*effective,6)})
    return rows

ordinary = trace(False,True)
intentional = trace(True,True)
seed_only = trace(True,False)
assert ordinary[0]["exposed_linear"]==23.04
assert all(row["exposed_linear"]==.18 for row in intentional)
assert seed_only[0]["exposed_linear"]>.18

def storage(old_pre, final_gain):
    scene, highlight = new_l, 28.8
    values = [scene*old_pre,highlight*old_pre]
    return {"pre_scale":old_pre,"final_gain":final_gain,"stored_linear":values,
            "correct_exposed":[round(v*final_gain/old_pre,6) for v in values],
            "incorrect_double_scaled":[round(v*final_gain,6) for v in values]}

storage_old = storage(old_e,new_e)
storage_new = storage(new_e,new_e)
assert storage_old["correct_exposed"]==storage_new["correct_exposed"]==[.18,1.8]
assert all(isclose(b/a,8) for a,b in zip(storage_old["correct_exposed"],storage_old["incorrect_double_scaled"],strict=True))
print(json.dumps({"retained_old_history_guard_meter":ordinary,
                  "seeded_new_shot_guard_meter":intentional,
                  "seeded_new_shot_unfiltered_old_meter":seed_only,
                  "linear_scale_cases":[storage_old,storage_new]},indent=2))
