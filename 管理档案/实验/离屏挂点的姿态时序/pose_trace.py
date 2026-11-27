"""Synthetic diagnostic: one axis, no Unity/Unreal code or measurements."""
import csv
import sys

CASES = {
    # Held samples distinguish value equality from freshness.
    # Animated samples make stale writes visible even when the actor translates.
    "normal": (True, False, (), False),
    "stale": (True, False, (2, 3), False),
    "early": (True, True, (), False),
    "missing": (False, False, (), False),
    "fresh_same_value": (True, False, (), True),
}

def make_rows(case):
    valid, early, skip, constant = CASES[case]
    published_id, published_x = 1, 10
    for frame in range(2, 5):
        if early:
            read_id, read_x = published_id, published_x
        if frame not in skip:
            published_id = frame
            published_x = 10 if constant else frame * 10
        if not early:
            read_id, read_x = published_id, published_x
        component_x = 100 * frame
        world_x = component_x + read_x if valid else component_x
        yield (frame, frame, valid, component_x,
               read_id if valid else None, read_x if valid else None,
               published_id, world_x)

EXPECTED = {
    "normal": [(2, 20, 2, 220), (3, 30, 3, 330), (4, 40, 4, 440)],
    "stale": [(1, 10, 1, 210), (1, 10, 1, 310), (4, 40, 4, 440)],
    "early": [(1, 10, 2, 210), (2, 20, 3, 320), (3, 30, 4, 430)],
    "missing": [(None, None, 2, 200), (None, None, 3, 300), (None, None, 4, 400)],
    "fresh_same_value": [(2, 10, 2, 210), (3, 10, 3, 310), (4, 10, 4, 410)],
}

if __name__ == "__main__":
    table = csv.writer(sys.stdout, lineterminator="\n")
    table.writerow(("case", "frame", "requested_sample_id", "socket_valid",
                    "component_world_x_cm", "used_pose_id", "socket_component_x_cm",
                    "published_id_after_producer", "returned_world_x_cm"))
    for case, expected in EXPECTED.items():
        rows = list(make_rows(case))
        assert [row[4:] for row in rows] == expected
        table.writerows((case, *row) for row in rows)
