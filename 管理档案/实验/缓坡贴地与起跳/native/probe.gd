extends SceneTree

func add_box(center: Vector2, size: Vector2, angle: float) -> StaticBody2D:
	var body := StaticBody2D.new()
	body.position = center
	body.rotation = angle
	var shape := RectangleShape2D.new()
	shape.size = size
	var collider := CollisionShape2D.new()
	collider.shape = shape
	body.add_child(collider)
	root.add_child(body)
	return body

func pair(v: Vector2) -> Array:
	return [snappedf(v.x, 0.0001), snappedf(v.y, 0.0001)]

func capture(p: CharacterBody2D) -> Dictionary:
	return {"p": pair(p.position), "delta": pair(p.get_position_delta()),
			"real": pair(p.get_real_velocity()), "velocity": pair(p.velocity),
			"floor": p.is_on_floor(), "normal": pair(p.get_floor_normal())}

func _initialize() -> void:
	call_deferred("run")

func run() -> void:
	var args := OS.get_cmdline_user_args()
	var level := args[0]
	var snap := float(args[1])
	var launch := args[2] == "jump"
	var manual := args[3] == "manual"
	Engine.physics_ticks_per_second = int(args[4])
	var slope := atan(0.25)
	if level == "ramp":
		add_box(Vector2(200, 150) + Vector2.DOWN.rotated(slope) * 10,
			Vector2(400 / cos(slope), 20), slope)
	else:
		add_box(Vector2(100, 110), Vector2(200, 20), 0)
		add_box(Vector2(300, 118), Vector2(200, 20), 0)
	var p := CharacterBody2D.new()
	p.position = Vector2(180 if level == "ramp" else 197, 80)
	p.floor_snap_length = snap
	p.floor_constant_speed = false
	p.safe_margin = 0.08
	var shape := RectangleShape2D.new()
	shape.size = Vector2(4, 8)
	var collider := CollisionShape2D.new()
	collider.shape = shape
	p.add_child(collider)
	root.add_child(p)
	for step in range(40):
		await physics_frame
		p.velocity = Vector2(0, 300)
		p.move_and_slide()
		if p.is_on_floor():
			break
	if not p.is_on_floor():
		printerr("fixture failed to establish initial support")
		quit(2)
		return
	await physics_frame
	var start := p.position
	p.velocity = Vector2(360, -90 if launch else 0)
	p.move_and_slide()
	var after_move := capture(p)
	if manual:
		p.apply_floor_snap()
	print(JSON.stringify({"case":args, "start": pair(start), "moved": after_move,
			"final":capture(p), "tick_hz": Engine.physics_ticks_per_second, "physics_dt": p.get_physics_process_delta_time()}))
	quit()
