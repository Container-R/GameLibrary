extends SceneTree

# Own application completion policy; deferred callbacks and Camera3D are native.
const PLAYING := "playing"
const GAME := "game"
const A := "clip#1"
const B := "clip#2"
const C := "overlay#1"
const KEY := "quest:key"
var cameras: Dictionary = {}
var active := ""
var camera_lease := GAME
var input_lease := GAME
var phases: Dictionary = {}
var grants: Dictionary = {}
var trace: Array[Dictionary] = []
var policy := ""

func _initialize() -> void:
	_run.call_deferred()

func _run() -> void:
	for entry in [GAME, A, B]:
		var camera := Camera3D.new()
		camera.name = entry.replace("#", "_")
		root.add_child(camera)
		cameras[entry] = camera
	var results: Dictionary = {}
	for mode in ["grant_only", "entry_guard", "compare_release"]:
		var rows: Dictionary = {}
		for scenario in ["skip_late_duplicate", "cancel_late_duplicate", "split_resource", "cleanup_reentry"]:
			policy = mode
			rows[scenario] = await _case(scenario)
		results[mode] = rows
	if not _check(results):
		printerr("Ownership expectations failed: ", JSON.stringify(results))
		quit(1)
		return
	print(JSON.stringify({"engine": Engine.get_version_info().string,
		"scope": "Native call_deferred and Viewport.get_camera_3d; synthetic quest flag and project input gate, not save persistence or devices",
		"cases": results}))
	quit(0)

func _activate(id: String) -> void:
	active = id
	phases[id] = PLAYING
	camera_lease = id
	input_lease = id
	cameras[id].make_current()

func _snapshot() -> Dictionary:
	var camera_name := ""
	for id: String in cameras:
		if root.get_camera_3d() == cameras[id]:
			camera_name = id
	return {"active": active, "current_camera": camera_name, "camera_lease": camera_lease,
		"input_lease": input_lease, "gameplay_input_allowed": input_lease == GAME, "grants": grants.size()}

func _finish(id: String, reason: String, activate_during_release := false) -> bool:
	if policy != "grant_only" and (id != active or phases.get(id) != PLAYING):
		return false
	phases[id] = reason
	if id == active:
		active = ""
	if reason != "cancel" and id == A:
		grants[KEY] = true
	# Explicit synchronous re-entry is an adversarial application hook.
	if activate_during_release:
		_activate(B)
	if policy != "compare_release" or camera_lease == id:
		camera_lease = GAME
		cameras[GAME].make_current()
	if policy != "compare_release" or input_lease == id:
		input_lease = GAME
	return true

func _late(id: String) -> void:
	var before := _snapshot()
	var accepted := _finish(id, "natural")
	trace.append({"before": before, "accepted": accepted, "after": _snapshot()})

func _case(scenario: String) -> Dictionary:
	active = ""
	camera_lease = GAME
	input_lease = GAME
	phases.clear()
	grants.clear()
	trace.clear()
	cameras[GAME].make_current()
	_activate(A)
	var old := A
	if scenario.ends_with("duplicate"):
		_late.call_deferred(old)
		_late.call_deferred(old)
		_finish(A, "cancel" if scenario.begins_with("cancel") else "skip")
		_activate(B)
		var successor := _snapshot()
		# Never call the callback directly; wait until Godot's queue delivers both.
		for frame in range(4):
			if trace.size() == 2:
				break
			await process_frame
		return {"successor_before_callbacks": successor, "deliveries": trace.duplicate(true), "final": _snapshot()}
	if scenario == "split_resource":
		input_lease = C
	var accepted := _finish(A, "skip", scenario == "cleanup_reentry")
	return {"accepted": accepted, "final": _snapshot()}

func _check(results: Dictionary) -> bool:
	for mode: String in results:
		var rows: Dictionary = results[mode]
		for scenario in ["skip_late_duplicate", "cancel_late_duplicate"]:
			var row: Dictionary = rows[scenario]
			var after: Dictionary = row.final
			var bad := mode == "grant_only"
			var target_grants := 1 if scenario.begins_with("skip") or bad else 0
			if row.deliveries.size() != 2 or row.successor_before_callbacks.current_camera != B:
				return false
			if row.deliveries[0].before.current_camera != B or row.deliveries[0].before.input_lease != B:
				return false
			if row.deliveries[0].accepted != bad or row.deliveries[1].accepted != bad:
				return false
			if after.current_camera != (GAME if bad else B) or after.input_lease != (GAME if bad else B) or after.grants != target_grants:
				return false
		var robust := mode == "compare_release"
		if rows.split_resource.final.input_lease != (C if robust else GAME) or rows.split_resource.final.current_camera != GAME:
			return false
		if rows.cleanup_reentry.final.current_camera != (B if robust else GAME) or rows.cleanup_reentry.final.input_lease != (B if robust else GAME):
			return false
	return true
