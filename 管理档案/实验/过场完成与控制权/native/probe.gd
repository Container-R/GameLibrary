extends SceneTree

class Probe:
	extends Node
	var door := 0.0
	var log: Array[String] = []
	func record(event: String) -> void:
		log.append(event)

func _initialize() -> void:
	call_deferred("_run")

func _run() -> void:
	var result: Dictionary = {}
	for name in ["natural", "seek_from_start", "seek_after_effect", "advance_to_end"]:
		var p := Probe.new()
		p.name = name
		root.add_child(p)
		var a := AnimationPlayer.new()
		p.add_child(a)
		a.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
		a.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE
		var clip := Animation.new()
		clip.length = 2.0
		var value_idx := clip.add_track(Animation.TYPE_VALUE)
		clip.track_set_path(value_idx, NodePath(".:door"))
		clip.track_insert_key(value_idx, 0.0, 0.0)
		clip.track_insert_key(value_idx, 2.0, 1.0)
		var method_idx := clip.add_track(Animation.TYPE_METHOD)
		clip.track_set_path(method_idx, NodePath("."))
		clip.track_insert_key(method_idx, 0.5, {"method": "record", "args": ["flash"]})
		clip.track_insert_key(method_idx, 1.0, {"method": "record", "args": ["key_award_attempt"]})
		var lib := AnimationLibrary.new()
		lib.add_animation("cutscene", clip)
		a.add_animation_library("", lib)
		a.animation_finished.connect(func(_anim): p.record("animation_finished"))
		a.play("cutscene")
		a.advance(0)
		match name:
			"natural":
				for i in range(8):
					a.advance(0.25)
			"seek_from_start":
				a.seek(2.0, true, true)
			"seek_after_effect":
				a.advance(0.75)
				a.seek(2.0, true, true)
			"advance_to_end":
				a.advance(2.0)
		result[name] = {"door_visual": p.door, "events": p.log.duplicate(),
			"is_playing": a.is_playing(), "position": a.current_animation_position}
		p.free()
	print(JSON.stringify({"engine": Engine.get_version_info().string, "cases": result}))
	quit()
