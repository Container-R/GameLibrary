"""Four actual independent-actor callback schedules; no third-party imports."""
import hashlib
import json
import os
import platform
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)
(OUT / "summary.json").unlink(missing_ok=True)
if sys.flags.optimize:
    raise RuntimeError("Run without -O")
BINARY = Path("/usr/local/bin/godot")
sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
summary = {"python_version": sys.version, "python_executable": sys.executable,
           "platform": platform.platform(), "binary": str(BINARY), "binary_sha256": sha(BINARY),
           "source_sha256": {n: sha(ROOT/n) for n in
              ("run.py", "main.gd", "main.tscn", "project.godot", "contract.md")},
           "runs": []}

def need(condition, message):
    if not condition:
        raise RuntimeError(message)

def raw(value):
    if value is None:
        return ""
    return value.decode(errors="replace") if isinstance(value, bytes) else value

for mode in ("immediate", "staged"):
    for first in ("A", "B"):
        name = mode + "-" + first
        # Each execution gets a new isolated HOME/XDG, preserving logs outside it.
        with tempfile.TemporaryDirectory(prefix="combat-godot-") as temp:
            env = os.environ.copy()
            for key in ("HOME", "XDG_CACHE_HOME", "XDG_DATA_HOME", "XDG_CONFIG_HOME"):
                path = Path(temp)/key
                path.mkdir()
                env[key] = str(path)
            env["GODOT_SILENCE_ROOT_WARNING"] = "1"
            command = [str(BINARY), "--headless", "--single-threaded-scene",
                       "--path", str(ROOT), "--", mode, first]
            metadata = {"command": command, "timeout_seconds": 20}
            try:
                p = subprocess.run(command, cwd=ROOT, env=env, capture_output=True,
                                   text=True, timeout=20)
            except subprocess.TimeoutExpired as exc:
                (OUT/f"{name}.stdout").write_text(raw(exc.stdout))
                (OUT/f"{name}.stderr").write_text(raw(exc.stderr))
                metadata["timeout"] = True
                (OUT/f"{name}.status.json").write_text(json.dumps(metadata, indent=2)+"\n")
                raise
            except OSError as exc:
                metadata["spawn_error"] = repr(exc)
                (OUT/f"{name}.status.json").write_text(json.dumps(metadata, indent=2)+"\n")
                raise
            (OUT/f"{name}.stdout").write_text(p.stdout)
            (OUT/f"{name}.stderr").write_text(p.stderr)
            metadata.update(returncode=p.returncode, timeout=False)
            (OUT/f"{name}.status.json").write_text(json.dumps(metadata, indent=2)+"\n")
        need(p.returncode == 0 and not p.stderr and "ERROR" not in p.stdout, name+" engine failure")
        records = [json.loads(line.split("=",1)[1]) for line in p.stdout.splitlines()
                   if line.startswith("RESULT_JSON=")]
        need(len(records) == 1, name+" result count")
        result = records[0]
        traces = [json.loads(line.split("=",1)[1]) for line in p.stdout.splitlines()
                  if line.startswith("TRACE_JSON=")]
        second = "B" if first == "A" else "A"
        need([r["label"] for r in traces] == ["Begin",first,second,"End"], name+" callback order")
        need(result["trace"] == traces, name+" raw trace mismatch")
        need(len({r["frame"] for r in traces}) == 1, name+" frame mismatch")
        need([r["priority"] for r in traces] == [-100,0,10,100], name+" priority")
        need(all(r["group"] == 0 and abs(r["delta"]-1/60) < 1e-8 for r in traces), name+" group/delta")
        need(result["root_group"] == 0 and result["physics_ticks_per_second"] == 60, name+" root")
        need(result["mode"] == mode and result["first"] == first and result["tree_order"] == ["Begin","A","B","End"], name+" configuration")
        need(result["initial"] == result["snapshot"] == {"A":1,"B":1}, name+" snapshot")
        expected_hp = {"A":0,"B":0} if mode == "staged" else {first:1,second:0}
        need(result["hp"] == expected_hp, name+" hp")
        expected_intents = [{"attacker":a,"target":"B" if a=="A" else "A","damage":1,"frame":traces[0]["frame"]}
                            for a in ([first,second] if mode=="staged" else [first])]
        need(result["intents"] == expected_intents, name+" intents")
        expected_events = []
        for intent in expected_intents:
            expected_events.extend([{"kind":"damage","attacker":intent["attacker"],"target":intent["target"],"amount":1},
                                    {"kind":"death","actor":intent["target"]}])
        need(result["events"] == expected_events, name+" events")
        need(traces[1]["eligible"] is True and traces[2]["eligible"] is (mode=="staged"), name+" eligibility")
        expected_before = [{"A":1,"B":1}]*4 if mode=="staged" else [{"A":1,"B":1}]*2+[expected_hp]*2
        need([r["hp_before"] for r in traces] == expected_before, name+" callback HP")
        summary["runs"].append({"name":name, "result":result})
(OUT/"summary.json").write_text(json.dumps(summary, indent=2)+"\n")
print("PASS: four fresh processes; one complete combat physics frame each")
