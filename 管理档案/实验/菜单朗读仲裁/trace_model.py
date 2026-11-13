"""Original admission model, not a UIA/NVDA implementation or audio test.

All completion callbacks below are injected by the test driver.
Run from any directory. Writes trace-result.json next to this script.
"""
from dataclasses import asdict, dataclass
from pathlib import Path
import json


@dataclass
class Item:
    kind: str
    identity: str
    page: str
    text: str
    token: int = 0
    session: str | None = None


class Model:
    def __init__(self):
        self.page = None
        self.focus = None
        self.active = None
        self.results = []
        self.latest_countdown = None
        self.countdown_seq = {}
        self.current_session = None
        self.session_binding_revision = 0
        self.operations = {}
        self.token = 0
        self.events = []
        self.actions = []
        self.submitted = []

    def cancel_active(self):
        if self.active:
            self.actions.append(f"cancel_token:{self.active.token}")
            if self.active.kind == "result":
                self.results.insert(0, self.active)
            self.active = None

    def submit(self, item):
        self.token += 1
        item.token = self.token
        self.active = item
        self.submitted.append(asdict(item))
        self.actions.append(f"request:{item.identity}:token{item.token}")

    def dispatch(self):
        if self.active:
            return
        if self.results:
            item = self.results.pop(0)
            if item.page != self.page:
                item.text = "之前的" + item.text.removeprefix("之前的")
            self.submit(item)
        elif self.latest_countdown:
            item = self.latest_countdown
            self.latest_countdown = None
            assert item.page == self.page
            assert item.session == self.current_session
            self.submit(item)

    def apply(self, name, *args):
        self.actions = []
        if name == "open":
            assert self.page is None
            self.page = args[0]
            # Opening snapshot and later session events come from the match owner.
            self.current_session = args[1] if len(args) > 1 else None
            self.session_binding_revision = args[2] if len(args) > 2 else 0
        elif name == "session":
            page, binding_revision, match = args
            if page != self.page or binding_revision <= self.session_binding_revision:
                self.actions.append("ignore_stale_session_binding")
            else:
                changed = match != self.current_session
                self.current_session = match
                self.session_binding_revision = binding_revision
                if changed:
                    self.latest_countdown = None
                    if self.active and self.active.kind == "countdown":
                        self.cancel_active()
                    self.actions.append("invalidate_old_session_countdown")
                    self.dispatch()
        elif name == "focus":
            page, revision, control = args
            if page != self.page or (self.focus and revision <= self.focus[1]):
                self.actions.append("ignore_stale_focus")
            else:
                self.focus = (page, revision, control)
                self.cancel_active()
                self.submit(Item("focus", f"{page}/focus/{revision}", page, control))
        elif name == "begin":
            op, target = args
            assert op not in self.operations
            self.operations[op] = {"page": self.page, "target": target, "result": None}
        elif name == "failure":
            op = args[0]
            record = self.operations[op]
            if record["result"] is not None:
                self.actions.append("ignore_duplicate_result:" + op)
            else:
                record["result"] = "failed"
                self.results.append(Item("result", op, record["page"], record["target"] + "保存失败"))
                self.dispatch()
        elif name == "countdown":
            page, match, sequence, seconds = args
            key = (page, match)
            if (page != self.page or match is None or match != self.current_session
                    or sequence <= self.countdown_seq.get(key, -1)):
                self.actions.append("ignore_stale_countdown")
            else:
                self.countdown_seq[key] = sequence
                self.latest_countdown = Item("countdown", f"{page}/{match}/{seconds}", page,
                                             f"剩余{seconds}秒", session=match)
                self.actions.append("replace_pending_countdown:" + str(seconds))
                self.dispatch()
        elif name == "complete":
            token = args[0]
            if not self.active or token != self.active.token:
                self.actions.append("ignore_stale_completion:" + str(token))
            else:
                self.actions.append("synthetic_complete:" + self.active.identity)
                self.active = None
                self.dispatch()
        elif name == "close":
            assert self.page == args[0]
            self.cancel_active()
            self.latest_countdown = None
            self.focus = None
            self.page = None
            self.current_session = None
            self.session_binding_revision = 0
            # No automatic dispatch in a routing transition.
        else:
            raise ValueError(name)
        self.events.append({
            "step": len(self.events) + 1,
            "input": [name, *args],
            "actions": list(self.actions),
            "page": self.page,
            "current_session": self.current_session,
            "session_binding_revision": self.session_binding_revision,
            "active": asdict(self.active) if self.active else None,
            "pending_results": [i.identity for i in self.results],
            "pending_countdown": self.latest_countdown.identity if self.latest_countdown else None,
        })
        return self.active.token if self.active else None


