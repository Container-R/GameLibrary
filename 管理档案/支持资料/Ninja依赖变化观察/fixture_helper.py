#!/usr/bin/env python3
"""Original finite byte-copy fixture, not a game asset compiler."""
import hashlib
import json
import sys
from pathlib import Path


def event(record):
    with Path("events.jsonl").open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")
        stream.flush()


def main():
    if len(sys.argv) != 2 or sys.argv[1] not in ("generate", "bundle"):
        raise SystemExit("expected generate or bundle")
    op = sys.argv[1]
    source, output = {
        "generate": ("recipe.txt", "generated.txt"),
        "bundle": ("generated.txt", "bundle.txt"),
    }[op]
    event({"event": "begin", "operation": op})
    content = Path(source).read_bytes()
    if content not in (b"asset-version=A\n", b"asset-version=B\n"):
        raise ValueError("unexpected synthetic recipe bytes")
    Path(output).write_bytes(content)
    actual = Path(output).read_bytes()
    if actual != content:
        raise ValueError("copy verification failed")
    event({"event": "finish", "operation": op,
           "source_sha256": hashlib.sha256(content).hexdigest(),
           "output_sha256": hashlib.sha256(actual).hexdigest()})


if __name__ == "__main__":
    main()
