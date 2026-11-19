from fractions import Fraction as F
from collections import Counter
import json

HORIZON = 7
old = [(4, "unlock"), (6, "unlock"), (7, "unlock"), (7, "censor")]
fresh = old + [(2,"censor")]*4
terminal = [(3,"blocked")]*2 + [(4,"unlock")]*2 + [(6,"unlock")]*2 + [(7,"unlock"),(7,"censor")]
# Observations start at the moment the player first meets eligibility, not at login.
# A "blocked" event permanently precludes this particular unlock within its definition.
# Events at exactly the censor boundary are observed and applied before removing censors.

def report(rows):
    assert rows and all(0 <= t <= HORIZON for t,_ in rows)
    size = len(rows)
    n = size
    km = survival = F(1)
    cumulative = F(0)
    table = []
    for t in sorted({t for t,_ in rows}):
        counts = Counter(kind for day,kind in rows if t==day)
        a,b,c = (counts[k] for k in ("unlock","blocked","censor"))
        cumulative += survival * F(a,n)
        survival *= 1-F(a+b,n)
        km *= 1-F(a,n)
        table.append([t,n,a,b,c,str(1-km),str(cumulative)])
        n -= a+b+c
    got = sum(k=="unlock" for _,k in rows)
    earlier_end = sum(k=="censor" and t<HORIZON for t,k in rows)
    return {"known_unlock_share":str(F(got,size)),
            "fixed_cohort_lower_upper": [str(F(got,size)),str(F(got+earlier_end,size))],
            "one_minus_km":str(1-km),
            "cumulative_incidence":str(cumulative),
            "table_day_risk_unlock_block_censor_one_minus_km_cif":table}

out = {name:report(rows) for name,rows in [("fully_followed_cohort",old),
                                          ("same_released_results_plus_late_entrants",fresh),
                                          ("permanent_block_is_observed",terminal)]}
assert out["fully_followed_cohort"]["known_unlock_share"] == "3/4"
assert out["same_released_results_plus_late_entrants"]["known_unlock_share"] == "3/8"
assert out["same_released_results_plus_late_entrants"]["one_minus_km"] == "3/4"
assert out["same_released_results_plus_late_entrants"]["fixed_cohort_lower_upper"] == ["3/8","7/8"]
assert out["permanent_block_is_observed"]["one_minus_km"] == "5/6"
assert out["permanent_block_is_observed"]["cumulative_incidence"] == "5/8"
print(json.dumps(out,indent=2))
