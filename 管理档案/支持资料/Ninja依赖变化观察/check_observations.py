#!/usr/bin/env python3
"""Check published records only. Never invoke Ninja, helper, compiler or network."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
A = b"asset-version=A\n"
B = b"asset-version=B\n"
NAMES = ("recipe.txt", "generated.txt", "bundle.txt")
PHASES = ("initial", "unchanged", "changed", "settled")
PACK_FILES = {"README.md", "fixture_helper.py", "recipe-v1.txt", "recipe-v2.txt",
              "implicit.ninja", "order_only.ninja", "observations.json", "check_observations.py"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def manifest_check():
    manifest = json.loads((ROOT / "artifact-manifest.json").read_text())
    require({e["path"] for e in manifest["files"]} == PACK_FILES, "manifest file set")
    require(len(manifest["files"]) == len(PACK_FILES), "duplicate manifest entry")
    for entry in manifest["files"]:
        data = (ROOT / entry["path"]).read_bytes()
        require(len(data) == entry["size"], "artifact size: " + entry["path"])
        require(hashlib.sha256(data).hexdigest() == entry["sha256"], "artifact hash: " + entry["path"])


def snapshot_check(snapshot):
    require(set(snapshot) == set(NAMES), "snapshot filenames")
    for value in snapshot.values():
        if value is None:
            continue
        require(set(value) == {"bytes_hex", "sha256", "size", "mtime_offset_ns"}, "snapshot fields")
        data = bytes.fromhex(value["bytes_hex"])
        require(data in (A, B), "unexpected content")
        require(value["size"] == len(data), "content size")
        require(value["sha256"] == hashlib.sha256(data).hexdigest(), "content digest")
        require(type(value["mtime_offset_ns"]) is int and value["mtime_offset_ns"] >= 0,
                "relative mtime")


def check(record):
    require(record["schema_version"] == 1, "schema version")
    phases = record["phases"]
    order = [(r, a, p) for r in (1, 2) for a in ("implicit", "order_only") for p in PHASES]
    require([(x["repeat"], x["arm"], x["phase"]) for x in phases] == order, "16-phase order")
    begins = finishes = 0
    for repeat in (1, 2):
        for arm in ("implicit", "order_only"):
            rows = [x for x in phases if x["repeat"] == repeat and x["arm"] == arm]
            prior = None
            arm_begins = 0
            for row in rows:
                phase = row["phase"]
                require(row["process_exit_code"] == 0, "native process did not exit zero")
                before, after = row["before"], row["after"]
                snapshot_check(before)
                snapshot_check(after)
                current = A if phase in ("initial", "unchanged") else B
                ops = ["generate", "bundle"] if phase == "initial" else (
                    (["generate", "bundle"] if arm == "implicit" else ["generate"])
                    if phase == "changed" else [])
                final = A if arm == "order_only" else current
                require([after[n]["bytes_hex"] for n in NAMES] ==
                        [current.hex(), current.hex(), final.hex()], "phase byte oracle")
                require(after["recipe.txt"] == before["recipe.txt"], "recipe changed during call")
                events = row["helper_events"]
                require([(e["event"], e["operation"]) for e in events] ==
                        [(kind, op) for op in ops for kind in ("begin", "finish")], "helper event oracle")
                for event in events:
                    if event["event"] == "begin":
                        require(set(event) == {"event", "operation"}, "begin fields")
                        begins += 1
                        arm_begins += 1
                    else:
                        require(set(event) == {"event", "operation", "source_sha256", "output_sha256"},
                                "finish fields")
                        expected_hash = hashlib.sha256(current).hexdigest()
                        require(event["source_sha256"] == event["output_sha256"] == expected_hash,
                                "helper digest oracle")
                        finishes += 1
                if phase == "initial":
                    require(before["recipe.txt"]["bytes_hex"] == A.hex(), "initial input")
                    require(before["recipe.txt"]["mtime_offset_ns"] == 0, "mtime origin")
                    require(before["generated.txt"] is None and before["bundle.txt"] is None,
                            "initial outputs existed")
                elif phase == "changed":
                    require(before["recipe.txt"]["bytes_hex"] == B.hex(), "changed input")
                    for name in ("generated.txt", "bundle.txt"):
                        require(before[name] == prior[name], "old output changed before call")
                        require(before["recipe.txt"]["mtime_offset_ns"] > before[name]["mtime_offset_ns"],
                                "changed input not strictly newer")
                    if arm == "order_only":
                        require(after["bundle.txt"] == before["bundle.txt"], "stale bundle not preserved")
                else:
                    require(before == prior and after == before, "no-op changed file snapshot")
                if ops:
                    require(after["generated.txt"]["mtime_offset_ns"] >= after["recipe.txt"]["mtime_offset_ns"],
                            "generated mtime predates recipe")
                    if "bundle" in ops:
                        require(after["bundle.txt"]["mtime_offset_ns"] >= after["generated.txt"]["mtime_offset_ns"],
                                "bundle mtime predates generated")
                prior = after
            require(arm_begins == (4 if arm == "implicit" else 3), "per-arm count")
    require(begins == finishes == 14, "total event count")
    require(record["summary"] == {"repeats": 2, "fixture_calls": 16,
            "helper_begins": 14, "helper_finishes": 14}, "summary count")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--record", type=Path, default=ROOT / "observations.json")
    args = parser.parse_args()
    manifest_check()
    check(json.loads(args.record.read_text()))
    print("Record checks matched: 16 phases, 14 helper begins and 14 finishes. No native build was run.")


if __name__ == "__main__":
    main()
