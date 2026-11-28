"""Orthographic camera / single-bone fixture, not Unity animation or rendering."""
from math import cos, pi

VIEW = (0.0, 4.0)
IMPORTED = (-0.2, 0.55)
MEASURED_SAMPLES_ONLY = (-0.2, 0.625)
CONSERVATIVE = (-0.2, 1.25)
LOOSE = (-5.0, 5.0)


def actual_x(degrees):
    # Body extent and the tip of a 1.25-unit rigidly weighted feature.
    return (-0.2, max(0.2, 1.25 * cos(degrees * pi / 180)))


def test_interval(local, root_x):
    lo, hi = (x + root_x for x in local)
    return hi >= VIEW[0] and lo <= VIEW[1]


def case(label, deg, root, supplied, expected):
    tip = actual_x(deg)[1] + root
    result = (test_interval(supplied, root), test_interval(actual_x(deg), root))
    assert result == expected, (label, result)
    print(f"{label:17s} sampled_angle={deg:+.0f} tip_x={tip:+.3f} "
          f"box_pass={int(result[0])} geometry_overlap={int(result[1])}")


if __name__ == "__main__":
    case("reference", 0, 0.5, IMPORTED, (True, True))
    case("imported box", 0, -1.0, IMPORTED, (False, True))
    case("fixed box", 0, -1.0, CONSERVATIVE, (True, True))
    case("replay stale pose", 60, -1.0, CONSERVATIVE, (True, False))
    for a in (-60, 60):
        case("endpoint only", a, -1.0, MEASURED_SAMPLES_ONLY, (False, False))
    case("missed midpoint", 0, -1.0, MEASURED_SAMPLES_ONLY, (False, True))
    for a in range(-60, 61):
        assert actual_x(a)[1] <= CONSERVATIVE[1]
    case("loose box", 0, -3.0, LOOSE, (True, False))
    case("tight box far", 0, -3.0, CONSERVATIVE, (False, False))
