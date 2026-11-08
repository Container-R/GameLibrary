"""Original finite model validation only. Not a game test or an ACTS run."""
from itertools import product, combinations
import json
names = ('P','V','U','T','C')
domains = (('desktop','handheld'),('compact','wide'),(100,125,150),('normal','large'),(0,5))
def valid(r):
    p,v,u,t,c=r
    return (p!='handheld' or v=='compact') and (u!=150 or v=='wide')
rows=list(product(*domains)); legal=[r for r in rows if valid(r)]
pairs=list(combinations(range(5),2)); groups=pairs+[(2,3,4)]
def tuples(r, gs): return {(g,tuple(r[i] for i in g)) for g in gs}
def target(gs): return set().union(*(tuples(r,gs) for r in legal))
required=target(groups); remaining=set(required); selected=[]
while remaining:
    # Deterministic greedy; no minimality claim. Ties retain domain order.
    r=max(legal,key=lambda r:len(tuples(r,groups)&remaining))
    selected.append(r);remaining-=tuples(r,groups)
# Separate verifier enumerates value assignments and asks whether any complete legal row extends them.
verified={}
for g in groups:
    need={v for v in product(*(domains[i] for i in g)) if any(all(r[i]==x for i,x in zip(g,v)) for r in legal)}
    observed={tuple(r[i] for i in g) for r in selected}
    assert need==observed
    verified[''.join(names[i] for i in g)]={'required':sorted(need,key=str),'covered':len(observed)}
assert len(set(selected))==len(selected) and all(valid(r) for r in selected)
# Negative control: remove a row carrying a unique high-strength obligation.
victim=next(r for r in selected if target([(2,3,4)])-set().union(*(tuples(x,[(2,3,4)]) for x in selected if x!=r)))
reduced=[r for r in selected if r!=victim]
missing=required-set().union(*(tuples(r,groups) for r in reduced))
# Compare an independent greedy baseline pairwise suite.
left=target(pairs); base=[]
while left:
    r=max(legal,key=lambda r:len(tuples(r,pairs)&left));base.append(r);left-=tuples(r,pairs)
triple_missing=target([(2,3,4)])-set().union(*(tuples(r,[(2,3,4)]) for r in base))
def show(ts):return [{'columns': ''.join(names[i] for i in g),'values':v} for g,v in sorted(ts,key=str)]
out={'scope':'Finite model only; no game/ACTS execution','columns':names,'raw_rows':len(rows),'legal_rows':len(legal),'all_legal_rows':legal,'candidate_rows':selected,'candidate_count':len(selected),'pair_obligations':len(target(pairs)),'extra_UTC_obligations':12,'required_total':len(required),'verified_by_group':verified,'indirect_invalid_PU':['handheld',150],'pairwise_baseline_rows':base,'pairwise_baseline_missing_UTC':show(triple_missing),'negative_control_removed':victim,'negative_control_missing':show(missing)}
print(json.dumps(out,ensure_ascii=False,indent=2))
