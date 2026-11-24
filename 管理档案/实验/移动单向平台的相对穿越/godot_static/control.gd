extends SceneTree

var actors: Array[CharacterBody2D] = []
var callback_step = 0
var below_passed = false
var below_landed = false
var two_way_blocked = false
var above_landed = false

func make_body(x: float, y: float, one_way: bool, platform: bool) -> PhysicsBody2D:
	var body: PhysicsBody2D
	var rect := RectangleShape2D.new()
	if platform:
		body = StaticBody2D.new()
		body.collision_mask = 0
		body.collision_layer = 1
		rect.size = Vector2(50, 8)
	else:
		body = CharacterBody2D.new()
		body.collision_mask = 1
		body.collision_layer = 2
		rect.size = Vector2(8, 12)
	body.position = Vector2(x, y)
	var shape := CollisionShape2D.new()
	shape.shape = rect
	shape.one_way_collision = one_way
	body.add_child(shape)
	root.add_child(body)
	return body

func _initialize() -> void:
	_setup.call_deferred()

func _setup() -> void:
	make_body(0, 0, true, true)
	make_body(100, 0, false, true)
	make_body(200, 0, true, true)
	actors.append(make_body(0, 30, false, false) as CharacterBody2D)
	actors.append(make_body(100, 30, false, false) as CharacterBody2D)
	actors.append(make_body(200, -30, false, false) as CharacterBody2D)
	physics_frame.connect(_physics)

func _physics() -> void:
	callback_step += 1
	if callback_step <= 3:
		return
	var upward: bool = callback_step <= 33
	actors[0].velocity = Vector2(0, -120 if upward else 120)
	actors[1].velocity = Vector2(0, -120 if upward else 0)
	actors[2].velocity = Vector2(0, 120)
	for actor in actors:
		actor.move_and_slide()
	if upward:
		below_passed = below_passed or actors[0].position.y < -10
		two_way_blocked = two_way_blocked or actors[1].is_on_ceiling()
	else:
		below_landed = below_landed or actors[0].is_on_floor()
	above_landed = above_landed or actors[2].is_on_floor()
	if callback_step >= 68:
		print("one-way from below reaches clear upper side: ", below_passed)
		print("one-way from below then descending lands above: ", below_landed, " final y=", "%.2f" % actors[0].position.y)
		print("two-way from below hits underside: ", two_way_blocked, " final y=", "%.2f" % actors[1].position.y)
		print("one-way from above lands: ", above_landed, " final y=", "%.2f" % actors[2].position.y)
		quit(0 if below_passed and below_landed and two_way_blocked and above_landed else 1)
