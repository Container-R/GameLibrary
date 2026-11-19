"""Synthetic game NPC state; no engine integration or real-world tracking."""
import json
from dataclasses import dataclass

@dataclass
class Vision:
    event: int = -1
    visible: bool = False
    sample: int | None = None
    position: tuple[int, int] | None = None

class Evidence:
    def __init__(self):
        self.vision = Vision()
        self.sound = None

    def see(self, sample, pos=None):
        """None means sight lost, with no location read from target transform."""
        v = self.vision
        if sample <= v.event:
            return "nonnew_vision"
        v.event, v.visible = sample, pos is not None
        if pos is not None:
            v.sample, v.position = sample, pos
        return "applied"

    def hear(self, sample, point, identity=None):
        if self.sound and sample <= self.sound[0]:
            return "nonnew_sound"
        self.sound = sample, point, identity
        return "applied"

    def decide(self, now):
        v = self.vision
        if v.visible and v.position is not None:
            return ["observe_visible", v.position]
        # 6s from positive sight; a loss signal at t=3 does not reset this.
        if v.sample is not None and now < v.sample+6:
            return ["check_last_sight", v.position]
        if self.sound and now < self.sound[0]+4:
            return ["inspect_noise", self.sound[1]]
        return ["resume_patrol", None]

a = Evidence()
a.see(2, (4, 0))
a.see(3)
lost = a.decide(3)
# A hidden actor can move arbitrarily; movement is not an input to Evidence.
sound = a.hear(5, (2, 2))
late_old = a.see(1, (9, 9))
noisy = a.decide(5)
expired_visual = a.decide(8)
nothing = a.decide(9)
reacquire = a.see(10, (1, 7))
old_loss = a.see(9)
revisible = a.decide(10)
result = {
    "lost_visible_contact": lost, "sound_received": sound,
    "out_of_order_older_sight": late_old, "noise_does_not_replace_recent_last_seen": noisy,
    "expired_sight_uses_unexpired_noise": expired_visual, "expired_both": nothing,
    "reacquired": reacquire, "late_old_loss": old_loss, "fresh_vision": revisible,
}
assert result == {
    "lost_visible_contact": ["check_last_sight", (4, 0)], "sound_received": "applied",
    "out_of_order_older_sight": "nonnew_vision", "noise_does_not_replace_recent_last_seen": ["check_last_sight", (4, 0)],
    "expired_sight_uses_unexpired_noise": ["inspect_noise", (2, 2)], "expired_both": ["resume_patrol", None],
    "reacquired": "applied", "late_old_loss": "nonnew_vision", "fresh_vision": ["observe_visible", (1, 7)],
}
print(json.dumps(result,indent=2))
