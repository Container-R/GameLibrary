"""Finite fixture: action choice by player, outcomes not chosen by player."""
from fractions import Fraction as F

GOAL = 'exit'

def reachable_somehow(g):
    seen = {GOAL}
    while True:
        add = {s for s, actions in g.items()
               if any(t in seen for outcomes in actions.values() for t in outcomes)}
        if add <= seen:
            return seen
        seen |= add

def ranks(g):
    rank = {GOAL: 0}
    while True:
        add = {s for s, actions in g.items() if s not in rank
               and any(outcomes and set(outcomes) <= rank.keys()
                       for outcomes in actions.values())}
        if not add:
            return rank
        rank.update(dict.fromkeys(add, 1+max(rank.values())))

def probabilities(g, turns):
    prev = {s: F(s == GOAL) for s in g}
    for _ in range(turns):
        prev = {s: F(1) if s == GOAL else
                max((sum((p * prev[t] for t,p in outcome.items()), F(0))
                     for outcome in actions.values()), default=F(0))
                for s, actions in g.items()}
    return prev

def scenario(retry=False, safe=False):
    g = {'hall': {'draw': {GOAL: F(1,2), ('hall' if retry else 'cell'): F(1,2)}},
         'cell': {}, GOAL: {}}
    if safe:
        g['hall']['detour'] = {'bridge': F(1)}
        g['bridge'] = {'cross': {GOAL: F(1)}}
    return g

for title, g, expected in [
    ('trap', scenario(), (True, None, F(1,2), F(1,2), F(1,2))),
    ('retry', scenario(retry=True), (True, None, F(1,2), F(3,4), F(7,8))),
    ('detour', scenario(retry=True, safe=True), (True, 2, F(1,2), F(1), F(1))),
]:
    got = ('hall' in reachable_somehow(g), ranks(g).get('hall'),
           *(probabilities(g,n)['hall'] for n in (1,2,3)))
    assert got == expected
    print(title, 'possible=',got[0], 'rank=',got[1], 'P(1,2,3)=',
          ','.join(str(p) for p in got[2:]))

# A hidden initial commitment removes independence. After the first failure
# the state is known stuck in a loop rather than drawing from the hall again.
g = {'hall': {'draw': {GOAL: F(1,2), 'known_bad': F(1,2)}},
     'known_bad': {'retry': {'known_bad': F(1)}}, GOAL: {}}
assert 'hall' in reachable_somehow(g) and 'hall' not in ranks(g)
assert all(probabilities(g,n)['hall'] == F(1,2) for n in (1,2,3,10))
print('fixed-seed bad branch P(1,2,3,10)=1/2,1/2,1/2,1/2')
