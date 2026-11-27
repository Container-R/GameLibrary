"""Reduced model of group selection; does not run Unity."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Binding:
    label: str
    kind: str
    groups: tuple = ()

def select(rows, group, composite_parts):
    result = []
    for i, row in enumerate(rows):
        if row.kind == "part":
            continue
        matched = group in row.groups
        if not matched and composite_parts and row.kind == "root":
            for part in rows[i + 1:]:
                if part.kind != "part":
                    break
                if group in part.groups:
                    matched = True
                    break
        if matched:
            result.append(row.label)
    return result

fixture = [
    Binding("Pad root", "root"), Binding("pad part", "part", ("Pad",)),
    Binding("Move root", "root"), Binding("up", "part", ("Keyboard",)),
    Binding("down", "part", ("Keyboard",)), Binding("alt", "part", ("Pad",)),
    Binding("Jump", "ordinary", ("Keyboard",)),
]
for group, expected_old, expected_new in [
    ("Keyboard", ["Jump"], ["Move root", "Jump"]),
    ("Pad", [], ["Pad root", "Move root"]),
    ("Other", [], []),
]:
    old, new = select(fixture, group, False), select(fixture, group, True)
    assert old == expected_old and new == expected_new, (group, old, new)
    print(f"{group}: old={old}; new={new}")
