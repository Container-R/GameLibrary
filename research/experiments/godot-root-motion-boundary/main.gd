extends SceneTree

func vec(v: Vector3) -> Array:
	return [v.x, v.y, v.z]

func quat(q: Quaternion) -> Array:
	return [q.x, q.y, q.z, q.w]

func pose(n: Node3D) -> Dictionary:
	return {"position": vec(n.position), "rotation": quat(n.quaternion)}

func capture(tree: AnimationTree, skeleton: Skeleton3D, actor: Node3D, label: String) -> Dictionary:
	return {"label": label, "delta_position": vec(tree.get_root_motion_position()),
		"delta_rotation": quat(tree.get_root_motion_rotation()),
		"bone_position": vec(skeleton.get_bone_pose_position(0)),
		"bone_rotation": quat(skeleton.get_bone_pose_rotation(0)), "actor": pose(actor)}

func clip(reset: bool) -> Animation:
	var a := Animation.new()
	a.length = 2.0
	a.loop_mode = Animation.LOOP_NONE
	var p := a.add_track(Animation.TYPE_POSITION_3D)
	a.track_set_path(p, NodePath("Skeleton:root"))
	a.track_set_interpolation_type(p, Animation.INTERPOLATION_LINEAR)
	a.position_track_insert_key(p, 0.0, Vector3.ZERO)
	if not reset:
		a.position_track_insert_key(p, 2.0, Vector3(4, 0, 0))
	var r := a.add_track(Animation.TYPE_ROTATION_3D)
	a.track_set_path(r, NodePath("Skeleton:root"))
	a.track_set_interpolation_type(r, Animation.INTERPOLATION_LINEAR)
	a.rotation_track_insert_key(r, 0.0, Quaternion.IDENTITY)
	if not reset:
		a.rotation_track_insert_key(r, 2.0, Quaternion(Vector3.UP, PI / 2.0))
	return a

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 1 or not args[0] in ["pose", "extract"]:
		quit(2)
		return
	var mode: String = args[0]
	var actor := Node3D.new()
	actor.name = "Actor"
	root.add_child(actor)
	var skeleton := Skeleton3D.new()
	skeleton.name = "Skeleton"
	actor.add_child(skeleton)
	skeleton.add_bone("root")
	skeleton.set_bone_rest(0, Transform3D.IDENTITY)
	skeleton.reset_bone_poses()
	var player := AnimationPlayer.new()
	player.name = "Player"
	player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	actor.add_child(player)
	var library := AnimationLibrary.new()
	library.add_animation("RESET", clip(true))
	library.add_animation("motion", clip(false))
	player.add_animation_library("", library)
	var tree := AnimationTree.new()
	tree.name = "Tree"
	tree.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	actor.add_child(tree)
	tree.anim_player = NodePath("../Player")
	var node := AnimationNodeAnimation.new()
	node.animation = "motion"
	tree.tree_root = node
	tree.root_motion_local = false
	tree.root_motion_track = NodePath("Skeleton:root") if mode == "extract" else NodePath("")
	tree.active = true
	var calls: Array = []
	tree.advance(0.0)
	calls.append("advance(0)")
	var snapshots: Array = [capture(tree, skeleton, actor, "initial")]
	tree.advance(0.5)
	calls.append("advance(0.5)")
	snapshots.append(capture(tree, skeleton, actor, "first_read"))
	snapshots.append(capture(tree, skeleton, actor, "second_read_no_advance"))
	var receivers: Array = []
	if mode == "extract":
		var dp := tree.get_root_motion_position()
		var dq := tree.get_root_motion_rotation()
		for count in [0, 1, 2]:
			var receiver := Node3D.new()
			root.add_child(receiver)
			for repeat in range(count):
				receiver.position += dp
				receiver.quaternion = receiver.quaternion * dq
			receivers.append({"application_count": count, "pose": pose(receiver)})
		tree.advance(0.25)
		calls.append("advance(0.25)")
		snapshots.append(capture(tree, skeleton, actor, "next_evaluation"))
	print("RESULT_JSON=" + JSON.stringify({"mode": mode, "version": Engine.get_version_info(),
		"manual": tree.callback_mode_process, "root_motion_local": tree.root_motion_local,
		"root_motion_track": str(tree.root_motion_track), "calls": calls,
		"snapshots": snapshots, "receivers": receivers}))
	quit(0)
