"""A synthetic counterexample about whom a randomized tutorial trial compares."""
from fractions import Fraction
import json

# Each row is one independent player. Deliberately stratified and deterministic.
def base(arm):
    rows=[]
    for i in range(1000):
        eligible=i>=900
        j=i-900 if eligible else i
        before_ui={"variant":arm,"first_common_checkpoint":eligible}
        shown=arm=="B" and eligible and j<80
        # A: 20/100 stuck complete. The UI helps 25 of 80 and never hurts.
        passed=(j<810) if not eligible else (j<20 or (shown and 20<=j<45))
        rows.append({**before_ui,"shown":shown,"complete":passed})
    return rows

def compare(a,b,sel_a=lambda row:True,sel_b=lambda row:True):
    def summarize(rows,keep):
        rows=[r for r in rows if keep(r)]
        return len(rows),sum(r["complete"] for r in rows)
    n0,p0=summarize(a,sel_a);n1,p1=summarize(b,sel_b)
    return {"A":[p0,n0],"B":[p1,n1],"B_minus_A_pp":float(100*(Fraction(p1,n1)-Fraction(p0,n0)))}

trigger=lambda r:r["first_common_checkpoint"]
show=lambda r:r["shown"]
other=lambda r:not trigger(r)
a,b=base("A"),base("B")
r={
 "full_assignment":compare(a,b),
 "same_checkpoint_both_arms":compare(a,b,trigger,trigger),
 "not_at_checkpoint_both_arms":compare(a,b,other,other),
 "wrong_shown_b_versus_all_a":compare(a,b,sel_b=show),
 "wrong_shown_b_versus_eligible_a":compare(a,b,trigger,show)
}
assert [row["B_minus_A_pp"] for row in r.values()]==[2.5,25.0,0.0,-26.75,36.25]

# Another experiment: no change in individual completion. Both groups have 50% 
# easy (complete) and 50% hard (do not). An earlier variant change affects who
# reaches the logged checkpoint: equal counts, different people.
def late(arm):
    rows=[]
    for i in range(200):
        easy=i<100
        rank=i%100
        selected=rank<(80 if easy==(arm=="B") else 20)
        rows.append({"variant":arm,"late_checkpoint":selected,"complete":easy})
    return rows
c,d=late("A"),late("B")
after=lambda x:x["late_checkpoint"]
r["equal_late_trigger_counts_but_selected_types_differ"]={
 "overall":compare(c,d),
 "triggered":compare(c,d,after,after),
 "complement":compare(c,d,lambda x:not after(x),lambda x:not after(x))
}
s=r["equal_late_trigger_counts_but_selected_types_differ"]
assert [o["B_minus_A_pp"] for o in s.values()]==[0.0,60.0,-60.0]
print(json.dumps(r,ensure_ascii=False,indent=2))
