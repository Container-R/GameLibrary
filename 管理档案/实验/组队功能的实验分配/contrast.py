from fractions import Fraction as F
import itertools, json
assignments = tuple(itertools.product((0, 1), repeat=2))
scores = {(0, 0):30, (0, 1):34, (1, 0):36, (1, 1):45}
def response(z):
    a,b=z
    return (scores[a,b], scores[b,a])
designs = {
    "independent_50_percent": (F(1,4),)*4,
    "exactly_one_per_team": (F(0),F(1,2),F(1,2),F(0)),
    "entire_team_randomized": (F(1,2),F(0),F(0),F(1,2))
}
out={}
for k,w in designs.items():
    by_own={}
    for arm in (0,1):
        items=[(v,p) for z,p in zip(assignments,w) for a,v in zip(z,response(z)) if a==arm]
        by_own[arm]=sum(v*p for v,p in items)/sum(p for _,p in items)
    out[k]={"control_mean":str(by_own[0]),"treated_mean":str(by_own[1]),"difference":str(by_own[1]-by_own[0])}
assert [x["difference"] for x in out.values()]==["17/2","2","15"]
out["same_partner_comparisons"]={"own_change_partner_off":scores[1,0]-scores[0,0],"own_change_partner_on":scores[1,1]-scores[0,1],"partner_change_own_off":scores[0,1]-scores[0,0]}
assert sorted(out["same_partner_comparisons"].values())==[4,6,11]
print(json.dumps(out,indent=2,ensure_ascii=False))
