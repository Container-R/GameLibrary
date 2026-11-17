extends SceneTree

class Boundary extends Node:
	var step := -1
	var inbox: Array[String] = []
	var receive: Array = []
	var drained: Array = []
	var sent := false

	func feed() -> void:
		var e := InputEventAction.new()
		e.action = &"boundary_probe"
		e.pressed = true
		e.set_meta("id", "B")
		Input.parse_input_event(e)
		Input.flush_buffered_events()

	func _input(event: InputEvent) -> void:
		if event is InputEventAction and event.action == &"boundary_probe" and event.pressed:
			var id: String = event.get_meta("id")
			receive.append([step, Engine.is_in_physics_frame(), id])
			inbox.append(id)

	func _process(_dt: float) -> void:
		if step == 0 and not sent:
			sent = true
			feed()

	func _physics_process(_dt: float) -> void:
		step += 1
		if OS.get_cmdline_user_args().has("--drop-inbox"):
			inbox.clear()
		var batch := inbox
		inbox = []
		for id in batch:
			drained.append([step, id])
		if step == 2:
			print(JSON.stringify({"received":receive,"drained":drained,"dropped_variant":OS.get_cmdline_user_args().has("--drop-inbox")}))
			var ok := receive == [[0, false, "B"]] and drained == [[1, "B"]]
			get_tree().quit(0 if ok else 1)

func _initialize() -> void:
	call_deferred("install")

func install() -> void:
	InputMap.add_action(&"boundary_probe")
	root.add_child(Boundary.new())
