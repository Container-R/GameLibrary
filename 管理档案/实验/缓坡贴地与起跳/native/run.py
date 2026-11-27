import json
import math
import os
from pathlib import Path
import subprocess
from tempfile import TemporaryDirectory

project = Path(__file__).resolve().parent
cases = (
    "ramp 0 run auto 60",
    "ramp 2 run auto 30",
    "ramp 2 run auto 60",
    "ramp 2 run auto 120",
    "ramp 4 jump auto 60",
    "ramp 4 jump manual 60",
    "ledge 2 run auto 60",
    "ledge 10 run auto 60",
)

rows = []
with TemporaryDirectory(prefix="ground-snap-") as tmp:
    env = os.environ.copy()
    env["GODOT_SILENCE_ROOT_WARNING"] = "1"
    for tag in ("CONFIG", "DATA", "CACHE"):
        d = Path(tmp) / tag
        d.mkdir()
        env[f"XDG_{tag}_HOME"] = str(d)
    for case in cases:
        args = case.split()
        proc = subprocess.run(
            [os.environ.get("GODOT", "godot"), "--headless", "--path", str(project),
             "-s", "res://probe.gd", "--", *args],
            env=env, text=True, capture_output=True, check=True, timeout=10,
        )
        if "ERROR:" in proc.stderr:
            raise RuntimeError(proc.stderr)
        lines = [s for s in proc.stdout.splitlines() if s.startswith("{")]
        assert len(lines) == 1
        row = json.loads(lines[0])
        assert row["case"] == args
        assert math.isclose(row["physics_dt"], 1 / int(args[-1]))
        rows.append(row)

assert [r["final"]["floor"] for r in rows] == [False, False, True, True, False, True, False, True]
_, _, _, _, auto, manual, short, long = rows
assert auto["start"] == manual["start"]
assert auto["moved"] == manual["moved"]
assert manual["moved"]["delta"][1] < 0 < manual["final"]["delta"][1]
assert manual["final"]["real"] == manual["moved"]["real"]
assert manual["final"]["velocity"] == manual["moved"]["velocity"] == [360., -90.]
assert short["start"] == long["start"]
assert all(r["final"]["p"][0] - 2 > 200 for r in (short, long))
assert 7.5 < long["final"]["delta"][1] < 8.5
for row in rows:
    print(json.dumps(row, sort_keys=True, separators=(",", ":")))
