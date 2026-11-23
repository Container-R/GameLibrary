"""Isolated Python fixture: staged local autosaves, controlled publication order."""
import hashlib
import json
from pathlib import Path
from tempfile import TemporaryDirectory

FULL = ("enter", "music", "request1", "pan", "request2", "commit2", "commit1", "verify")
BASE = b'{"revision":0}\n'
FAIL = "FAIL:stale-autosave"
UNKNOWN = "UNRESOLVED"

def replay(events, guard=False):
    with TemporaryDirectory() as root:
        home = Path(root)
        live = home / "save.json"
        live.write_bytes(BASE)
        assert hashlib.sha256(live.read_bytes()).digest() == hashlib.sha256(BASE).digest()
        started, pending, commits = set(), {}, []
        active = False
        for event in events:
            if event == "enter":
                active = True
            elif event.startswith("request"):
                rev = int(event[-1])
                if not active or rev in started:
                    return UNKNOWN
                started.add(rev)
                stage = home / f"stage-{rev}.json"
                stage.write_text(json.dumps({"revision": rev}), encoding="utf-8")
                pending[rev] = stage
            elif event.startswith("commit"):
                rev = int(event[-1])
                if rev not in pending:
                    return UNKNOWN
                stage = pending.pop(rev)
                current = json.loads(live.read_bytes())["revision"]
                if guard and rev <= current:
                    stage.unlink()
                else:
                    stage.replace(live)
                    commits.append(rev)
            elif event == "verify":
                if pending or started != {1, 2}:
                    return UNKNOWN
                actual = json.loads(live.read_bytes())["revision"]
                if actual == 2:
                    return "PASS"
                if actual == 1 and commits == [2, 1]:
                    return FAIL
                return UNKNOWN
    return UNKNOWN

def reduce_by_deletion(events):
    while True:
        # Try deleting chunks, then individual events; keep original order.
        for size in (len(events) // 2, 2, 1):
            if not size:
                continue
            for start in range(len(events) - size + 1):
                trial = events[:start] + events[start + size:]
                if replay(trial) == FAIL:
                    events = trial
                    break
            else:
                continue
            break
        else:
            return events

def main():
    core = reduce_by_deletion(FULL)
    print(f"baseline sha256={hashlib.sha256(BASE).hexdigest()}")
    print("reduced:", " ".join(core))
    cases = (
        ("full", FULL, False, FAIL),
        ("reduced", core, False, FAIL),
        ("swapped", core[:3] + ("commit1", "commit2", "verify"), False, "PASS"),
        ("orphan_commit", tuple(e for e in core if e != "request1"), False, UNKNOWN),
        ("missing_observation", core[:-1], False, UNKNOWN),
        ("guarded", core, True, "PASS"),
    )
    for name, events, guard, expected in cases:
        result = replay(events, guard)
        assert result == expected, (name, result, expected)
        print(f"{name}: {result}")
    for i, event in enumerate(core):
        result = replay(core[:i] + core[i+1:])
        assert result != FAIL
        print(f"drop {event}: {result}")

if __name__ == "__main__":
    main()
