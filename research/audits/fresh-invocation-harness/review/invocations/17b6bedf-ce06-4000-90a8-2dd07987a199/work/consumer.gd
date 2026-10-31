extends Node
var ticks: int = 0
var inputs: Array = []
var naive_events: Array = []
var guarded_events: Array = []

func _input(event: InputEvent) -> void:
    if event is InputEventAction and event.action == &"fixture_attack":
        inputs.append({"label": event.get_meta("label"), "pressed": event.pressed,
            "paused": get_tree().paused})

func _physics_process(delta: float) -> void:
    ticks += 1
    var owner_node: Node = get_parent()
    owner_node.trace.append({"kind": "gameplay_physics", "tick": ticks,
        "paused": get_tree().paused, "delta": delta})
    while not owner_node.naive_queue.is_empty():
        naive_events.append(owner_node.naive_queue.pop_front()["label"])
    while not owner_node.guarded_queue.is_empty():
        var command: Dictionary = owner_node.guarded_queue.pop_front()
        if command["epoch"] == owner_node.epoch:
            guarded_events.append(command["label"])
