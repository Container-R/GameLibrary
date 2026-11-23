"""Tiny local asset transform; no artifact-cache service."""
import json
import sys
from pathlib import Path
from PIL import Image

BASE = Path("rules/base.json")
PLATFORM = Path("rules/handheld.json")
MANIFEST = Path("effective.json")


def resolve():
    chosen = PLATFORM if PLATFORM.is_file() else BASE
    # Read selected input once, materialize the exact relevant setting.
    snapshot = json.dumps({"max_side": json.loads(chosen.read_bytes())["max_side"]}) + "\n"
    if not MANIFEST.exists() or MANIFEST.read_text() != snapshot:
        tmp = MANIFEST.with_suffix(".tmp")
        tmp.write_text(snapshot)
        tmp.replace(MANIFEST)


def render(rule_dep):
    # The broken scheduler declaration tracks BASE, although this branch reads
    # from PLATFORM when available. The fixed version reads the declared snapshot.
    selected = MANIFEST if rule_dep == MANIFEST else (PLATFORM if PLATFORM.is_file() else BASE)
    size = json.loads(selected.read_bytes())["max_side"]
    output = Path("out/sprite.png")
    output.parent.mkdir(exist_ok=True)
    with Image.open("sprite.png") as image:
        image.thumbnail((size, size), Image.Resampling.NEAREST)
        image.save(output)
    print("BUILD sprite")


if __name__ == "__main__":
    if sys.argv[1] == "resolve":
        resolve()
    else:
        render(Path(sys.argv[2]))
