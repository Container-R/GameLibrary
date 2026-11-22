"""Export a small authored fixture twice and show what actually survived."""
from pathlib import Path
import json
import sys
import bpy

output = Path(sys.argv[sys.argv.index("--") + 1])
output.mkdir(parents=True, exist_ok=True)
bpy.ops.wm.read_factory_settings(use_empty=True)
asset_key = "gamelibrary_source_id"

def slot(n):
    return f"80a06da0-efde-4550-a0af-{n:012d}"

def material(name, serial, color):
    m = bpy.data.materials.new(name)
    m[asset_key] = slot(serial)
    m.diffuse_color = color + (1.0,)
    return m

def triangle(name, x, mat):
    me = bpy.data.meshes.new(name+"Mesh")
    me.from_pydata([(x,0,0),(x+0.9,0,0),(x,0.9,0)], [], [(0,1,2)])
    me.update()
    ob = bpy.data.objects.new(name,me)
    bpy.context.collection.objects.link(ob)
    me.materials.append(mat)
    return ob

metal = material("Metal",1,(0.4,0.4,0.4))
glass = material("Glass",2,(0.2,0.3,0.7))
latch = material("Latch",3,(0.8,0.4,0.2))
rail = triangle("A Rail",0,metal)
window = triangle("B Window",1,glass)
door = triangle("C Side Door",2,latch)

def snapshot(filename, extras):
    path = output / filename
    result = bpy.ops.export_scene.gltf(filepath=str(path),export_format="GLTF_SEPARATE",export_extras=extras,export_animations=False)
    assert result == {"FINISHED"}
    js = json.loads(path.read_text())
    return [
        {"index": i,"name":m["name"],"source_id":m.get("extras",{}).get(asset_key)}
        for i,m in enumerate(js["materials"])
    ]

before = snapshot("before.gltf",True)
metal.name="Exterior Metal"
metal.diffuse_color=(0.5,0.45,0.4,1.0)
bpy.data.objects.remove(door,do_unlink=True)
bpy.data.materials.remove(latch)
clip = material("Latch",4,(0.1,0.8,0.2))
triangle("C Window Clip",2,clip)
rail.name="Z Rail"
bpy.context.collection.objects.unlink(rail)
bpy.context.collection.objects.link(rail)
after = snapshot("after.gltf",True)
without_extras = snapshot("after-no-extras.gltf",False)

by_id = lambda rows: {m["source_id"]:m for m in rows}
prev, following = by_id(before),by_id(after)
assert prev[slot(1)]["name"] == "Metal" and following[slot(1)]["name"] == "Exterior Metal"
assert slot(3) in prev and slot(3) not in following
assert following[slot(4)]["name"] == "Latch"
assert all(m["source_id"] is None for m in without_extras)
(output / "blender.observed.json").write_text(json.dumps({"blender":bpy.app.version_string,"before":before,"after":after,"without_extras":without_extras},indent=2)+"\n")
