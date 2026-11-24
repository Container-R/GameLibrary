extends SceneTree

const MID := Vector2(960, 540)
const SHIFT := 0.20
const EPS_WORLD := 0.0001
const EPS_PX := 0.005

var view: SubViewport
var aim: Camera3D
var visual: Camera3D
var frame_i := 0
var finished := false

func _initialize() -> void:
	var args := OS.get_cmdline_user_args()
	if args.size() != 1 or args[0] != "--fixture":
		push_error("Expected --fixture")
		quit(2)
		return
	call_deferred("setup")

func setup() -> void:
	view = SubViewport.new()
	view.size = Vector2i(1920, 1080)
	view.own_world_3d = true
	view.world_3d = World3D.new()
	root.add_child(view)
	aim = make_camera()
	visual = make_camera()
	visual.make_current()
	# Two thin, small boxes on distinct physics layers. The front faces are
	# exactly at -5 and -20 m; independent masks prevent mutual occlusion.
	target("near", 5.0, 1)
	target("far", 20.0, 2)

func make_camera() -> Camera3D:
	var camera := Camera3D.new()
	camera.keep_aspect = Camera3D.KEEP_WIDTH
	camera.fov = 90.0
	camera.near = 0.05
	camera.far = 100.0
	view.add_child(camera)
	return camera

func target(label: String, depth: float, layer: int) -> void:
	var body := StaticBody3D.new()
	body.name = label
	body.collision_layer = layer
	body.collision_mask = 0
	body.position = Vector3(0, 0, -depth - 0.05)
	var collider := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(0.1, 0.1, 0.1)
	collider.shape = box
	body.add_child(collider)
	view.add_child(body)

func check(ok: bool, why: String) -> void:
	if not ok:
		push_error("FAIL: " + why)
		finished = true
		quit(1)

func cast(camera: Camera3D, screen: Vector2, mask: int) -> Dictionary:
	var origin := camera.project_ray_origin(screen)
	var direction := camera.project_ray_normal(screen)
	var query := PhysicsRayQueryParameters3D.create(origin, origin + 50.0 * direction, mask)
	return aim.get_world_3d().direct_space_state.intersect_ray(query)

func _physics_process(_delta: float) -> bool:
	if not is_instance_valid(view) or finished:
		return false
	frame_i += 1
	if frame_i != 3:
		return false
	print("viewport=1920x1080 horizontal_fov=90 fixed_reticle=(960,540)")
	var old_positions := {}
	for phase in ["baseline", "shifted", "disabled_with_active_offset"]:
		var raw_offset: float = 0.0 if phase == "baseline" else SHIFT
		var motion_scale: float = 0.0 if phase == "disabled_with_active_offset" else 1.0
		var shift: float = raw_offset * motion_scale
		visual.position = Vector3(shift, 0, 0)
		var origin := aim.project_ray_origin(MID)
		var direction := aim.project_ray_normal(MID)
		check(origin.length() < EPS_WORLD and direction.distance_to(Vector3.FORWARD) < EPS_WORLD, "fixed aim ray")
		print("phase=%s raw_offset=%.2f scale=%.1f camera_shift=%.2f gameplay_ray_origin=(%.3f,%.3f,%.3f) direction=(%.3f,%.3f,%.3f)" %
			[phase, raw_offset, motion_scale, shift, origin.x, origin.y, origin.z, direction.x, direction.y, direction.z])
		for target_i in [0, 1]:
			var expected_depth := 5.0 if target_i == 0 else 20.0
			var mask: int = 1 << target_i
			var hit := cast(aim, MID, mask)
			check(not hit.is_empty(), "gameplay ray must hit")
			if hit.is_empty():
				return false
			var pos: Vector3 = hit.position
			check(pos.distance_to(Vector3(0, 0, -expected_depth)) < EPS_WORLD, "front surface position")
			if phase == "baseline":
				old_positions[mask] = pos
			else:
				check(pos.distance_to(old_positions[mask]) < EPS_WORLD, "same gameplay hit after visual shift")
			var projected := visual.unproject_position(pos)
			var expected_x: float = 960.0 - 960.0 * shift / expected_depth
			check(absf(projected.x - expected_x) < EPS_PX and absf(projected.y - MID.y) < EPS_PX, "projected point")
			var fixed := cast(visual, MID, mask)
			var aligned := cast(visual, projected, mask)
			check(fixed.is_empty() == (shift > 0.0), "fixed reticle ray negative control")
			check(not aligned.is_empty(), "reprojected marker ray must hit")
			if not aligned.is_empty():
				check(aligned.collider == hit.collider and pos.distance_to(aligned.position) < EPS_WORLD, "reprojected marker hits same collider and point")
			print("depth=%.0f gameplay_hit=(%.3f,%.3f,%.3f) marker=(%.3f,%.3f) dx=%.3f fixed_reticle_ray=%s marker_ray=%s" %
				[expected_depth, pos.x, pos.y, pos.z, projected.x, projected.y, projected.x - MID.x,
				"miss" if fixed.is_empty() else "hit", "miss" if aligned.is_empty() else "hit"])
	# Synthetic gameplay outcomes passed through two presentation settings.
	var events: Array[Dictionary] = [
		{"id": 19, "kind": "hit", "direction": "left", "tick": 100},
		{"id": 20, "kind": "block", "direction": "left", "tick": 101},
	]
	for event in events:
		event.make_read_only()
		var enabled := cue(event, true, true, true)
		var disabled := cue(event, false, false, false)
		var expected := "HIT" if event.kind == "hit" else "BLOCK"
		check(disabled.label == expected and disabled.label == enabled.label, "distinct stable text cues")
		check(disabled.id == enabled.id and disabled.tick == enabled.tick and disabled.direction == enabled.direction, "same event ID, tick and direction")
		check(enabled.shake and enabled.audio and enabled.rumble, "optional channels enabled")
		check(not disabled.shake and not disabled.audio and not disabled.rumble, "optional channels muted")
		print("event=%d tick=%d kind=%s direction=%s all_on_label=%s all_off_label=%s shake/audio/rumble=off" %
			[disabled.id, disabled.tick, event.kind, disabled.direction, enabled.label, disabled.label])
	if not finished:
		print("PASS")
		finished = true
		quit()
	return false

func cue(event: Dictionary, shake: bool, audio: bool, rumble: bool) -> Dictionary:
	return {
		"id": event.id,
		"tick": event.tick,
		"label": "HIT" if event.kind == "hit" else "BLOCK",
		"direction": event.direction,
		"shake": shake,
		"audio": audio,
		"rumble": rumble,
	}
