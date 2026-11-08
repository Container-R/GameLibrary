"""Original synchronous teaching fixture; standard library only.
Run: python3 behavior_fixture.py > results.json
No engine, movement, production safety or gameplay-benefit claim.
"""
import json

A, B = ('mine', 'A'), ('mine', 'B')
KEYS = (A, B)
ACTOR = 'actor'


def label(key):
    return None if key is None else ':'.join(key)


def choose(scores, current, h=50, scope='candidate'):
    def bonus(key):
        return h if (key == current if scope == 'candidate' else
                     current is not None and key[0] == current[0]) else 0
    return min(scores, key=lambda k: (-(scores[k] + bonus(k)),
                                     k != current, k)) if scores else None


class Fixture:
    def __init__(self):
        self.available = {k: True for k in KEYS}
        self.owner = {k: None for k in KEYS}
        self.current = None
        self.run_id = 0
        self.work = 0
        self.limit = None
        self.counts = dict(start_attempt=0, start_success=0, stop=0, update=0)
        self.calls = []

    def eligibility(self, key, continuing=False):
        if not self.available[key]:
            return False, 'unavailable'
        if continuing:
            ok = self.owner[key] == ACTOR
            return ok, 'owned_by_self' if ok else 'not_owned_by_self'
        ok = self.owner[key] is None
        return ok, 'free' if ok else 'occupied'

    def start(self, key, fail=False, limit=None):
        assert self.current is None
        assert not any(self.owner.values())
        ok, reason = self.eligibility(key)
        self.counts['start_attempt'] += 1
        if not ok or fail:
            self.calls.append(dict(op='start_failed', key=label(key),
                                   reason=reason if not ok else 'injected_failure'))
            return False
        self.owner[key] = ACTOR
        self.run_id += 1
        self.work, self.limit = 0, limit
        self.counts['start_success'] += 1
        self.calls.append(dict(op='start', key=label(key), run_id=self.run_id))
        return True

    def stop(self, reason):
        assert self.current is not None
        assert self.owner[self.current] == ACTOR
        self.owner[self.current] = None
        self.counts['stop'] += 1
        self.calls.append(dict(op='stop', key=label(self.current),
                               run_id=self.run_id, reason=reason, work=self.work))
        self.current = None

    def update(self):
        assert self.current is not None
        assert self.eligibility(self.current, continuing=True)[0]
        self.work += 1
        self.counts['update'] += 1
        self.calls.append(dict(op='update', key=label(self.current),
                               run_id=self.run_id, work=self.work))

    def tick(self, t, scores=None, fail=False, limit=None):
        assert (scores is not None) == (t % 100 == 0)
        self.calls = []
        before = self.current
        guard = None
        if self.current is not None:
            ok, reason = self.eligibility(self.current, continuing=True)
            complete = self.limit is not None and self.work >= self.limit
            guard = dict(key=label(self.current), continue_ok=ok,
                         reason=reason, completed=complete, work=self.work)
            if not ok or complete:
                self.stop('invalid' if not ok else 'completed')
        scoring = None
        decision = 'wait_for_ordinary_scoring'
        if scores is not None:
            snapshot, eligible = [], {}
            for key in KEYS:
                continuing = key == self.current
                ok, reason = self.eligibility(key, continuing)
                snapshot.append(dict(key=label(key), mode='continue' if continuing else 'start',
                                     eligible=ok, reason=reason, base=scores[key],
                                     bonus=50 if continuing and ok else 0))
                if ok:
                    eligible[key] = scores[key]
            chosen = choose(eligible, self.current)
            scoring = dict(time_ms=t, candidates=snapshot, selected=label(chosen))
            if chosen == self.current:
                decision = 'empty' if chosen is None else 'retain'
            else:
                decision = 'switch' if self.current is not None else 'start_from_none'
                if self.current is not None:
                    self.stop('better_candidate')
                if chosen is not None:
                    if self.start(chosen, fail=fail, limit=limit):
                        self.current = chosen  # Commit only after successful start.
                    else:
                        decision = 'start_failed_remain_none'
        if self.current is not None:
            self.update()
        occupied = [k for k in KEYS if self.owner[k] is not None]
        assert occupied == ([] if self.current is None else [self.current])
        return dict(time_ms=t, previous=label(before), guard=guard, scoring=scoring,
                    decision=decision, calls=self.calls.copy(), current=label(self.current),
                    owners={label(k): self.owner[k] for k in KEYS},
                    active_work=self.work if self.current is not None else None,
                    counts=self.counts.copy())


