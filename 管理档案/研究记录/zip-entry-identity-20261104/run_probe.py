"""Finite runner requiring a matching, separately reviewed FREEZE.json."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parent
N = "weapons/rifle.json"
M = "weapons/pistol.json"
A = '{"damage":1}\n'
B = '{"damage":2}\n'


def expected_case(label, names, payloads, selected):
    duplicate = label != "unique"
    return {
        "case": label, "entry_count": 2, "distinct_entry_objects": True,
        "write_warnings": ([{"category": "UserWarning",
                             "message": "Duplicate name: 'weapons/rifle.json'"}]
                           if duplicate else []),
        "read_warnings": [], "duplicates": [N] if duplicate else [],
        "project_decision": "reject" if duplicate else "accept",
        "rows": [{"ordinal": i, "name": names[i],
                  "metadata_size": len(payloads[i].encode("utf-8")),
                  "name_selected_ordinal": selected[i],
                  "by_name": payloads[selected[i]], "by_entry": payloads[i],
                  "by_name_size": len(payloads[selected[i]].encode("utf-8")),
                  "by_entry_size": len(payloads[i].encode("utf-8"))}
                 for i in range(2)],
    }


EXPECTED = [
    expected_case("unique", [N, M], [A, B], [0, 1]),
    expected_case("duplicate_ab", [N, N], [A, B], [1, 1]),
    expected_case("duplicate_ba", [N, N], [B, A], [1, 1]),
    expected_case("duplicate_aa", [N, N], [A, A], [1, 1]),
]


def atomic_write(path, value):
    temporary = path.with_suffix(".json.tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    os.replace(temporary, path)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("run", choices=["run1", "run2"])
    args = parser.parse_args()
    # Nothing executes or overwrites prior observations until all hashes match.
    freeze = json.loads((ROOT / "FREEZE.json").read_text())
    if freeze.get("decision") != "approved":
        raise SystemExit("Protocol is not approved")
    names = ("PROTOCOL.md", "probe.py", "run_probe.py")
    if set(freeze.get("sha256", {})) != set(names):
        raise SystemExit("Incomplete freeze")
    for name in names:
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != freeze["sha256"][name]:
            raise SystemExit("Freeze mismatch")
    out = ROOT / (args.run + ".json")
    # Discard only this runner's prior same-label result and incomplete write.
    out.unlink(missing_ok=True)
    out.with_suffix(".json.tmp").unlink(missing_ok=True)
    result = {"schema": 1, "run": args.run, "status": "runner_error",
              "input_sha256": dict(freeze["sha256"])}
    try:
        with tempfile.TemporaryDirectory(prefix="zip-entry-probe-") as temp:
            env = {"HOME": temp, "XDG_CONFIG_HOME": temp,
                   "XDG_CACHE_HOME": temp, "XDG_DATA_HOME": temp,
                   "TMPDIR": temp, "PYTHONDONTWRITEBYTECODE": "1"}
            with tempfile.TemporaryFile() as stdout, tempfile.TemporaryFile() as stderr:
                completed = subprocess.run(
                    [sys.executable, "-I", "-B", str(ROOT / "probe.py")],
                    cwd=temp, env=env, stdin=subprocess.DEVNULL,
                    stdout=stdout, stderr=stderr, timeout=10, check=False)
                if stdout.tell() > 65536 or stderr.tell() > 65536:
                    result.update(status="runner_error", reason="output_limit")
                else:
                    stdout.seek(0)
                    stderr.seek(0)
                    raw, error = stdout.read(), stderr.read()
                    if completed.returncode != 0 or error:
                        result.update(status="probe_error", reason="nonzero_exit_or_stderr")
                    else:
                        data = json.loads(raw)
                        result["observation"] = data
                        if data.get("python") != [3, 12, 14]:
                            result.update(status="environment_mismatch")
                        elif data != {"schema": 1, "status": "observed",
                                     "python": [3, 12, 14], "cases": EXPECTED}:
                            result.update(status="functional_mismatch")
                        else:
                            result.update(status="pass")
    except subprocess.TimeoutExpired:
        result.update(status="runner_error", reason="timeout")
    except Exception as exc:
        result.update(status="runner_error", reason=type(exc).__name__)
    atomic_write(out, result)
    print(json.dumps({"run": args.run, "status": result["status"]}))
    return 0 if result["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
