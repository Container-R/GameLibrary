"""Project-level event policy model; times in ms, not engine callback behavior."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Cue:
    at: int
    source: str
    foot: str
    step: int

def by_owner(cues):
    return [e for e in cues if e.source == ("walk" if e.at < 500 else "run")]

def global_debounce(cues, window):
    heard = []
    for e in sorted(cues, key=lambda entry: entry.at):
        if not heard or e.at - heard[-1].at >= window:
            heard.append(e)
    return heard

def crossings(previous, current, count=2):
    """Unwrapped integer phase. Contact markers at 0 and 500 of each 1000."""
    assert count == 2 and 0 <= previous <= current
    for index in range(previous // 500 + 1, current // 500 + 1):
        yield index, ("R" if index % 2 else "L")

def exercise():
    duplicate = [Cue(480, "walk", "L", 4), Cue(520, "run", "L", 4)]
    missing = [Cue(480, "run", "L", 4), Cue(520, "walk", "L", 4)]
    assert len(by_owner(duplicate)) == 2 and len(by_owner(missing)) == 0
    expected = [(4, "L"), (5, "R"), (6, "L")]
    assert list(crossings(1900, 3000)) == expected
    sliced = [(1900, 2000), (2000, 2180), (2180, 2500), (2500, 3000)]
    assert [step for previous, current in sliced for step in crossings(previous, current)] == expected
    fast = [Cue(480, "walk", "L", 4), Cue(520, "run", "R", 5)]
    assert len(global_debounce(duplicate, 60)) == 1
    assert len(global_debounce(fast, 60)) == 1  # wrong: two distinct steps
    print("Per-clip owner: duplicate=2, missed=0")
    print("Canonical unwrapped phase: [(4,L),(5,R),(6,L)] in one coarse tick and 4 fine ticks")
    print("60 ms global debounce wrongly drops a distinct right-foot event")

if __name__ == "__main__":
    exercise()
