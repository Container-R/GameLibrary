extends SceneTree

func clip(offset: float, speed: float) -> Animation:
	var a := Animation.new()
	a.length = 2.0
	var track := a.add_track(Animation.TYPE_POSITION_3D)
	a.track_set_path(track, NodePath("Actor"))
	a.position_track_insert_key(track, 0.0, Vector3(offset, 0, 0))
	a.position_track_insert_key(track, 2.0, Vector3(offset + 2.0 * speed, 0, 0))
	return a

func _initialize() -> void:
	run_probe.call_deferred()

func run_probe() -> void:
	var results := {
		"offset_8_equal_speed": series(8.0, 1.0),
		"offset_0_equal_speed": series(0.0, 1.0),
		"offset_0_unequal_speed": series(0.0, 2.0)
	}
	var valid := absf(results["offset_8_equal_speed"][1]["position_difference_x"] - 2.1) < 0.00001
	valid = valid and absf(results["offset_8_equal_speed"][1]["root_motion_delta_x"] - 0.1) < 0.00001
	valid = valid and absf(results["offset_0_equal_speed"][1]["position_difference_x"] - 0.1) < 0.00001
	valid = valid and absf(results["offset_0_unequal_speed"][1]["position_difference_x"] - 0.175) < 0.00001
	valid = valid and absf(results["offset_0_unequal_speed"][1]["root_motion_delta_x"] - 0.125) < 0.00001
	print(JSON.stringify(results, "  "))
	quit(0 if valid else 1)

func series(b_offset: float, b_speed: float) -> Array:
	var rig := Node3D.new()
	rig.name = "Rig"
	root.add_child(rig)
	var actor := Node3D.new()
	actor.name = "Actor"
	rig.add_child(actor)
	var player := AnimationPlayer.new()
	player.name = "Player"
	rig.add_child(player)
	var lib := AnimationLibrary.new()
	lib.add_animation("a", clip(0.0, 1.0))
	lib.add_animation("b", clip(b_offset, b_speed))
	player.add_animation_library("", lib)
	var tree := AnimationTree.new()
	tree.name = "Mixer"
	tree.active = false
	rig.add_child(tree)
	tree.anim_player = NodePath("../Player")
	tree.root_node = NodePath("..")
	tree.root_motion_track = NodePath("Actor")
	tree.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	var graph := AnimationNodeBlendTree.new()
	var an := AnimationNodeAnimation.new()
	var bn := AnimationNodeAnimation.new()
	an.animation = &"a"
	bn.animation = &"b"
	graph.add_node("A", an)
	graph.add_node("B", bn)
	var mix := AnimationNodeBlend2.new()
	mix.sync = true
	graph.add_node("Mix", mix)
	graph.connect_node("Mix", 0, "A")
	graph.connect_node("Mix", 1, "B")
	graph.connect_node("output", 0, "Mix")
	tree.tree_root = graph
	tree.set("parameters/Mix/blend_amount", 0.0)
	tree.active = true
	tree.advance(0.0)
	tree.advance(0.1)
	var previous := tree.get_root_motion_position_accumulator().x
	var rows: Array = []
	for w: float in [0.0, 0.25, 0.5, 0.75, 1.0, 1.0]:
		tree.set("parameters/Mix/blend_amount", w)
		tree.advance(0.1)
		var p := tree.get_root_motion_position_accumulator().x
		var delta := tree.get_root_motion_position().x
		rows.append({
			"weight_b": w,
			"blended_position_x": snappedf(p, 0.000001),
			"position_difference_x": snappedf(p-previous, 0.000001),
			"root_motion_delta_x": snappedf(delta, 0.000001)
		})
		previous = p
	rig.queue_free()
	return rows