def main():
    f, trace = Fixture(), []
    events = [dict(time_ms=241, A=False, B=False),
              dict(time_ms=351, A=True, B=False),
              dict(time_ms=451, A=False, B=True)]
    frames = {0: {A:600, B:590}, 100: {A:600, B:620},
              200: {A:600, B:700}, 300: {A:600, B:700},
              400: {A:0, B:700}, 500: {A:0, B:900}, 600: {A:0, B:900}}
    for t in range(0, 631, 10):
        # Events are world facts visible immediately at their declared timestamp;
        # this loop samples their latest value only at the scheduled tick.
        for event in events:
            if event['time_ms'] <= t:
                f.available = {A:event['A'], B:event['B']}
        trace.append(f.tick(t, frames.get(t), fail=t == 500,
                            limit=3 if t in (400, 600) else None))
    rows = {r['time_ms']: r for r in trace}
    expected = [label(A) if t < 200 else label(B) if t < 250 else
                label(A) if 400 <= t < 430 else label(B) if 600 <= t < 630 else None
                for t in range(0, 631, 10)]
    assert [r['current'] for r in trace] == expected
    assert f.counts == dict(start_attempt=5, start_success=4, stop=4, update=31)
    assert [c['op'] for c in rows[200]['calls']] == ['stop','start','update']
    assert rows[250]['calls'][0]['reason'] == 'invalid'
    assert rows[250]['scoring'] is None
    assert rows[300]['decision'] == 'empty'
    assert rows[400]['scoring']['candidates'][0]['base'] == 0
    assert rows[430]['calls'][0]['reason'] == 'completed'
    assert rows[500]['calls'] == [dict(op='start_failed',key=label(B),reason='injected_failure')]
    assert rows[630]['calls'][0]['reason'] == 'completed'
    assert rows[100]['scoring']['candidates'][0]['mode'] == 'continue'
    assert rows[100]['scoring']['candidates'][0]['eligible']

    g = Fixture()
    first = g.tick(0, {A:600, B:590})
    start_ok, start_reason = g.eligibility(A)
    continue_ok, continue_reason = g.eligibility(A, continuing=True)
    assert not start_ok and continue_ok
    failure = g.tick(100, {A:600, B:900}, fail=True)
    assert [c['op'] for c in failure['calls']] == ['stop', 'start_failed']
    assert failure['current'] is None and not any(g.owner.values())
    assert g.counts == dict(start_attempt=2, start_success=1, stop=1, update=1)
    assert choose({A:600, B:650}, A) == A
    assert choose({B:500, A:500}, None) == A

    def replay(frames, scope):
        current, out = A, []
        for i, scores in enumerate(frames):
            chosen = choose(scores, current, scope=scope)
            out.append(dict(time_ms=i*100, previous=label(current),
                            scores={label(k):v for k,v in scores.items()},
                            selected=label(chosen), transition=chosen != current))
            current = chosen
        return out
    small = [{A:600,B:610}, {A:610,B:600}]*3
    candidate = replay(small, 'candidate')
    type_bonus = replay(small, 'type')
    large = replay([{A:500,B:560}, {A:560,B:500}]*3, 'candidate')
    assert sum(r['transition'] for r in candidate) == 0
    assert sum(r['transition'] for r in type_bonus) == 6
    assert sum(r['transition'] for r in large) == 6
    result = dict(contract='original synchronous fixture, no engine', margin=50,
                  score_unit='integer milli-units', world_events=events, trace=trace,
                  eligibility_difference=dict(start_ok=start_ok, start_reason=start_reason,
                                              continue_ok=continue_ok, continue_reason=continue_reason),
                  failed_switch=[first,failure],
                  tie_checks=dict(incumbent_equal=label(A), no_incumbent_stable_key=label(A)),
                  counterexamples=dict(candidate_bonus=candidate, type_bonus=type_bonus,
                                       large_reversal=large),
                  all_protocol_assertions_passed=True)
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
