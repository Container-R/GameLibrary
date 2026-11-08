"""Original finite teaching model. No engine, UI framework or wall-clock execution."""
import json
from itertools import permutations

# Two language requests; completions may happen in either legal order.
# S explicitly repairs layout/content from current desired locale in this model.
def run(order, guarded):
    desired = rendered = 'en'
    revision = 0
    requests = {}
    trace = []
    for event in order:
        if event.startswith('L'):
            revision += 1
            desired = {'L1':'ja', 'L2':'fr'}[event]
            requests[event] = (revision, desired)
        elif event.startswith('C'):
            rev, lang = requests['L'+event[1:]]
            if not guarded or rev == revision:
                rendered = lang
        elif event == 'S':
            rendered = desired
        trace.append(dict(event=event, desired=desired, rendered=rendered,
                          revision=revision, matches_current=desired==rendered))
    return trace

orders=[]
for p in permutations(['L1','L2','C1','C2']):
    if p.index('L1') < p.index('L2') and p.index('L1') < p.index('C1') and p.index('L2') < p.index('C2'):
        orders.append(p)
assert len(orders)==3
case=('L1','L2','C2','C1','S')
bad=run(case,False); good=run(case,True)
assert bad[2]['matches_current'] and not bad[3]['matches_current'] and bad[4]['matches_current']
assert good[3]['matches_current']
# Eventual success after C2 cannot establish that no later stale overwrite occurs.
print(json.dumps({'scope':'finite teaching model; not engine execution',
 'legal_orders':orders,'counterexample_without_revision_guard':bad,
 'same_trace_with_revision_guard':good},ensure_ascii=False,indent=2))
