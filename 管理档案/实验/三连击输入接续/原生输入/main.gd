extends SceneTree

class Harness extends Node:
	var t := -1
	var mode := 0
	var stage := 0
	var started := 0
	var pending: Array = []
	var received: Array = []
	var starts: Array = []
	var seen := {}
	var inbox: Array = []
	var interrupt := false

	func emit_event(action: StringName, id: String) -> void:
		var e := InputEventAction.new()
		e.action = action
		e.pressed = true
		e.set_meta("id", id)
		Input.parse_input_event(e)
		Input.flush_buffered_events()

	func _input(event: InputEvent) -> void:
		if event is InputEventAction and event.pressed:
			var id: String = event.get_meta("id")
			received.append([t, id])
			if event.action == &"interrupt":
				interrupt = true
			else:
				inbox.append(id)

	func enter(next: int, id: String) -> void:
		stage = next
		started = t
		starts.append([t, next, id])

	func rules() -> void:
		if interrupt:
			stage = 0
			pending.clear()
			for id in inbox:
				seen[id] = true
			return
		if not pending.is_empty() and t >= pending[1]:
			pending.clear()
		if stage > 0 and t - started >= 6:
			stage = 0
			pending.clear()
		for id in inbox:
			if seen.has(id):
				continue
			seen[id] = true
			if stage == 0:
				enter(1, id)
			elif stage < 3 and pending.is_empty():
				pending = [id, t + 2]
		if stage > 0 and stage < 3 and t - started >= 3 and t - started < 5 and not pending.is_empty():
			var id: String = pending[0]
			pending.clear()
			enter(stage + 1, id)

	func _physics_process(_dt: float) -> void:
		t += 1
		inbox.clear()
		interrupt = false
		if t == 0:
			emit_event(&"attack", "A")
		if t == 2:
			emit_event(&"attack", "B")
		if t == 3 and mode == 1:
			emit_event(&"attack", "X")
			emit_event(&"interrupt", "interrupt")
		if t == 4 and mode == 1:
			emit_event(&"attack", "D")
		if t == 5:
			emit_event(&"attack", "C" if mode == 0 else "X")
		rules()
		if t == 8:
			var want_starts := [[0, 1, "A"], [3, 2, "B"], [6, 3, "C"]] if mode == 0 else [[0, 1, "A"], [4, 1, "D"]]
			var want_input := [[0, "A"], [2, "B"], [5, "C"]] if mode == 0 else [[0, "A"], [2, "B"], [3, "X"], [3, "interrupt"], [4, "D"], [5, "X"]]
			print(JSON.stringify({"mode": mode,"input": received,"starts": starts,"pending_at_end": pending}))
			if starts != want_starts or received != want_input or not pending.is_empty():
				get_tree().quit(1)
				return
			if mode == 1:
				get_tree().quit()
			else:
				mode = 1
				t = -1
				stage = 0
				pending.clear()
				seen.clear()
				starts.clear()
				received.clear()

func _initialize() -> void:
	call_deferred("install")

func install() -> void:
	InputMap.add_action(&"attack")
	InputMap.add_action(&"interrupt")
	root.add_child(Harness.new())
