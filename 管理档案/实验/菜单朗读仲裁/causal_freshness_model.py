"""Original finite business-state model; no storage, network, UIA or audio calls."""
from dataclasses import asdict, dataclass
from pathlib import Path
import json


@dataclass
class Attempt:
    resource: str
    intent: int
    value: str
    order: int
    status: str = "pending"
    revision: int | None = None
    accepted_value: str | None = None


class Ledger:
    """Trusted full-replacement replies only; assertions are not a protocol validator.

    No historical revision/value index or version-epoch reset support.
    Validate authority replies upstream before using current() for narration.
    """
    def __init__(self):
        self.intents = {}
        self.attempts = {}
        self.confirmed = {}
        self.events = []

    def choose(self, resource, value):
        generation = self.intents.get(resource, (0, None))[0] + 1
        self.intents[resource] = (generation, value)
        self.events.append(["choose", resource, generation, value])

    def begin(self, op, resource):
        assert op not in self.attempts
        generation, value = self.intents[resource]
        self.attempts[op] = Attempt(resource, generation, value, len(self.attempts))
        self.events.append(["begin", op, resource, generation, value])

    def finish(self, op, status, revision=None, accepted_value=None):
        assert status in {"failed", "succeeded", "uncertain"}
        attempt = self.attempts[op]
        if attempt.status in {"failed", "succeeded"}:
            assert (attempt.status, attempt.revision, attempt.accepted_value) == (
                status, revision, accepted_value), "contradictory terminal reply"
            self.events.append(["duplicate", op, status, revision, accepted_value])
            return
        if status == "succeeded":
            assert type(revision) is int and revision >= 0
            assert isinstance(accepted_value, str), "success must report the authority's accepted value"
            prior = self.confirmed.get(attempt.resource)
            if prior and prior[0] == revision:
                assert prior[1] == accepted_value, "authority revision must identify one full value"
            if not prior or revision > prior[0]:
                self.confirmed[attempt.resource] = (revision, accepted_value, op)
        else:
            assert revision is None
            assert accepted_value is None
        attempt.status, attempt.revision, attempt.accepted_value = status, revision, accepted_value
        self.events.append(["reply", op, status, revision, accepted_value])

    def current(self, resource):
        intent, value = self.intents[resource]
        confirmed = self.confirmed.get(resource)
        unresolved = [op for op, a in self.attempts.items()
                      if a.resource == resource and a.status in {"pending", "uncertain"}]
        if unresolved:
            state = "pending_or_uncertain"
        elif confirmed and confirmed[1] == value:
            state = "confirmed_current"
        elif any(a.resource == resource and a.intent == intent and a.status == "failed"
                 for a in self.attempts.values()):
            state = "failed_current"
        elif confirmed:
            state = "confirmed_different"
        else:
            state = "unconfirmed_current"
        return {"resource": resource, "intent": intent, "desired": value,
                "last_confirmed": confirmed, "unresolved": unresolved, "state": state}

    def history(self, op):
        a = self.attempts[op]
        current = self.current(a.resource)
        relation = a.status
        if a.status == "failed":
            if current["intent"] > a.intent:
                relation = ("superseded_by_confirmed_intent" if current["state"] == "confirmed_current"
                            else "superseded_intent_unconfirmed")
            elif current["state"] == "confirmed_current" and any(
                b.resource == a.resource and b.intent == a.intent and b.order > a.order
                and b.status == "succeeded" for b in self.attempts.values()
            ):
                relation = "retry_succeeded"
            else:
                relation = "failure_still_relevant"
        return {"operation": op, **asdict(a), "relation": relation, "current": current}

    def snapshot(self):
        return {"inputs": self.events, "history": [self.history(op) for op in self.attempts]}


@dataclass(frozen=True)
class TimerRequest:
    page: str
    session: str


