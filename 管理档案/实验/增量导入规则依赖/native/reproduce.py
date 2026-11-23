"""Run with python3 reproduce.py (GNU Make and Pillow required)."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from PIL import Image, __version__

HERE = Path(__file__).resolve().parent


def put(path, n):
    path.write_text(json.dumps({"max_side": n}))


def run(mode, cold=False):
    with tempfile.TemporaryDirectory() as td:
        p = Path(td)
        for name in ("Makefile", "asset.py"):
            shutil.copyfile(HERE / name, p / name)
        rules = p / "rules"
        rules.mkdir()
        base = rules / "base.json"
        override = rules / "handheld.json"
        put(base, 256)
        Image.new("RGB", (1024, 768), "#345678").save(p / "sprite.png")
        (p / "audio.bin").write_bytes(b"unrelated audio-control bytes")
        if cold:
            put(override, 1024)
        unchanged = {f: f.read_bytes() for f in (base, p / "sprite.png", p / "audio.bin")}
        control_mtime = None

        def make(label, expected_width, expect_sprite, expect_audio):
            nonlocal control_mtime
            if mode == "fixed":
                subprocess.run([sys.executable, "asset.py", "resolve"], cwd=p, check=True)
            dep = "effective.json" if mode == "fixed" else "rules/base.json"
            out = subprocess.check_output(["make", "--no-print-directory", f"RULE_DEP={dep}"], cwd=p, text=True)
            sprite, audio = "BUILD sprite" in out, "BUILD audio" in out
            assert (sprite, audio) == (expect_sprite, expect_audio), out
            with Image.open(p / "out/sprite.png") as image:
                width, height = image.size
            assert (width, height) == (expected_width, expected_width * 3 // 4)
            control = p / "out/audio.bin"
            assert all(f.read_bytes() == data for f, data in unchanged.items())
            assert control.read_bytes() == unchanged[p / "audio.bin"]
            actual_mtime = control.stat().st_mtime_ns
            assert control_mtime is None or actual_mtime == control_mtime
            control_mtime = actual_mtime
            print(f"{mode:6} {label:18} {width}x{height} sprite={'ran' if sprite else 'skipped'} audio={'ran' if audio else 'skipped'}")

        if cold:
            make("cold+override", 1024, True, True)
            return
        make("cold", 256, True, True)
        make("warm", 256, False, False)
        put(override, 1024)
        make("add override", 1024 if mode == "fixed" else 256, mode == "fixed", False)
        make("warm+override", 1024 if mode == "fixed" else 256, False, False)
        override.unlink()
        make("remove override", 256, mode == "fixed", False)
        make("warm again", 256, False, False)


if __name__ == "__main__":
    version = subprocess.check_output(["make", "--version"], text=True).splitlines()[0]
    print(f"{version}, Pillow {__version__}")
    run("broken")
    run("broken", cold=True)
    run("fixed")
