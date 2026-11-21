import bpy, json, math, statistics
bpy.ops.wm.read_factory_settings(use_empty=True)
s=bpy.context.scene
s.render.engine='CYCLES'
s.cycles.device='CPU'
s.cycles.samples=16
s.cycles.seed=4
s.cycles.use_adaptive_sampling=False
s.cycles.use_denoising=False
s.render.threads_mode='FIXED'
s.render.threads=2
s.world=bpy.data.worlds.new("Black")
s.world.use_nodes=True
s.world.node_tree.nodes["Background"].inputs["Strength"].default_value=0
bpy.ops.object.light_add(type='POINT',location=(-.47,-.3,2.0))
light=bpy.context.object
light.data.energy=120
light.data.shadow_soft_size=0
W=128
def build(name, faces, uv_bases, split):
    # Slot x=-1..0 or 0..1; y=-.5.. .5. Both quads geometrically identical across cases.
    verts=[]; vmap={}; polygons=[]
    for i in faces:
        corners=[(i-1,-.5,0),(i,-.5,0),(i,.5,0),(i-1,.5,0)]
        ids=[]
        for c in corners:
            if split or c not in vmap:
                vmap[c]=len(verts)
                verts.append(c)
            ids.append(vmap[c])
        polygons.append(ids)
    mesh=bpy.data.meshes.new(name);mesh.from_pydata(verts,[],polygons);mesh.update()
    obj=bpy.data.objects.new(name,mesh);s.collection.objects.link(obj)
    mesh.materials.append(mat)
    uv=mesh.uv_layers.new(name="Lightmap")
    for p,i in zip(mesh.polygons,faces):
        base=uv_bases[i]
        for li,(u,v) in zip(p.loop_indices,[(0,0),(32,0),(32,32),(0,32)]):
            uv.data[li].uv=((base+u)/W,(48+v)/W)
    return obj
mat=bpy.data.materials.new("Identical opaque white diffuse")
mat.use_nodes=True
n=mat.node_tree.nodes;n.clear()
diff=n.new("ShaderNodeBsdfDiffuse");diff.inputs["Color"].default_value=(1,1,1,1)
out=n.new("ShaderNodeOutputMaterial");mat.node_tree.links.new(diff.outputs[0],out.inputs["Surface"])
tex=n.new("ShaderNodeTexImage");n.active=tex
def bake(name, bases, separate):
    im=bpy.data.images.new(name,width=W,height=W,float_buffer=True,alpha=True)
    im.colorspace_settings.name='Non-Color'
    tex.image=im
    bpy.ops.object.select_all(action='DESELECT')
    objects=[build(name+str(i),[i],bases,True) for i in (0,1)] if separate else [build(name,[0,1],bases,bases==(16,80))]
    for obj in objects: obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    ret=bpy.ops.object.bake(type='DIFFUSE',pass_filter={'DIRECT'},margin=8,margin_type='EXTEND',use_clear=True)
    assert ret=={'FINISHED'}, ret
    values=list(im.pixels)
    def pixel(x,y):return values[(y*W+x)*4]
    patches=[[pixel(base+x,48+y) for y in range(32) for x in range(32)] for base in bases]
    assert all(min(p)>0.05 and max(p)<100 for p in patches), [(min(p),max(p)) for p in patches]
    assert all(max(p)-min(p)>0.01 for p in patches)
    bg=max(pixel(i,0) for i in range(W)); assert bg==0,bg
    for obj in objects: bpy.data.objects.remove(obj,do_unlink=True)
    return patches
a=bake('joined_continuous_uv',(32,64),False)
b=bake('split_segmented_uv',(16,80),True)
c=bake('joined_segmented_uv',(16,80),False)
def summary(p):
    center=[(p[0][y*32+31],p[1][y*32]) for y in range(32)]
    return {"covered_core_texels":[sum(v>0.05 for v in q) for q in p],"core_min_max":[[min(q),max(q)] for q in p],
       "center_row_last2_left_first2_right":p[0][16*32+30:16*32+32]+p[1][16*32:16*32+2],
       "mean_abs_raw_neighbor_difference":statistics.mean(abs(x-y) for x,y in center)}
def compare(x,y):
    diff=[b-a for p,q in zip(x,y) for a,b in zip(p,q)]
    join_diff=[(y[1][r*32]-y[0][r*32+31])-(x[1][r*32]-x[0][r*32+31]) for r in range(32)]
    return {"max_abs_matched_core":max(map(abs,diff)),"mean_abs_matched_core":statistics.mean(map(abs,diff)),
      "max_abs_edge_jump_excess_over_joined":max(map(abs,join_diff))}
print("RESULT "+json.dumps({"blender":bpy.app.version_string,"device":"Cycles CPU","size":[W,W],"texels_per_unit":32,
"margin":8,"samples":16,"diffuse_bake":"DIRECT only","seed":4,"world":"black","joined":summary(a),"split":summary(b),
"joined_segmented":summary(c),"split_vs_joined":compare(a,b),"joined_segmented_vs_joined":compare(a,c),
"split_vs_joined_segmented_same_packing":compare(c,b),"split_same_packing_identical_samples": b==c},sort_keys=True))
