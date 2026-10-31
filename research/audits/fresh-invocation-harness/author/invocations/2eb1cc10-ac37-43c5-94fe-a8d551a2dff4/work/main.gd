extends Node
var sample: float = -1.0
var hits: int = 0
var labels: Array = []
var finishes: int = 0
var player: AnimationPlayer
var strategy: String
var phase: String = "setup"
var traces: Array = []
var config: Dictionary = {}
func record(kind: String) -> void:
	var row := {"kind":kind,"phase":phase,"strategy":strategy,"sample":sample,"hits":hits,"labels":labels.duplicate(),"finishes":finishes,"position":player.current_animation_position,"assigned":player.assigned_animation}
	traces.append(row)
	print("TRACE " + JSON.stringify(row))
func marker(label: String = "single") -> void:
	labels.append(label)
	hits += 1
	record("method")
func completed(anim: StringName) -> void:
	finishes += 1
	print("SIGNAL " + str(anim))
	record("finished")
func _ready() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 1 or args[0] not in ["seek_cross", "advance_cross", "seek_exact", "seek_exact_update_only", "seek_two_cross", "advance_two_cross"]:
		push_error("invalid case")
		get_tree().quit(2)
		return
	strategy = args[0]
	player = AnimationPlayer.new()
	add_child(player)
	player.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	player.callback_mode_method = AnimationMixer.ANIMATION_CALLBACK_MODE_METHOD_IMMEDIATE
	player.root_node = NodePath("..")
	var anim := Animation.new()
	anim.length = 1.0
	anim.loop_mode = Animation.LOOP_NONE
	var value_track := anim.add_track(Animation.TYPE_VALUE)
	anim.track_set_path(value_track, NodePath(".:sample"))
	anim.track_insert_key(value_track, 0.0, 0.0)
	anim.track_insert_key(value_track, 1.0, 1.0)
	var method_track := anim.add_track(Animation.TYPE_METHOD)
	anim.track_set_path(method_track, NodePath("."))
	if "two" in strategy:
		anim.track_insert_key(method_track, 0.25, {"method": &"marker", "args": ["A"]})
		anim.track_insert_key(method_track, 0.6, {"method": &"marker", "args": ["B"]})
	else:
		anim.track_insert_key(method_track, 0.5, {"method": &"marker", "args": []})
	var library := AnimationLibrary.new()
	library.add_animation(&"attack_visual", anim)
	player.add_animation_library(&"", library)
	player.animation_finished.connect(completed)
	config = {"process_mode":player.callback_mode_process,"method_mode":player.callback_mode_method,"length":anim.length,"loop":anim.loop_mode,"keys": _keys(anim, method_track),"key_time":anim.track_get_key_time(method_track,0),"key_value":anim.track_get_key_value(method_track,0),"method_path":str(anim.track_get_path(method_track)),"value_path":str(anim.track_get_path(value_track)),"version":Engine.get_version_info()}
	print("CONFIG " + JSON.stringify(config))
	player.play(&"attack_visual")
	player.advance(0.0)
	record("initialized")
	phase = "first"
	record("before")
	if strategy in ["seek_cross", "seek_two_cross"]:
		player.seek(0.75, true, false)
	elif strategy in ["advance_cross", "advance_two_cross"]:
		player.advance(0.75)
	else:
		player.seek(0.5, true, strategy == "seek_exact_update_only")
	record("after")
	if strategy.ends_with("cross"):
		phase = "end"
		record("before")
		if strategy in ["seek_cross", "seek_two_cross"]:
			player.seek(1.0, true, false)
		else:
			player.advance(0.25)
		record("after")
	print("RESULT_JSON=" + JSON.stringify({"case":strategy,"config":config,"traces":traces}))
	get_tree().quit(0)

func _keys(anim: Animation, track: int) -> Array:
	var rows: Array = []
	for i in anim.track_get_key_count(track):
		rows.append({"time":anim.track_get_key_time(track,i),"value":anim.track_get_key_value(track,i)})
	return rows
