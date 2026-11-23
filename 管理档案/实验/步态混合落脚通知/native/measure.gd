extends SceneTree

class Probe extends Node:
	var trial: String
	var t_ms: int
	var blend: float
	func record(source: String, key_ms: int) -> void:
		var line := "%s,%s,%d,%d,%.2f" % [trial, source, key_ms, t_ms, blend]
		print(line)

func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	print("trial,clip,key_ms,advance_to_ms,blend_run")
	_trial("only_walk", 480, 520, 0.0)
	_trial("only_run", 480, 520, 1.0)
	_trial("steady_half", 480, 520, 0.5)
	_trial("handoff_aligned", 500, 500, -1.0)
	_trial("handoff_walk_early", 480, 520, -1.0)
	_trial("handoff_walk_late", 520, 480, -1.0)
	_trial("synced_handoff_aligned", 500, 500, -1.0, true)
	_trial("synced_handoff_walk_early", 480, 520, -1.0, true)
	_trial("synced_handoff_walk_late", 520, 480, -1.0, true)
	quit()

func _clip(label: String, key_ms: int) -> Animation:
	var a := Animation.new()
	a.length = 1.0
	var track := a.add_track(Animation.TYPE_METHOD)
	a.track_set_path(track, NodePath("Probe"))
	a.track_insert_key(track, key_ms / 1000.0, {"method": &"record", "args": [label, key_ms]})
	return a

func _trial(label: String, key_walk: int, key_run: int, fixed_blend: float, sync: bool = false) -> void:
	var rig := Node.new()
	root.add_child(rig)
	var probe := Probe.new()
	probe.name = "Probe"
	probe.trial = label
	rig.add_child(probe)
	var player := AnimationPlayer.new()
	player.name = "Player"
	rig.add_child(player)
	var library := AnimationLibrary.new()
	library.add_animation(&"walk", _clip("walk", key_walk))
	library.add_animation(&"run", _clip("run", key_run))
	player.add_animation_library(&"", library)
	var tree := AnimationTree.new()
	tree.anim_player = NodePath("../Player")
	tree.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	tree.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE
	var graph := AnimationNodeBlendTree.new()
	var walk := AnimationNodeAnimation.new()
	walk.animation = &"walk"
	var run := AnimationNodeAnimation.new()
	run.animation = &"run"
	graph.add_node(&"walk", walk)
	graph.add_node(&"run", run)
	var mix := AnimationNodeBlend2.new()
	mix.sync = sync
	graph.add_node(&"mix", mix)
	graph.connect_node(&"mix", 0, &"walk")
	graph.connect_node(&"mix", 1, &"run")
	graph.connect_node(&"output", 0, &"mix")
	tree.tree_root = graph
	rig.add_child(tree)
	tree.active = true
	for t_ms in range(10, 1110, 10):
		probe.t_ms = t_ms
		probe.blend = fixed_blend if fixed_blend >= 0 else clampf((t_ms - 400.0) / 200.0, 0.0, 1.0)
		tree.set("parameters/mix/blend_amount", probe.blend)
		tree.advance(0.01)
	rig.free()
