extends SceneTree
const ENABLE = "physics/jolt_physics_3d/queries/enable_ray_cast_face_index"

func box_node(node: CollisionObject3D, pos: Vector3, size: Vector3) -> void:
	var col := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = size
	col.shape = box
	node.add_child(col)
	root.add_child(node)
	node.position = pos

func ray(x: float, areas: bool = false) -> Dictionary:
	var q := PhysicsRayQueryParameters3D.create(Vector3(x, 1, -0.25), Vector3(x, -1, -0.25))
	q.collide_with_areas = areas
	var hit := root.world_3d.direct_space_state.intersect_ray(q)
	if hit.is_empty():
		return {}
	var collider: Node3D = hit.collider
	var pt: Vector3 = hit.position
	var local: Vector3 = collider.to_local(pt)
	return {"collider": str(collider.name), "shape_slot": hit.shape, "face_index": hit.face_index,
			"world_x": snappedf(pt.x, 0.001), "world_y": snappedf(pt.y, 0.001),
			"local_x": snappedf(local.x, 0.001),
			"material": ("stone" if local.x < 0 else "soil") if collider.name == &"Floor" else str(collider.name)}

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var body := StaticBody3D.new()
	body.name = "Floor"
	var vertices := PackedVector3Array()
	for edge in [-1.0, 0.0]:
		var a := Vector3(edge,0,-1)
		var b := Vector3(edge+1.0,0,-1)
		var c := Vector3(edge+1.0,0,1)
		var d := Vector3(edge,0,1)
		vertices.append_array(PackedVector3Array([a,b,c,a,c,d]))
	var concave := ConcavePolygonShape3D.new()
	concave.set_faces(vertices)
	concave.backface_collision = true
	var col := CollisionShape3D.new()
	col.shape = concave
	body.add_child(col)
	root.add_child(body)
	for _i in range(3):
		await physics_frame
	var initial := [ray(-0.2),ray(0.2)]
	body.position.x = 3
	for _i in range(3):
		await physics_frame
	var translated := [ray(2.8),ray(3.2)]
	var area := Area3D.new()
	area.name = "Trigger"
	box_node(area,Vector3(2.8,0.60,-0.25),Vector3(0.3,0.1,0.3))
	var plank := StaticBody3D.new()
	plank.name = "Wood"
	box_node(plank,Vector3(3.2,0.20,-0.25),Vector3(0.3,0.1,0.3))
	for _i in range(3):
		await physics_frame
	var support := [ray(2.8),ray(3.2),ray(2.8,true)]
	print("RESULT ",JSON.stringify({"face_index_setting":ProjectSettings.get_setting(ENABLE),
			"physics_engine_setting":ProjectSettings.get_setting("physics/3d/physics_engine"),"initial":initial,"translated":translated,"support":support}))
	quit()
