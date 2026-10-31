extends SceneTree

var sk: Skeleton3D
var mods: Array[LookAtModifier3D] = []
var targets: Array[Node3D] = []
var trace: Array = []
var evaluations: Array = []
var phase := "setup"
var index := -1
var stages: Array = []
var current: Dictionary = {}
var finished := false

func vec(v: Vector3) -> Array:
	return [v.x, v.y, v.z]

func transform(t: Transform3D) -> Dictionary:
	return {"origin":vec(t.origin), "basis":[vec(t.basis.x),vec(t.basis.y),vec(t.basis.z)]}

func pose() -> Array:
	var out: Array = []
	for i in range(2):
		out.append({"local":transform(sk.get_bone_pose(i)), "global":transform(sk.get_bone_global_pose(i))})
	return out

func settings(m: LookAtModifier3D) -> Dictionary:
	return {"id":m.get_instance_id(), "bone":m.bone, "bone_name":m.bone_name,
		"target_path":str(m.target_node), "target_id":m.get_node(m.target_node).get_instance_id(),
		"forward_axis":m.forward_axis,"primary_rotation_axis":m.primary_rotation_axis,
		"relative":m.relative,"origin_from":m.origin_from,"origin_offset":vec(m.origin_offset),
		"duration":m.duration,"influence":m.influence,"active":m.active,
		"use_angle_limitation":m.use_angle_limitation,"use_secondary_rotation":m.use_secondary_rotation,
		"origin_safe_margin":m.origin_safe_margin,"interpolating":m.is_interpolating(),
		"interpolation_remaining":m.get_interpolation_remaining()}

func snapshot() -> Dictionary:
	var children: Array = []
	for n in sk.get_children():
		children.append({"id":n.get_instance_id(),"name":str(n.name)})
	var bindings: Array = []
	for m in mods:
		bindings.append(settings(m))
	var ts: Array = []
	for t in targets:
		ts.append({"id":t.get_instance_id(),"world":transform(t.global_transform)})
	var bones: Array = []
	for i in range(2):
		bones.append({"name":sk.get_bone_name(i),"parent":sk.get_bone_parent(i),"rest":transform(sk.get_bone_rest(i))})
	return {"skeleton_id":sk.get_instance_id(),"world":transform(sk.global_transform),
		"callback_mode":sk.modifier_callback_mode_process,"interpolation_mode":sk.physics_interpolation_mode,
		"children":children,"modifiers":bindings,"targets":ts,"bones":bones,"poses":pose()}

func _initialize() -> void:
	call_deferred("build")

func build() -> void:
	create_timer(10.0).timeout.connect(func():
		if not finished:
			print("WATCHDOG_JSON="+JSON.stringify({"phase":phase,"trace":trace,"evaluations":evaluations}))
			quit(2))
	var host := Node3D.new()
	host.name = "Host"
	host.physics_interpolation_mode = Node.PHYSICS_INTERPOLATION_MODE_OFF
	sk = Skeleton3D.new()
	sk.name = "Skeleton"
	sk.modifier_callback_mode_process = Skeleton3D.MODIFIER_CALLBACK_MODE_PROCESS_MANUAL
	sk.physics_interpolation_mode = Node.PHYSICS_INTERPOLATION_MODE_OFF
	sk.add_bone("P")
	sk.add_bone("C")
	sk.set_bone_parent(1,0)
	sk.set_bone_rest(0,Transform3D.IDENTITY)
	sk.set_bone_rest(1,Transform3D(Basis.IDENTITY,Vector3(0,1,0)))
	sk.reset_bone_poses()
	host.add_child(sk)
	for i in range(2):
		var t := Node3D.new()
		t.name = "TargetP" if i == 0 else "TargetC"
		t.position = Vector3(10,0,0) if i == 0 else Vector3(0,1,10)
		host.add_child(t)
		targets.append(t)
		var m := LookAtModifier3D.new()
		m.name = "P" if i == 0 else "C"
		m.forward_axis = 4
		m.primary_rotation_axis = Vector3.AXIS_Y
		m.relative = false
		m.origin_from = LookAtModifier3D.ORIGIN_FROM_SELF
		m.origin_offset = Vector3.ZERO
		m.duration = 0.0
		m.influence = 1.0
		m.active = true
		m.use_angle_limitation = false
		m.use_secondary_rotation = true
		m.origin_safe_margin = 0.1
		sk.add_child(m)
		m.bone_name = "P" if i == 0 else "C"
		m.target_node = NodePath("../../TargetP" if i == 0 else "../../TargetC")
		m.modification_processed.connect(stage.bind(i))
		mods.append(m)
	sk.skeleton_updated.connect(final_pose)
	root.add_child(host)
	call_deferred("arm",0)

func stage(i: int) -> void:
	var e := {"kind":"stage","phase":phase,"evaluation":index,"emitter":mods[i].get_instance_id(),"bone":i,"poses":pose()}
	trace.append(e)
	if phase == "armed":
		stages.append(e)
	elif phase != "setup" and phase != "reconfigure":
		fail("unexpected stage")

func final_pose() -> void:
	var e := {"kind":"skeleton_updated","phase":phase,"evaluation":index,"poses":pose()}
	trace.append(e)
	if phase == "armed":
		if stages.size() != 2:
			fail("stage count before final")
			return
		current["stages"] = stages.duplicate(true)
		current["final"] = e
		phase = "await_restore"
		call_deferred("after_restore")
	elif phase != "setup" and phase != "reconfigure":
		fail("unexpected final")

func arm(i: int) -> void:
	index = i
	trace.append({"kind":"drain_marker","phase":phase,"evaluation":index})
	current = {"index":i,"before":snapshot()}
	stages = []
	phase = "armed"
	trace.append({"kind":"advance_call","evaluation":index})
	sk.advance(1.0/60.0)
	trace.append({"kind":"advance_return","evaluation":index})

func after_restore() -> void:
	current["restored"] = snapshot()
	trace.append({"kind":"deferred_restored","evaluation":index,"poses":pose()})
	evaluations.append(current)
	if index == 0:
		phase = "reconfigure"
		sk.reset_bone_poses()
		sk.move_child(mods[1],0)
		call_deferred("arm",1)
	else:
		phase = "done"
		finished = true
		print("RESULT_JSON="+JSON.stringify({"version":Engine.get_version_info(),"evaluations":evaluations,"trace":trace}))
		quit(0)

func fail(reason: String) -> void:
	finished = true
	print("FAILURE_JSON="+JSON.stringify({"reason":reason,"phase":phase,"trace":trace,"evaluations":evaluations}))
	quit(2)
