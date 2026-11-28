"""Synthetic 2D segment/box query. No SDK or network dependency."""
from dataclasses import dataclass
from fractions import Fraction as F


@dataclass(frozen=True)
class Box:
    name: str
    x: F
    y: F = F(0)
    radius_x: F = F(1, 4)
    radius_y: F = F(1, 4)

    def first_intersection(self, length=F(10)):
        # Segment runs from (0,0) toward (length,0).
        front = max(F(0), self.x - self.radius_x)
        back = min(length, self.x + self.radius_x)
        return front if abs(self.y) <= self.radius_y and front <= back else None


def outcome(target, gate):
    intersections = []
    for box in (target, gate):
        if box is not None and (d := box.first_intersection()) is not None:
            intersections.append((d, box.name))
    intersections.sort()
    if not intersections:
        return "miss", "-"
    first = intersections[0][1]
    return ("blocked" if first == "gate" else "reached",
            ",".join(f"{name}@{d}" for d, name in intersections))


closed = Box("gate", F(4))
opened = Box("gate", F(4), F(1))
target = Box("target", F(8))
off_target = Box("target", F(8), F(3, 5))

cases = [
    ("open->closed", target, opened, closed, ("reached", "blocked")),
    ("closed->open", target, closed, opened, ("blocked", "reached")),
    ("closed static", target, closed, closed, ("blocked", "blocked")),
    ("gate removed", target, None, None, ("reached", "reached")),
    ("target off line", off_target, opened, opened, ("miss", "miss")),
]

if __name__ == "__main__":
    for label, checked, then, now, results in cases:
        historic, current = outcome(checked, then), outcome(checked, now)
        assert (historic[0], current[0]) == results
        print(f"{label:16s} historical={historic[0]:7s} [{historic[1]}]; current={current[0]:7s} [{current[1]}]")