class Countdown:
    """Injected integer milliseconds in one clock domain, not an OS clock test."""
    def __init__(self, page, session, deadline_ms, revision=1):
        self.page, self.session = page, session
        self.deadline_ms, self.revision = deadline_ms, revision
        self.status = "running"
        self.remaining_ms = None
        self.events = [["create", page, session, deadline_ms, revision]]

    def update_deadline(self, session, deadline_ms, revision):
        accepted = session == self.session and revision > self.revision and self.status == "running"
        if accepted:
            self.deadline_ms, self.revision = deadline_ms, revision
        self.events.append(["deadline", session, deadline_ms, revision, accepted])

    def pause(self, now_ms):
        assert self.status == "running"
        self.remaining_ms = max(0, self.deadline_ms - now_ms)
        self.status = "paused"
        self.events.append(["pause", now_ms, self.remaining_ms])

    def resume(self, now_ms):
        assert self.status == "paused"
        self.deadline_ms = now_ms + self.remaining_ms
        self.status = "running"
        self.events.append(["resume", now_ms, self.deadline_ms])

    def cancel(self):
        self.status = "cancelled"
        self.events.append(["cancel"])

    def render(self, request, current_page, now_ms):
        if request.page != current_page or request.page != self.page:
            result = {"drop": "old_page"}
        elif request.session != self.session:
            result = {"drop": "old_session"}
        elif self.status != "running":
            result = {"drop": self.status}
        else:
            remaining = self.deadline_ms - now_ms
            result = ({"drop": "deadline_reached_without_start_confirmation"} if remaining <= 0
                      else {"seconds": (remaining + 999) // 1000, "revision": self.revision})
        self.events.append(["render", asdict(request), current_page, now_ms, result])
        return result


def run():
    cases = {}
    a = Ledger()
    a.choose("subtitle", "24")
    a.begin("r1", "subtitle")
    a.finish("r1", "failed")
    queued_resource = "subtitle"  # Queue a semantic read, not a frozen failure sentence.
    a.begin("r2", "subtitle")
    assert a.current("subtitle")["state"] == "pending_or_uncertain"
    a.finish("r2", "succeeded", 10, "24")
    assert a.history("r1")["status"] == "failed"
    assert a.history("r1")["relation"] == "retry_succeeded"
    assert a.current(queued_resource)["state"] == "confirmed_current"
    cases["same_intent_retry_and_late_render"] = a.snapshot()

    b = Ledger()
    b.choose("subtitle", "24")
    b.begin("r1", "subtitle")
    b.choose("subtitle", "28")
    b.begin("r2", "subtitle")
    b.finish("r2", "succeeded", 11, "28")
    assert b.current("subtitle")["state"] == "pending_or_uncertain"
    b.finish("r1", "failed")
    assert b.history("r1")["relation"] == "superseded_by_confirmed_intent"
    assert b.current("subtitle")["last_confirmed"][1] == "28"
    cases["new_intent_success_before_old_failure"] = b.snapshot()

    for newer_old_write in [False, True]:
        c = Ledger()
        c.choose("subtitle", "24")
        c.begin("r1", "subtitle")
        c.choose("subtitle", "28")
        c.begin("r2", "subtitle")
        c.finish("r2", "succeeded", 11, "28")
        c.finish("r1", "succeeded", 12 if newer_old_write else 10, "24")
        expected = "confirmed_different" if newer_old_write else "confirmed_current"
        assert c.current("subtitle")["state"] == expected
        cases["old_intent_newer_commit" if newer_old_write else "older_reply_does_not_regress"] = c.snapshot()

    d = Ledger()
    d.choose("subtitle", "24")
    d.begin("r1", "subtitle")
    d.finish("r1", "failed")
    d.choose("graphics", "high")
    d.begin("g1", "graphics")
    d.finish("g1", "succeeded", 99, "high")
    assert d.history("r1")["relation"] == "failure_still_relevant"
    d.begin("r2", "subtitle")
    d.finish("r2", "uncertain")
    assert d.current("subtitle")["state"] == "pending_or_uncertain"
    d.finish("r2", "succeeded", 1, "24")
    d.finish("r2", "succeeded", 1, "24")
    assert d.history("r1")["relation"] == "retry_succeeded"
    cases["independent_resource_and_timeout_reconciliation"] = d.snapshot()

    e = Ledger()
    e.choose("subtitle", "24")
    e.begin("r1", "subtitle")
    e.finish("r1", "failed")
    e.choose("subtitle", "28")
    e.begin("r2", "subtitle")
    assert e.history("r1")["relation"] == "superseded_intent_unconfirmed"
    assert e.current("subtitle")["state"] == "pending_or_uncertain"
    cases["new_intent_is_not_yet_saved"] = e.snapshot()

    f = Ledger()
    f.choose("subtitle", "28")
    f.begin("r1", "subtitle")
    f.finish("r1", "succeeded", 1, "26")
    assert f.history("r1")["value"] == "28"  # Request remains part of history.
    assert f.history("r1")["accepted_value"] == "26"
    assert f.current("subtitle")["last_confirmed"][1] == "26"
    assert f.current("subtitle")["state"] == "confirmed_different"
    f.finish("r1", "succeeded", 1, "26")
    try:
        f.finish("r1", "succeeded", 1, "28")
    except AssertionError:
        pass
    else:
        raise AssertionError("changed accepted value must not be treated as a duplicate")
    cases["accepted_value_is_not_requested_value"] = f.snapshot()

    g = Ledger()
    g.choose("subtitle", "28")
    g.begin("r1", "subtitle")
    try:
        g.finish("r1", "succeeded", 1)
    except AssertionError:
        pass
    else:
        raise AssertionError("missing accepted value must not confirm the requested value")
    assert not g.confirmed and g.attempts["r1"].status == "pending"
    cases["missing_accepted_value_rejected"] = g.snapshot()

    timer = Countdown("p1", "s1", 8000)
    request = TimerRequest("p1", "s1")
    assert timer.render(request, "p1", 2400) == {"seconds": 6, "revision": 1}
    assert "drop" in timer.render(request, "p1", 8000)
    timer.update_deadline("s1", 12000, 2)
    timer.update_deadline("s1", 9000, 1)
    assert timer.render(request, "p1", 8500) == {"seconds": 4, "revision": 2}
    timer.pause(9000)
    assert timer.render(request, "p1", 20000) == {"drop": "paused"}
    timer.resume(20000)
    assert timer.render(request, "p1", 21000) == {"seconds": 2, "revision": 2}
    assert timer.render(request, "p2", 21000) == {"drop": "old_page"}
    timer.cancel()
    assert timer.render(request, "p1", 21000) == {"drop": "cancelled"}
    replacement = Countdown("p1", "s2", 30000)
    assert replacement.render(request, "p1", 21000) == {"drop": "old_session"}
    result = {"model_only": True, "checks": "all finite assertions passed",
              "causality_cases": cases, "timer_inputs_and_outputs": timer.events,
              "replacement_timer": replacement.events,
              "not_tested": ["storage", "network", "OS sleep/pause behavior", "UIA", "audio", "user experience"]}
    output = Path(__file__).with_name("causal-freshness-result.json")
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"causality_cases": len(cases), "timer_log_entries": len(timer.events) + len(replacement.events),
                      "checks": result["checks"], "output": str(output)}, ensure_ascii=False))


if __name__ == "__main__":
    run()
