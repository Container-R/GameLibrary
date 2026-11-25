extends SceneTree

class Fixture extends Node3D:
	var foot_l := Node3D.new()
	var foot_r := Node3D.new()
	var player := AnimationPlayer.new()
	var delivered: Array[String] = []

	func _ready() -> void:
		foot_l.name = "L"
		foot_r.name = "R"
		add_child(foot_l)
		add_child(foot_r)
		add_child(player)
		player.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE
		player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
		var lib := AnimationLibrary.new()
		lib.add_animation("source", make_clip(false, "L"))
		lib.add_animation("pose_only", make_clip(true, "L"))
		lib.add_animation("both", make_clip(true, "R"))
		lib.add_animation("twice", make_clip(true, other(other("L"))))
		player.add_animation_library("", lib)

	func other(side: String) -> String:
		return "R" if side == "L" else "L"

	func make_clip(mirror: bool, side: String) -> Animation:
		var a := Animation.new()
		a.length = 1.0
		var left := Vector3(-1.5,0.7,0) if mirror else Vector3(-2.0,0.0,0)
		var right := Vector3(2.0,0.0,0) if mirror else Vector3(1.5,0.7,0)
		for row in [["L:position",left], ["R:position",right]]:
			var p := a.add_track(Animation.TYPE_VALUE)
			a.track_set_path(p, NodePath(row[0]))
			a.track_insert_key(p, 0.0, row[1])
		var event := a.add_track(Animation.TYPE_METHOD)
		a.track_set_path(event, NodePath("."))
		a.track_insert_key(event, 0.25, {"method":"foot_event", "args":[side]})
		return a

	func foot_event(side: String) -> void:
		delivered.append(side)

	func measure(clip: String) -> String:
		delivered.clear()
		player.stop()
		player.play(clip)
		player.advance(0)
		player.advance(0.30) # crosses the method key once
		assert(delivered.size() == 1)
		var f := foot_l if delivered[0] == "L" else foot_r
		var mat := "Stone" if f.position.x < 0 else "Metal" # synthetic regions, not ray casts
		return "%s L_height=%.1f R_height=%.1f event=%s sampled_height=%.1f region=%s" % [clip,foot_l.position.y,foot_r.position.y,delivered[0],f.position.y,mat]

func _initialize() -> void:
	run.call_deferred()

func run() -> void:
	var fixture := Fixture.new()
	root.add_child(fixture)
	var lines := []
	for clip in ["source","pose_only","both","twice"]:
		var info := fixture.measure(clip)
		lines.append(info)
		print(info)
	var ok: bool = lines == [
		"source L_height=0.0 R_height=0.7 event=L sampled_height=0.0 region=Stone",
		"pose_only L_height=0.7 R_height=0.0 event=L sampled_height=0.7 region=Stone",
		"both L_height=0.7 R_height=0.0 event=R sampled_height=0.0 region=Metal",
		"twice L_height=0.7 R_height=0.0 event=L sampled_height=0.7 region=Stone",
	]
	quit(0 if ok else 1)
