extends SceneTree
var mode: String
var sensor: Area2D
var sensor_shape: CollisionShape2D
var body: StaticBody2D
var events: Array = []
var entries: int = 0
var exits: int = 0
var callback_active: bool = false
var marker_seen: bool = false
var immediate_disabled: bool = false
var marker_disabled: bool = false

func record(kind: String) -> void:
	events.append({"kind":kind, "physics_frame":Engine.get_physics_frames(), "process_frame":Engine.get_process_frames(), "body_id":body.get_instance_id(), "body_position":[body.position.x,body.position.y], "disabled":sensor_shape.disabled})

func _initialize() -> void:
	mode = OS.get_cmdline_user_args()[0]
	call_deferred("execute")

func entered(who: Node2D) -> void:
	entries += 1
	callback_active = true
	record("enter")
	events[-1]["event_body_id"] = who.get_instance_id()
	if who != body:
		push_error("Unexpected body")
	if entries == 1:
		if mode == "direct-shape":
			sensor_shape.disabled = true
		else:
			sensor_shape.set_deferred("disabled", true)
		immediate_disabled = sensor_shape.disabled
		record("setter_return")
		call_deferred("observation_marker")
	callback_active = false
	record("callback_return")

func exited(who: Node2D) -> void:
	exits += 1
	record("exit")
	events[-1]["event_body_id"] = who.get_instance_id()

func observation_marker() -> void:
	marker_disabled = sensor_shape.disabled
	record("marker")
	if callback_active:
		push_error("Marker inside callback")
	marker_seen = true
	body.position = Vector2(100,0)
	record("move_outside")
	for i in range(4):
		await physics_frame
		record("outside_prephysics_boundary")
	body.position = Vector2.ZERO
	record("move_inside")
	for i in range(4):
		await physics_frame
		record("inside_prephysics_boundary")
	record("final")
	var overlap_ids: Array = []
	for b in sensor.get_overlapping_bodies():
		overlap_ids.append(b.get_instance_id())
	var result = {"mode":mode,"entries":entries,"exits":exits,"immediate_disabled":immediate_disabled,"marker_disabled":marker_disabled,"callback_active":callback_active,"body_id":body.get_instance_id(),"sensor_id":sensor.get_instance_id(),"events":events,"overlap_ids":overlap_ids,"settings":{"backend":ProjectSettings.get_setting("physics/2d/physics_engine"),"separate_thread":ProjectSettings.get_setting("physics/2d/run_on_separate_thread"),"ticks_per_second":Engine.physics_ticks_per_second,"sensor_radius":sensor_shape.shape.radius,"body_radius":body.get_child(0).shape.radius,"sensor_position":[sensor.position.x,sensor.position.y],"sensor_layer":sensor.collision_layer,"sensor_mask":sensor.collision_mask,"body_layer":body.collision_layer,"body_mask":body.collision_mask,"monitoring":sensor.monitoring},"engine":Engine.get_version_info()}
	print("RESULT_JSON=" + JSON.stringify(result))
	quit(0)

func execute() -> void:
	sensor = Area2D.new()
	sensor.collision_layer = 1
	sensor.collision_mask = 1
	sensor.monitoring = true
	sensor_shape = CollisionShape2D.new()
	var circle = CircleShape2D.new()
	circle.radius = 10
	sensor_shape.shape = circle
	sensor.add_child(sensor_shape)
	body = StaticBody2D.new()
	body.collision_layer = 1
	body.collision_mask = 1
	body.position = Vector2(100,0)
	var body_shape = CollisionShape2D.new()
	var body_circle = CircleShape2D.new()
	body_circle.radius = 5
	body_shape.shape = body_circle
	body.add_child(body_shape)
	root.add_child(sensor)
	root.add_child(body)
	sensor.body_entered.connect(entered)
	sensor.body_exited.connect(exited)
	record("initial_outside")
	for i in range(4):
		await physics_frame
		record("initial_prephysics_boundary")
	body.position = Vector2.ZERO
	record("initial_move_inside")
	for i in range(20):
		await physics_frame
		if marker_seen:
			return
	print("DIAGNOSTIC_JSON=" + JSON.stringify({"events":events,"sensor_space":PhysicsServer2D.area_get_space(sensor.get_rid()).get_id(),"body_space":PhysicsServer2D.body_get_space(body.get_rid()).get_id(),"world_space":sensor.get_world_2d().space.get_id(),"space_active":PhysicsServer2D.space_is_active(sensor.get_world_2d().space),"sensor_shape_count":PhysicsServer2D.area_get_shape_count(sensor.get_rid()),"body_shape_count":PhysicsServer2D.body_get_shape_count(body.get_rid()),"body_server_transform":str(PhysicsServer2D.body_get_state(body.get_rid(),PhysicsServer2D.BODY_STATE_TRANSFORM)),"sensor_server_transform":str(PhysicsServer2D.area_get_transform(sensor.get_rid())),"sensor_disabled":sensor_shape.disabled,"paused":paused,"physics_frames":Engine.get_physics_frames(),"process_frames":Engine.get_process_frames()}))
	push_error("Initial entry deadline exceeded")
	quit(2)
