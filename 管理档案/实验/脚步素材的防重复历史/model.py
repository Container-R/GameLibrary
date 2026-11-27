"""Controlled draws; this is not Wwise behavior or a frequency benchmark."""
from collections import Counter

def select(events, global_history):
    previous={}
    picked=[]
    for actor, ordered in events:
        scope='all' if global_history else actor
        choice=next((v for v in ordered if v!=previous.get(scope)), None)
        picked.append((actor,choice))
        if choice is not None:
            previous[scope]=choice
    return picked

events=[('A',[1,2]),('B',[2,1]),('A',[1,2])]
g=select(events,True)
l=select(events,False)
assert g == [('A',1),('B',2),('A',1)]
assert l == [('A',1),('B',2),('A',2)]
print('global:',g)
print('per emitter:',l)

# With exactly two clips and strict no adjacent repeats, only one choice
# is eligible after the initial event, regardless of source weights.
two=select([('A',['heavy','light'])]*100,False)
assert Counter(c for _,c in two)=={'heavy':50,'light':50}
print('two strict variants:',dict(Counter(c for _,c in two)))
