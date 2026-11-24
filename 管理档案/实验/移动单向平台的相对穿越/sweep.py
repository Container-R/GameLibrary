"""Point-foot sweep against a horizontal top segment, with exact rational arithmetic."""
from fractions import Fraction as F
from typing import NamedTuple

class P(NamedTuple):
    x: F
    y: F

def crossing(foot0, foot1, platform0, platform1, width, ignore=False):
    """Screen sign convention: y increases upwards. Platform position is left endpoint."""
    if ignore:
        return ("ignore", None, None)
    d0, d1 = foot0.y - platform0.y, foot1.y - platform1.y
    if not (d0 >= 0 >= d1 and d0 > d1):
        return ("no-top-crossing", None, None)
    t = F(d0, d0 - d1)
    x0, x1 = foot0.x - platform0.x, foot1.x - platform1.x
    offset = x0 + t * (x1 - x0)
    return ("land" if 0 <= offset <= width else "miss-width", t, offset)

def retain_support(same_platform, leave_requested, end_offset, width, end_gap, slop):
    # Applies only to previously solved support, not to a new landing.
    return same_platform and not leave_requested and 0 <= end_offset <= width and abs(end_gap) <= slop

def still_ignored(body_top, surface_top, thickness, reset_gap):
    # Deliberately conservative: re-enable only once the entire body is below the slab.
    return body_top >= surface_top - thickness - reset_gap

cases = (
    ("world-up / relative-down", P(4,4), P(5,5), P(0,0), P(2,6), 4, False, ("land", F(4,5), F(16,5))),
    ("endpoint in width / crossing missed", P(5,4), P(5,5), P(0,0), P(5,6), F(1,2), False, ("miss-width", F(4,5), F(1))),
    ("world-down / relative-up from below", P(2,-2), P(2,-3), P(0,0), P(0,-5), 4, False, ("no-top-crossing", None, None)),
    ("explicit drop suppresses landing", P(4,4), P(5,5), P(0,0), P(2,6), 4, True, ("ignore", None, None)),
)
for name, f0, f1, p0, p1, width, ignored, expected in cases:
    actual = crossing(f0, f1, p0, p1, width, ignored)
    assert actual == expected
    kind, t, local_x = actual
    print(f"{name}: world dy={f1.y-f0.y:+}; normal gap {f0.y-p0.y:+}->{f1.y-p1.y:+}; {kind}, t={t}, x_local={local_x}")

for desc, actual, expected in (
    ("retain at zero relative approach", retain_support(True, False, 2, 4, 0, F(1,10)), True),
    ("leave at segment edge", retain_support(True, False, 5, 4, 0, F(1,10)), False),
    ("release on jump/drop request", retain_support(True, True, 2, 4, 0, F(1,10)), False),
    ("drop still ignored while body intersects slab", still_ignored(-1, 0, 2, F(1,4)), True),
    ("drop still ignored within clearance threshold", still_ignored(F(-17,8), 0, 2, F(1,4)), True),
    ("drop may re-arm after complete clearance", still_ignored(F(-5,2), 0, 2, F(1,4)), False),
):
    assert actual == expected
    print(f"{desc}: {actual}")
