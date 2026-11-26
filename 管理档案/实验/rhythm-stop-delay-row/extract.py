"""Generate a temporary C++ include from a pinned upstream file users supply."""
import hashlib
import sys
from pathlib import Path

source = Path(sys.argv[1]).read_bytes()
assert hashlib.sha256(source).hexdigest() == "58d181ab179812c0f75f5d5bd2c1f19f7230b56963b430e3251f6746908c3a4f"
lines = source.decode("utf-8").splitlines(keepends=True)
# Upstream 1-based ranges: event enum and selection, elapsed->beat,
# and beat->elapsed. No lookup, file parser, globals, or game loop.
text = "".join(lines[761:914] + lines[928:993])
Path(sys.argv[2]).write_text(text, encoding="utf-8")
