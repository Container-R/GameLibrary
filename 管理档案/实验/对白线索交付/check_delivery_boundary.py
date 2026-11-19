"""Synthetic delivery state: queue/focus is not an exposure; save is one snapshot."""
from dataclasses import dataclass, field
import json
from itertools import count


# Session ids are never reused inside this test process, even when reopening old saves.
SESSION_IDS = count(1)


@dataclass
class Story:
    facts: dict = field(default_factory=lambda: {"visitor": ["heard_tram_exists"]})
    committed: set = field(default_factory=set)
    staged: dict = field(default_factory=dict)
    focus: str | None = None
    session: int = field(default_factory=lambda: next(SESSION_IDS))
    play_counter: int = 0

    def queue(self, content_id, listener, enabled=("subtitle", "voice")):
        self.play_counter += 1
        event_id = f"{self.session}:{self.play_counter}:{content_id}"
        self.staged[event_id] = (listener, frozenset(enabled))
        return event_id

    def cancel(self, event_id):
        self.staged.pop(event_id, None)

    def focus_known(self, listener, fact):
        if fact in self.facts.get(listener, []):
            self.focus = fact

    def disclose(self, event_id, listener, channel, marker):
        # Different transports send the same author-assigned marker.
        key = (event_id, listener, marker)
        if key in self.committed:
            return "duplicate_delivery"
        staged = self.staged.get(event_id)
        if staged is None or staged[0] != listener or marker != "reveals_platform_v2":
            return "no_matching_live_delivery"
        if channel not in staged[1]:
            return "channel_not_enabled"
        # One authoritative update persists both effect and idempotency key.
        ledger = self.facts.setdefault(listener, [])
        if "new_notice:west@2" not in ledger:
            ledger.append("new_notice:west@2")
        self.committed.add(key)
        return f"granted_from_{channel}"

    def save(self):
        return json.dumps({"facts": self.facts, "committed": sorted(self.committed)})

    @classmethod
    def from_save(cls, payload):
        p = json.loads(payload)
        # This policy drops uncommitted pending presentations after load.
        return cls(p["facts"], set(tuple(x) for x in p["committed"]))


s = Story()
trace = []
fact = "new_notice:west@2"
def record(name, result, known):
    assert (fact in s.facts["visitor"]) == known
    trace.append({"case": name, "result": result, "known": known})


record("preview", "metadata_only", False)
s.focus_known("visitor", "heard_tram_exists")
assert s.focus == "heard_tram_exists"
record("focus_known_topic", "changed_relevance_only", False)
line1 = s.queue("line-1", "visitor")
record("queue_line_before_cue", "no_delivery", False)
s.cancel(line1)
r = s.disclose(line1, "visitor", "voice", "reveals_platform_v2")
assert r == "no_matching_live_delivery"
record("cancel_then_late_voice", r, False)
line1_again = s.queue("line-1", "visitor")
assert line1_again != line1
r = s.disclose(line1, "visitor", "voice", "reveals_platform_v2")
assert r == "no_matching_live_delivery"
record("old_callback_after_same_line_reopened", r, False)
r = s.disclose(line1_again, "visitor", "preview", "reveals_platform_v2")
assert r == "channel_not_enabled"
record("unsupported_channel_cannot_disclose", r, False)
line2 = s.queue("line-2", "visitor")
r = s.disclose(line2, "wrong_listener", "subtitle", "reveals_platform_v2")
assert r == "no_matching_live_delivery"
record("wrong_recipient", r, False)
s = Story.from_save(s.save())
r = s.disclose(line2, "visitor", "voice", "reveals_platform_v2")
assert r == "no_matching_live_delivery"
record("reload_without_uncommitted_queued_lines", r, False)
line2_reloaded = s.queue("line-2", "visitor")
assert line2_reloaded != line2
r = s.disclose(line2, "visitor", "voice", "reveals_platform_v2")
assert r == "no_matching_live_delivery"
record("old_callback_after_loading_and_reopening_same_line", r, False)
line3 = s.queue("line-3", "visitor")
r = s.disclose(line3, "visitor", "subtitle", "reveals_platform_v2")
assert r == "granted_from_subtitle"
record("same_fact_delivered_by_enabled_subtitle", r, True)
r = s.disclose(line3, "visitor", "voice", "reveals_platform_v2")
assert r == "duplicate_delivery"
record("voice_callback_is_same_disclosure", r, True)
s = Story.from_save(s.save())
r = s.disclose(line3, "visitor", "subtitle", "reveals_platform_v2")
assert r == "duplicate_delivery" and s.facts["visitor"].count(fact) == 1
record("reload_and_replay_already_committed_delivery", r, True)
# If dubbing is the enabled route, voice can commit after the authored cue.
voice_only = Story()
voice_event = voice_only.queue("voice-only", "visitor", enabled=("voice",))
assert voice_only.disclose(voice_event, "visitor", "subtitle", "reveals_platform_v2") == "channel_not_enabled"
assert voice_only.disclose(voice_event, "visitor", "voice", "reveals_platform_v2") == "granted_from_voice"
print(json.dumps({"scope": "synthetic disclosure, not middleware or audio/text rendering",
                  "trace": trace, "voice_only_commit_checked": True}, indent=2))
