from fractions import Fraction as F
import json

p=F(1,5)
q=1-p
guarantee=10

def still_waiting(attempts, cap=None):
    return F(0) if cap is not None and attempts >= cap else q**attempts

def percentile(target, cap=None):
    return next(i for i in range(1,101) if 1-still_waiting(i,cap)>=target)

def metrics(cap=None):
    # E[T] = sum P(T>n), n=0,... ; finite for cap, geometric otherwise.
    expected=sum(still_waiting(i,cap) for i in range(cap)) if cap else 1/p
    return {"mean_attempts":str(expected),
            "median":percentile(F(1,2),cap),
            "p90":percentile(F(9,10),cap),
            "p95":percentile(F(95,100),cap),
            "share_waiting_after_10":str(still_waiting(10,cap))}
rows={"independent_rolls_only":metrics(),"force_at_attempt_10":metrics(guarantee)}
assert rows["independent_rolls_only"]["p95"]==14
assert rows["force_at_attempt_10"]["p95"]==10
assert rows["independent_rolls_only"]["median"]==rows["force_at_attempt_10"]["median"]==4
# Same expected value as the uncapped p=.2 example but no random waits.
rows["fixed_earned_target"]={"mean_attempts":"5","median":5,"p90":5,"p95":5,"share_waiting_after_10":"0"}
print(json.dumps(rows,indent=2))
