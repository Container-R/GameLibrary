extends SceneTree

func add_clip() -> Animation:
	var a := Animation.new()
	a.length = 2.0
	a.loop_mode = Animation.LOOP_LINEAR
	var p := a.add_track(Animation.TYPE_POSITION_3D)
	a.track_set_path(p, NodePath("Skeleton:root"))
	a.track_set_interpolation_loop_wrap(p, false)
	# Nonzero beginning catches replacing the tail with the endpoint itself.
	a.position_track_insert_key(p, 0.0, Vector3(10, 0, 0))
	a.position_track_insert_key(p, 2.0, Vector3(14, 0, 0))
	return a

func at(tree: AnimationTree, seconds: float) -> Array:
	tree.advance(seconds)
	return [snappedf(tree.get_root_motion_position().x, 0.00001),
		snappedf(tree.get_root_motion_position_accumulator().x, 0.00001)]

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var actor := Node3D.new()
	root.add_child(actor)
	var skeleton := Skeleton3D.new()
	skeleton.name = &"Skeleton"
	actor.add_child(skeleton)
	skeleton.add_bone("root")
	skeleton.set_bone_rest(0, Transform3D.IDENTITY)
	skeleton.reset_bone_poses()
	var library := AnimationLibrary.new()
	library.add_animation("motion", add_clip())
	var player := AnimationPlayer.new()
	player.name = &"Player"
	player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	actor.add_child(player)
	player.add_animation_library("", library)
	var tree := AnimationTree.new()
	tree.name = &"Tree"
	tree.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	actor.add_child(tree)
	tree.anim_player = NodePath("../Player")
	var node := AnimationNodeAnimation.new()
	node.animation = &"motion"
	tree.tree_root = node
	tree.root_motion_local = false
	tree.root_motion_track = NodePath("Skeleton:root")
	tree.active = true
	at(tree, 0.0)
	var before := at(tree, 1.75)
	var wrap := at(tree, 0.5)
	var after := at(tree, 0.25)
	var exact_end := at(tree, 1.5)
	var next_tick := at(tree, 0.25)
	var partitioned := OS.get_cmdline_user_args().has("partitioned")
	var hitch_steps: Array = [0.25, 1.75, 0.25, 1.75, 0.5] if partitioned else [4.5]
	var hitch_total := 0.0
	var hitch_last: Array = []
	for dt: float in hitch_steps:
		hitch_last = at(tree, dt)
		hitch_total += hitch_last[0]
	print("RESULT=" + JSON.stringify({"engine": Engine.get_version_info().string,
		"before": before, "one_wrap": wrap, "after": after,
		"exact_end": exact_end, "next_tick": next_tick, "hitch_total": hitch_total, "hitch_last": hitch_last, "hitch_steps": hitch_steps,
		"difference_of_sampled_accumulators": wrap[1] - before[1]}))
	quit(0)
