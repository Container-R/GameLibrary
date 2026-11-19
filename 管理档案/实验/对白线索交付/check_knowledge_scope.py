"""Synthetic authoring test: fact, exposure, source and character scope are separate."""
from dataclasses import asdict, dataclass
import json


@dataclass(frozen=True)
class Evidence:
    actor: str
    fact: str
    value: str
    subject_version: int
    channel: str
    source: str
    delivery: str


class Session:
    def __init__(self):
        self.archive_revision = 1
        self.real_platform = "east"
        self.evidence = {}
        self.entries_opened = set()
        self.deliveries = set()

    def revise_unseen(self):
        self.archive_revision += 1
        self.real_platform = "west"

    def open_notice(self, actor):
        self.entries_opened.add(actor)

    def receive(self, e, cue_was_delivered):
        if not cue_was_delivered or e.delivery in self.deliveries:
            return False
        self.deliveries.add(e.delivery)  # idempotent committed presentation ID
        self.evidence.setdefault((e.actor, e.fact), []).append(e)
        return True

    def options(self, actor):
        # Does not read real_platform or archive_revision; they're world state.
        options = ["ask_current_platform"]
        facts = self.evidence.get((actor, "tram_platform"), [])
        if facts:
            recent = max(facts, key=lambda e: (e.subject_version, e.channel == "posted_notice"))
            options.append(f"cite_{recent.channel}:{recent.value}@{recent.subject_version}")
        return options

    def respond(self, actor, choice):
        # Re-evaluate actor and evidence on selecting a cached choice.
        if choice not in self.options(actor):
            return "choice_no_longer_available"
        if choice == "ask_current_platform":
            return "ask_without_revealing_it_in_the_option"
        version = int(choice.rsplit("@", 1)[1])
        if version != self.archive_revision:
            return "clerk_flags_old_notice_without_granting_new_value"
        kind = choice.split(":")[0]
        return {"cite_hearsay": "ask_clerk_to_verify_report",
                "cite_posted_notice": "show_current_posted_notice"}[kind]


s = Session()
alice, ben = "visitor", "new_arrival"
trace = []
def check(label, actor, expected):
    actual = s.options(actor)
    assert actual == expected, (label, actual, expected)
    trace.append({"case": label, "actor": actor, "options": actual})

ask = ["ask_current_platform"]
e_v1 = Evidence(alice, "tram_platform", "east", 1, "posted_notice", "station_noticeboard", "notice/a/v1")
s.open_notice(alice)
assert not s.receive(e_v1, False)
check("noticed_panel_but_left_before_reveal", alice, ask)
assert s.receive(e_v1, True)
assert not s.receive(e_v1, True)
check("notice_actually_delivered", alice, [*ask, "cite_posted_notice:east@1"])
check("switch_protagonist_no_implicit_transfer", ben, ask)
assert s.respond(ben, "cite_posted_notice:east@1") == "choice_no_longer_available"
e_heard = Evidence(ben, "tram_platform", "east", 1, "hearsay", alice, "talk/b/east")
assert s.receive(e_heard, True)
check("new_protagonist_hears_report", ben, [*ask, "cite_hearsay:east@1"])
assert s.respond(ben, "cite_hearsay:east@1") == "ask_clerk_to_verify_report"
s.revise_unseen()
check("hidden_world_revision_does_not_leak_in_ui", alice, [*ask, "cite_posted_notice:east@1"])
assert s.respond(alice, "cite_posted_notice:east@1") == "clerk_flags_old_notice_without_granting_new_value"
check("reply_has_not_yet_revealed_replacement", alice, [*ask, "cite_posted_notice:east@1"])
e_v2 = Evidence(alice, "tram_platform", "west", 2, "posted_notice", "station_noticeboard", "notice/a/v2")
assert s.receive(e_v2, True)
check("new_notice_actually_delivered", alice, [*ask, "cite_posted_notice:west@2"])
assert s.respond(alice, "cite_posted_notice:east@1") == "choice_no_longer_available"
assert s.respond(alice, "cite_posted_notice:west@2") == "show_current_posted_notice"
check("hearsay_retains_its_old_provenance", ben, [*ask, "cite_hearsay:east@1"])
print(json.dumps({"scope": "synthetic two-character station narrative, not an engine",
                  "trace": trace, "evidence": [asdict(e_v1), asdict(e_heard), asdict(e_v2)]},
                 indent=2))
