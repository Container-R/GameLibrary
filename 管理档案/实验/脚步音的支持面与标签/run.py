"""Reproduce Jolt ray results with two independently booted Godot projects."""
import json
import os
from pathlib import Path
from shutil import copyfile
from subprocess import run
from tempfile import TemporaryDirectory

source = Path(__file__).with_name("probe.gd")
engine = os.environ.get("GODOT_BIN", "godot")
with TemporaryDirectory() as temporary:
    root = Path(temporary)
    cache = root / "cache"
    cache.mkdir()
    env = dict(os.environ, XDG_CACHE_HOME=str(cache),
               XDG_CONFIG_HOME=str(root / "config"), XDG_DATA_HOME=str(root / "data"))
    def execute(args):
        p = run([engine, *args], env=env, capture_output=True, text=True, timeout=60)
        assert p.returncode == 0, p.stdout + p.stderr
        assert "ERROR:" not in p.stderr, p.stderr
        return p.stdout.strip()
    data = {"godot_version": execute(["--version"])}
    for enabled in (False,True):
        project = root / ("enabled" if enabled else "default")
        project.mkdir()
        (project / "project.godot").write_text(
            'config_version=5\n[application]\nconfig/name="Footstep Ray Probe"\n'
            '[physics]\n3d/physics_engine="Jolt Physics"\n' +
            ('jolt_physics_3d/queries/enable_ray_cast_face_index=true\n' if enabled else "") +
            '[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
        copyfile(source, project/"probe.gd")
        stdout = execute(["--headless","--path",str(project),"--script","probe.gd","--quit-after","180"])
        rows = [line.removeprefix("RESULT ") for line in stdout.splitlines() if line.startswith("RESULT ")]
        assert len(rows) == 1, stdout
        result = json.loads(rows[0])
        assert result["face_index_setting"] is enabled, result
        assert result["physics_engine_setting"] == "Jolt Physics", result
        for key, worlds in (("initial",[-0.2,0.2]),("translated",[2.8,3.2])):
            hits=result[key]
            assert [x["collider"] for x in hits] == ["Floor","Floor"], result
            assert [x["shape_slot"] for x in hits] == [0,0], result
            assert [x["world_x"] for x in hits] == worlds, result
            assert [x["world_y"] for x in hits] == [0,0], result
            assert [x["local_x"] for x in hits] == [-0.2,0.2], result
            assert [x["material"] for x in hits] == ["stone","soil"], result
        a,b=([x["face_index"] for x in result[k]] for k in ("initial","translated"))
        assert a == b, result
        assert (len(set(a)) == 2 and all(0 <= i < 4 for i in a)) if enabled else a == [-1,-1], result
        assert [x["collider"] for x in result["support"]] == ["Floor","Wood","Trigger"], result
        assert [x["world_y"] for x in result["support"]] == [0,0.25,0.65], result
        data["explicit_face_index" if enabled else "default"] = result
print(json.dumps(data, indent=2))
