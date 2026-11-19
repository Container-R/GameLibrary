"""Original finite story model. Does not import/compile/run ink."""
from collections import deque
from dataclasses import dataclass, asdict
import json
import platform

@dataclass(frozen=True)
class State:
    scene: str = 'prepare'
    trust: int = 0
    badge: bool = False

def choices(s, version):
    if s.scene == 'prepare':
        return {
            'help': State('audience', 2, False),
            'credential': State('audience', 1, True),
            'rush': State('audience', 0, False),
        }
    if s.scene != 'audience':
        return {}
    guard = {
        'old': s.trust >= 2 or s.badge,
        'approved': s.trust >= 2,
        'bad_threshold': s.trust > 2,
        'bad_open': s.trust >= 0,
    }[version]
    out = {'leave': State('left', s.trust, s.badge)}
    if guard:
        out['parley'] = State('agreement', s.trust, s.badge)
    return out

def explore(version, limit=100):
    root = State()
    paths = {root: []}
    todo = deque([root])
    while todo:
        s = todo.popleft()
        for action, target in choices(s, version).items():
            if target not in paths:
                if len(paths) >= limit:
                    return paths, False
                paths[target] = paths[s] + [action]
                todo.append(target)
    return paths, True

def approved_delta(s, removed, added):
    # Exact author's change contract. Not a blanket permit to remove parley.
    return (s == State('audience', 1, True)
            and removed == ['parley'] and added == [])

def audit(version):
    old, old_complete = explore('old')
    new, new_complete = explore(version)
    diffs = []
    for s in sorted(old.keys() & new.keys(), key=lambda s:(s.scene,s.trust,s.badge)):
        before, after = set(choices(s, 'old')), set(choices(s, version))
        removed, added = sorted(before-after), sorted(after-before)
        if removed or added:
            diffs.append({'state': asdict(s), 'old_prefix': old[s], 'new_prefix': new[s],
                          'removed': removed, 'added': added,
                          'approved': approved_delta(s, removed, added)})
    all_finish = all(s.scene in ('left', 'agreement') or bool(choices(s, version)) for s in new)
    # For this acyclic two-action model each nonterminal goes to a terminal.
    coverage = [{'state':asdict(s),'prefix':p} for s,p in new.items() if s not in old]
    lost = [{'state':asdict(s),'prefix':p} for s,p in old.items() if s not in new]
    expected = {
        State('audience',2,False): {'leave','parley'},
        State('audience',1,True): {'leave'},
        State('audience',0,False): {'leave'},
    }
    obligations = all(s in new and set(choices(s,version)) == wanted
                      for s,wanted in expected.items())
    expected_lost = {State('agreement',1,True)}
    graph_delta_ok = not (new.keys()-old.keys()) and (old.keys()-new.keys()) == expected_lost
    return {'version':version,'complete':old_complete and new_complete,
            'old_states':len(old), 'new_states':len(new),
            'all_reachable_states_can_finish':all_finish,
            'differences':diffs,'new_only_states':coverage,'old_only_states':lost,
            'obligations_met':obligations, 'graph_delta_approved':graph_delta_ok,
            'accepted':old_complete and new_complete and obligations and graph_delta_ok and all(d['approved'] for d in diffs)}

if __name__ == '__main__':
    result = [audit(v) for v in ('approved','bad_threshold','bad_open')]
    assert [r['accepted'] for r in result] == [True,False,False]
    assert not audit('old')['accepted']  # Doing nothing also violates the required edit.
    assert all(r['all_reachable_states_can_finish'] for r in result)
    assert len(result[0]['differences']) == 1
    assert len(result[1]['differences']) == 2
    assert result[1]['differences'][1]['new_prefix'] == ['help']
    assert result[2]['differences'][0]['added'] == ['parley']
    assert result[2]['differences'][0]['new_prefix'] == ['rush']
    assert not explore('old',limit=2)[1]
    reachable,_=explore('old')
    assert State('audience',2,True) not in reachable
    print(json.dumps({'python':platform.python_version(), 'kind':'synthetic finite model, not ink runtime',
                      'cases':result,'budget_limit_2':'undetermined',
                      'unreachable_combination':asdict(State('audience',2,True))},ensure_ascii=False,indent=2))
