from pathlib import Path
from tempfile import TemporaryDirectory
from subprocess import run
import json
import os

UID = "uid://bq2lpt4k4dhau"
OTHER = "uid://dn5dov1132y4s"
ORIGINAL = "assets/old.tres"
MOVED = "assets/new.tres"

GRADIENT = '''[gd_resource type="Gradient" format=3 uid="{uid}"]

[resource]
colors = PackedColorArray({rgb}, 1, {rgb}, 1)
'''
RED = (UID,"1, 0, 0")
DECOY = (OTHER,"0, 0, 1")
REF = f'''[gd_resource type="GradientTexture1D" load_steps=2 format=3]

[ext_resource type="Gradient" uid="{UID}" path="res://{ORIGINAL}" id="1"]

[resource]
gradient = ExtResource("1")
'''

GDS = '''extends SceneTree

func _initialize() -> void:
    var id := ResourceUID.text_to_id("''' + UID + '''")
    var mapped := ResourceUID.get_id_path(id) if ResourceUID.has_id(id) else ""
    var dep: Gradient = null
    var tex := ResourceLoader.load("res://probe.tres", "GradientTexture1D") as GradientTexture1D
    if tex != null:
        dep = tex.gradient
    var by_text: Gradient = null
    if ResourceLoader.exists("res://assets/old.tres", "Gradient"):
        by_text = ResourceLoader.load("res://assets/old.tres", "Gradient") as Gradient
    var result := {
        "engine": Engine.get_version_info().string,
        "direct_old_path_marker": by_text.get_color(0).to_html() if by_text != null else "",
        "uid_mapped_path": mapped,
        "texture_exists": tex != null,
        "gradient_exists": dep != null,
        "gradient_path": dep.resource_path if dep != null else "",
        "gradient_marker": dep.get_color(0).to_html() if dep != null else ""
    }
    print("OBSERVED " + JSON.stringify(result))
    quit(0)
'''

def one(files, remove_after_import=None, replace_after_import=False):
    with TemporaryDirectory(prefix="gamelibrary-uid-example-") as base:
        d = Path(base)
        p = d/"project"
        p.mkdir()
        (p/"project.godot").write_text('config_version=5\n\n[application]\nconfig/name="Asset Move Fixture"\n')
        f = p/"probe.tres"
        f.write_text(REF)
        (p/"probe.gd").write_text(GDS)
        for path,(uid,rgb) in files.items():
            dst=p/path
            dst.parent.mkdir(exist_ok=True)
            dst.write_text(GRADIENT.format(uid=uid,rgb=rgb))
        env = dict(os.environ)
        for n in ("CACHE","CONFIG","DATA"):
            x=d/n.lower()
            x.mkdir()
            env[f"XDG_{n}_HOME"]=str(x)
        godot=os.environ.get("GODOT","godot")
        def invoke(*extra):
            cmd = [godot,"--headless","--path",str(p),*extra]
            res = run(cmd,env=env,text=True,capture_output=True,timeout=30)
            if res.returncode:
                raise RuntimeError((res.returncode,res.stdout,res.stderr))
            return res.stdout,res.stderr
        out,err=invoke("--editor","--import")
        assert f.read_text()==REF,"import rewrote probe text"
        if remove_after_import:
            (p/remove_after_import).unlink()
        if replace_after_import:
            uid, rgb = DECOY
            (p/MOVED).write_text(GRADIENT.format(uid=uid,rgb=rgb))
        out,err=invoke("--script","res://probe.gd")
        obs=[l[9:] for l in out.splitlines() if l.startswith("OBSERVED ")]
        assert len(obs)==1, (out,err)
        data=json.loads(obs[0])
        data["warned_invalid_uid"] = "ext_resource, invalid UID" in err
        return data

rows = {
    "same_file_same_uid":one({ORIGINAL:RED}),
    "moved_with_uid":one({MOVED:RED}),
    "missing_uid_path_missing":one({MOVED:DECOY}),
    "missing_uid_path_reused":one({ORIGINAL:DECOY}),
    "uid_and_path_both_resolve":one({MOVED:RED,ORIGINAL:DECOY}),
    "stale_registered_uid_path":one({MOVED:RED,ORIGINAL:DECOY},remove_after_import=MOVED),
    "stale_registered_uid_file_replaced":one({MOVED:RED},replace_after_import=True),
}
assert rows["same_file_same_uid"]["gradient_marker"] == "ff0000ff"
assert rows["moved_with_uid"]["gradient_path"] == "res://assets/new.tres"
assert rows["moved_with_uid"]["direct_old_path_marker"] == ""
assert not rows["missing_uid_path_missing"]["texture_exists"]
assert rows["missing_uid_path_reused"]["gradient_marker"] == "0000ffff"
assert rows["missing_uid_path_reused"]["warned_invalid_uid"]
assert rows["uid_and_path_both_resolve"]["gradient_marker"] == "ff0000ff"
assert rows["uid_and_path_both_resolve"]["direct_old_path_marker"] == "0000ffff"
assert rows["stale_registered_uid_path"]["uid_mapped_path"] == "res://assets/new.tres"
assert not rows["stale_registered_uid_path"]["texture_exists"]
assert not rows["stale_registered_uid_path"]["warned_invalid_uid"]
assert rows["stale_registered_uid_path"]["direct_old_path_marker"] == "0000ffff"
assert rows["stale_registered_uid_file_replaced"]["uid_mapped_path"] == "res://assets/new.tres"
assert rows["stale_registered_uid_file_replaced"]["texture_exists"]
assert rows["stale_registered_uid_file_replaced"]["gradient_marker"] == "0000ffff"
assert not rows["stale_registered_uid_file_replaced"]["warned_invalid_uid"]
print(json.dumps(rows,indent=2))
