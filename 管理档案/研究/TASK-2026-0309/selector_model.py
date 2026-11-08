"""Original deterministic teaching model, not a game or production AI library.

Run: python3 selector_model.py > results.json
Scores use integer milli-units. The source papers do not supply this algorithm.
"""
import json
import platform


def label(key):
    return None if key is None else ':'.join(key)


def select(scores, current, margin=50, bonus_scope='candidate'):
    """All supplied candidates are eligible; 0 is an ordinary valid score.

    Rank by adjusted score, then exact incumbent, then stable key order.
    candidate bonus is the reference design; type bonus is a counterexample.
    """
    if not scores:
        return None
    adjusted = {}
    for key, value in scores.items():
        has_bonus = (key == current) if bonus_scope == 'candidate' else (
            current is not None and key[0] == current[0])
        adjusted[key] = value + (margin if has_bonus else 0)
    return min(scores, key=lambda key: (-adjusted[key], key != current, key))


def replay(frames, margin=50, scope='candidate', initial=None):
    current = initial
    rows = []
    for i, scores in enumerate(frames):
        chosen = select(scores, current, margin, scope)
        rows.append({'step': i, 'scores': {label(k): v for k, v in scores.items()},
                     'previous': label(current), 'selected': label(chosen),
                     'transition': chosen != current})
        current = chosen
    return rows


def main():
    a, b = ('mine', 'ore-A'), ('mine', 'ore-B')
    small = [{a:600,b:610}, {a:610,b:600}]*3
    reference = replay(small, initial=a)
    wrong_scope = replay(small, initial=a, scope='type')
    assert all(r['selected'] == label(a) for r in reference)
    assert sum(r['transition'] for r in wrong_scope) == 6

    eligibility = replay([{a:400,b:900},{a:100},{}, {b:0}], initial=a)
    assert [r['selected'] for r in eligibility] == [label(b), label(a), None, label(b)]
    # The removed incumbent is not scored, even when it had a recent bonus.
    assert select({b:0}, a) == b

    diffs = list(range(-60,61,10)) + list(range(50,-61,-10))
    sweep = replay([{a:500,b:500+d} for d in diffs], initial=a)
    switches = [(diffs[i],r['selected']) for i,r in enumerate(sweep) if r['transition']]
    assert switches == [(60,label(b)),(-60,label(a))]
    for i,r in enumerate(sweep):
        r['difference_B_minus_A'] = diffs[i]

    fast = replay([{a:500,b:560},{a:560,b:500}]*3, initial=a)
    assert sum(r['transition'] for r in fast) == 6

    base = {a:500,b:530}
    scaled = {k:v*10 for k,v in base.items()}
    scale = {'original_h50':label(select(base,a,50)),
             'scores_x10_h50':label(select(scaled,a,50)),
             'scores_x10_h500':label(select(scaled,a,500))}
    assert list(scale.values()) == [label(a),label(b),label(a)]

    schedule = []
    slow = fast_guard = a
    for t in range(0,121,10):
        eligible = {a:600,b:590} if t < 40 else {b:590}
        ordinary_due = t % 100 == 0
        if ordinary_due:
            slow = select(eligible,slow)
        # This branch synchronously drops invalid intent before considering a
        # replacement. It does NOT implement asynchronous stop or rollback.
        invalid = fast_guard is not None and fast_guard not in eligible
        if invalid:
            fast_guard = None
        if ordinary_due or invalid:
            fast_guard = select(eligible,fast_guard)
        schedule.append({'time_ms':t,'eligible':[label(k) for k in eligible],
                         'ordinary_due':ordinary_due,
                         'slow_check':label(slow), 'per_tick_guard':label(fast_guard)})
    assert next(r['time_ms'] for r in schedule if r['slow_check']==label(b)) == 100
    assert next(r['time_ms'] for r in schedule if r['per_tick_guard']==label(b)) == 40

    print(json.dumps({'python':platform.python_version(),
        'model_kind':'original synchronous selector replay; no engine or game simulation',
        'score_units':'integer milli-units','margin':50,
        'same_type_candidate_bonus':reference, 'same_type_type_bonus':wrong_scope,
        'eligibility_and_empty':eligibility, 'threshold_sweep':sweep,
        'large_reversal_each_step':fast, 'scale_dependence':scale,
        'eligibility_schedule':schedule, 'all_protocol_assertions_passed':True},
        ensure_ascii=False,indent=2))


if __name__ == '__main__':
    main()
