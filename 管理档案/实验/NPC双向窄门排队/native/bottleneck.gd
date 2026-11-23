extends SceneTree
## Real CharacterBody2D collision queries; no NavigationServer or RVO.

const RADIUS := 30.0
const STEP := 2.0
const TICKS := 420

func _initialize() -> void:
	_run.call_deferred()

func _body(where: Vector2, parent: Node2D) -> CharacterBody2D:
	var agent := CharacterBody2D.new()
	var hitbox := CollisionShape2D.new()
	var circle := CircleShape2D.new()
	circle.radius = RADIUS
	hitbox.shape = circle
	agent.add_child(hitbox)
	agent.position = where
	parent.add_child(agent)
	return agent

func _wall(y: float, parent: Node2D) -> void:
	var wall := StaticBody2D.new()
	var hitbox := CollisionShape2D.new()
	var rect := RectangleShape2D.new()
	rect.size = Vector2(200.0, 10.0)
	hitbox.shape = rect
	wall.add_child(hitbox)
	wall.position = Vector2(100, y)
	parent.add_child(wall)

func _measure(gated: bool) -> Dictionary:
	var stage := Node2D.new()
	root.add_child(stage)
	_wall(-60.0, stage)
	_wall(60.0, stage)
	var east := _body(Vector2(-50, 0), stage)
	var west := _body(Vector2(250, 90), stage)
	await physics_frame
	await physics_frame
	var first_east := -1
	var first_west := -1
	var hit_count := 0
	var min_center_gap := INF
	var label := "no_admission" if not gated else "gated"
	var west_admitted := not gated
	for tick in range(1, TICKS + 1):
		await physics_frame
		if east.position.x < 316:
			if east.move_and_collide(Vector2(STEP, 0), false, 0.01) != null:
				hit_count += 1
		if gated and not west_admitted and east.position.x >= 316:
			west_admitted = true
			print("%s tick=%d handoff east_x=%.1f west_x=%.1f east_tail=%.1f" % [label, tick, east.position.x, west.position.x, east.position.x - RADIUS])
		if west_admitted and west.position.x > -116:
			var motion := Vector2(-STEP, 0)
			if west.position.y > 0:
				motion = Vector2(0, -STEP)
			if west.move_and_collide(motion, false, 0.01) != null:
				hit_count += 1
		min_center_gap = minf(min_center_gap, east.position.distance_to(west.position))
		if first_east < 0 and east.position.x - RADIUS >= 200:
			first_east = tick
		if first_west < 0 and west.position.x + RADIUS <= 0:
			first_west = tick
	var result := {"east": first_east, "west": first_west, "hits": hit_count, "min_gap": min_center_gap}
	print("%s ticks=%d clear_E=%d clear_W=%d hit_calls=%d min_center_gap=%.3f final=(%.1f,%.1f)" % [label, TICKS, first_east, first_west, hit_count, min_center_gap, east.position.x, west.position.x])
	stage.queue_free()
	await physics_frame
	return result

func _run() -> void:
	var bare := await _measure(false)
	var gated := await _measure(true)
	if not (bare.east == -1 and bare.west == -1 and bare.hits > 0 and bare.min_gap >= 57.9
		and gated.east > 0 and gated.west > gated.east and gated.hits == 0 and gated.min_gap >= 60):
		push_error("Unexpected fixed-case result")
		quit(1)
	else:
		quit(0)