def run():
    m = Model()
    m.apply("open", "p1", "match1", 1)
    m.apply("focus", "p1", 1, "A")
    m.apply("focus", "p1", 2, "B")
    c = m.apply("focus", "p1", 3, "C")
    m.apply("begin", "r1", "字幕设置")
    m.apply("begin", "r2", "画质设置")
    m.apply("countdown", "p1", "match1", 1, 8)
    m.apply("failure", "r1")
    m.apply("countdown", "p1", "match1", 2, 7)
    r1 = m.apply("complete", c)
    m.apply("countdown", "p1", "match1", 3, 6)
    countdown = m.apply("complete", r1)
    m.apply("close", "p1")
    m.apply("open", "p2")
    new_focus = m.apply("focus", "p2", 1, "C")
    m.apply("complete", countdown)
    m.apply("focus", "p1", 4, "obsolete-C")
    m.apply("failure", "r1")
    assert m.active.token == new_focus
    m.apply("failure", "r2")
    m.apply("begin", "r3", "字幕设置")
    m.apply("failure", "r3")
    assert [i.identity for i in m.results] == ["r2", "r3"]
    r2 = m.apply("complete", new_focus)
    assert m.active.text == "之前的画质设置保存失败"
    assert m.active.page == "p1" and m.page == "p2"
    r3 = m.apply("complete", r2)
    assert m.active.text == "字幕设置保存失败" and m.active.page == "p2"
    m.apply("complete", r3)
    result_ids = [i["identity"] for i in m.submitted if i["kind"] == "result"]
    countdown_ids = [i["identity"] for i in m.submitted if i["kind"] == "countdown"]
    assert result_ids == ["r1", "r2", "r3"]
    assert countdown_ids == ["p1/match1/6"]
    assert len(m.operations) == 3 and all(o["result"] == "failed" for o in m.operations.values())
    baseline = ["focus-A", "focus-B", "focus-C", "r1-failed", "countdown-8", "countdown-7", "countdown-6"]
    interrupted = Model()
    interrupted.apply("open", "p3")
    f1 = interrupted.apply("focus", "p3", 1, "A")
    interrupted.apply("begin", "r4", "字幕设置")
    interrupted.apply("failure", "r4")
    old_result = interrupted.apply("complete", f1)
    f2 = interrupted.apply("focus", "p3", 2, "B")
    interrupted.apply("complete", old_result)
    assert interrupted.active.token == f2
    new_result = interrupted.apply("complete", f2)
    assert new_result != old_result and interrupted.active.identity == "r4"
    interrupted.apply("complete", new_result)
    interrupted.apply("failure", "r4")
    result_attempts = [i for i in interrupted.submitted if i["kind"] == "result"]
    assert len(result_attempts) == 2 and len(interrupted.operations) == 1
    assert interrupted.active is None and not interrupted.results
    switching = Model()
    switching.apply("open", "p4", "old", 1)
    focus_token = switching.apply("focus", "p4", 1, "A")
    switching.apply("countdown", "p4", "old", 1, 8)
    switching.apply("session", "p4", 2, "new")
    switching.apply("countdown", "p4", "new", 1, 20)
    switching.apply("countdown", "p4", "old", 2, 7)
    assert switching.latest_countdown.identity == "p4/new/20"
    switching.apply("session", "p4", 1, "old")
    assert switching.current_session == "new"
    old_output = switching.apply("complete", focus_token)
    assert switching.active.identity == "p4/new/20"
    switching.apply("session", "p4", 3, "newer")
    assert switching.active is None
    newest_output = switching.apply("countdown", "p4", "newer", 1, 30)
    switching.apply("complete", old_output)
    assert switching.active.token == newest_output
    assert [x["identity"] for x in switching.submitted if x["kind"] == "countdown"] == [
        "p4/new/20", "p4/newer/30"]
    report = {
        "model_only": True,
        "completion_callbacks": "synthetic test driver input; no audio or UIA acknowledgements",
        "baseline_input": baseline,
        "fifo_retains_obsolete_focus": "focus-A" in baseline and "focus-B" in baseline,
        "latest_only_loses_operation_result": baseline[-1] != "r1-failed",
        "checks": "assertions passed for this finite trace only",
        "submitted": m.submitted,
        "retained_operation_history": m.operations,
        "trace": m.events,
        "interrupted_result_trace": interrupted.events,
        "interrupted_result_request_count": len(result_attempts),
        "session_switch_trace": switching.events,
        "session_switch_submitted": switching.submitted,
    }
    out = Path(__file__).with_name("trace-result.json")
    out.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"steps": len(m.events), "interrupted_result_steps": len(interrupted.events), "session_switch_steps": len(switching.events), "result_requests": result_ids, "countdown_requests": countdown_ids, "interrupted_result_requests": len(result_attempts), "assertions": "passed", "output": str(out)}, ensure_ascii=False))


if __name__ == "__main__":
    run()
