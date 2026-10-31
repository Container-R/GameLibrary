extends Node

class Phase:
	extends Node
	var coordinator
	var label: String
	func _physics_process(delta: float) -> void:
		coordinator.callback(label, delta)

var mode: String
var first: String
var hp = {"A": 1, "B": 1}
var snapshot = {}
var trace = []
var intents = []
var events = []
var phases = []
var complete = false
var failed = false
var combat_frame = -1

func _ready() -> void:
	var args = OS.get_cmdline_user_args()
	if args.size() != 2 or args[0] not in ["immediate", "staged"] or args[1] not in ["A", "B"]:
		fail("invalid arguments")
		return
	mode = args[0]
	first = args[1]
	for label in ["Begin", "A", "B", "End"]:
		var node = Phase.new()
		node.coordinator = self
		node.label = label
		node.name = label
		node.set_physics_process(false)
		if label == "Begin":
			node.process_physics_priority = -100
		elif label == "End":
			node.process_physics_priority = 100
		else:
			node.process_physics_priority = 0 if label == first else 10
		add_child(node)
		phases.append(node)
	for node in phases:
		node.set_physics_process(true)

func fail(message: String) -> void:
	failed = true
	printerr("FIXTURE_FAILURE=" + message)
	get_tree().quit(2)

func callback(label: String, delta: float) -> void:
	if failed:
		return
	if complete:
		fail("callback after completion")
		return
	var frame = Engine.get_physics_frames()
	if label == "Begin":
		if not trace.is_empty():
			fail("second combat frame")
			return
		combat_frame = frame
		snapshot = hp.duplicate()
	if frame != combat_frame:
		fail("unbracketed callback")
		return
	var node = get_node(label)
	var row = {"label":label, "frame":frame, "delta":delta, "priority":node.process_physics_priority,
		"group":node.process_thread_group, "hp_before":hp.duplicate()}
	if label in ["A", "B"]:
		var target = "B" if label == "A" else "A"
		var basis = snapshot if mode == "staged" else hp
		var eligible = basis[label] > 0 and basis[target] > 0
		row["eligible"] = eligible
		if eligible:
			var intent = {"attacker":label, "target":target, "damage":1, "frame":frame}
			intents.append(intent)
			if mode == "immediate":
				apply_damage(intent)
	trace.append(row)
	print("TRACE_JSON=" + JSON.stringify(row))
	if label == "End":
		if trace.size() != 4 or trace[0]["label"] != "Begin":
			fail("incomplete callbacks")
			return
		if mode == "staged":
			for intent in intents:
				apply_damage(intent)
		complete = true
		for phase in phases:
			phase.set_physics_process(false)

func apply_damage(intent: Dictionary) -> void:
	var target = intent["target"]
	hp[target] -= intent["damage"]
	events.append({"kind":"damage", "attacker":intent["attacker"], "target":target, "amount":1})
	if hp[target] == 0:
		events.append({"kind":"death", "actor":target})

func _process(_delta: float) -> void:
	if complete and not failed:
		set_process(false)
		print("RESULT_JSON=" + JSON.stringify({"mode":mode, "first":first, "initial":{"A":1,"B":1},
			"snapshot":snapshot, "hp":hp, "trace":trace, "intents":intents, "events":events,
			"version":Engine.get_version_info(), "physics_ticks_per_second":Engine.physics_ticks_per_second,
			"root_group":process_thread_group, "tree_order":["Begin","A","B","End"]}))
		get_tree().quit(0)
