extends SceneTree
# Original finite focus configuration fixture; no synthetic input or native modal.
var fixture: Control
var background: Control
var modal: Control
var opener: Control
var fallback: Control
var rows: Array = []
var phase: String = "setup"
var sequence: int = 0
var ticks: int = 0
var finished: bool = false

func make_control(parent: Node, label: String, local_mode: int, behavior: int) -> Control:
    var node := Control.new()
    node.name = label
    node.focus_mode = local_mode
    node.focus_behavior_recursive = behavior
    node.visible = true
    parent.add_child(node)
    return node

func node_info(node: Control) -> Dictionary:
    return {"id": node.get_instance_id(), "name": str(node.name),
        "parent_id": node.get_parent().get_instance_id(), "viewport_id": node.get_viewport().get_instance_id(),
        "inside_tree": node.is_inside_tree(), "visible_in_tree": node.is_visible_in_tree(),
        "local_mode": node.focus_mode, "effective_mode": node.get_focus_mode_with_override(),
        "behavior": node.focus_behavior_recursive,
        "in_modal": modal.is_ancestor_of(node), "position": [node.position.x, node.position.y],
        "size": [node.size.x, node.size.y]}

func record(kind: String, target: int = 0) -> void:
    # Observation ends after the final snapshot or an explicit failure gate.
    if finished:
        return
    sequence += 1
    var owner := root.gui_get_focus_owner()
    rows.append({"sequence": sequence, "phase": phase, "kind": kind, "target_id": target,
        "owner_id": owner.get_instance_id() if owner != null else 0,
        "nodes": {"fixture": node_info(fixture), "background": node_info(background),
                  "modal": node_info(modal), "opener": node_info(opener), "default": node_info(fallback)}})

func marker(label: String) -> void:
    phase = label
    record(label)

func _initialize() -> void:
    fixture = make_control(root, "Fixture", Control.FOCUS_NONE, Control.FOCUS_BEHAVIOR_INHERITED)
    background = make_control(fixture, "Background", Control.FOCUS_NONE, Control.FOCUS_BEHAVIOR_ENABLED)
    modal = make_control(fixture, "LogicalModal", Control.FOCUS_NONE, Control.FOCUS_BEHAVIOR_ENABLED)
    opener = make_control(background, "Opener", Control.FOCUS_ALL, Control.FOCUS_BEHAVIOR_INHERITED)
    fallback = make_control(modal, "Default", Control.FOCUS_ALL, Control.FOCUS_BEHAVIOR_INHERITED)
    opener.size = Vector2(160, 40)
    fallback.size = Vector2(160, 40)
    opener.position = Vector2.ZERO
    fallback.position = Vector2(200, 0)
    opener.focus_entered.connect(func(): record("focus_entered", opener.get_instance_id()))
    opener.focus_exited.connect(func(): record("focus_exited", opener.get_instance_id()))
    fallback.focus_entered.connect(func(): record("focus_entered", fallback.get_instance_id()))
    fallback.focus_exited.connect(func(): record("focus_exited", fallback.get_instance_id()))
    root.gui_focus_changed.connect(func(node: Control): record("gui_focus_changed", node.get_instance_id()))
    call_deferred("begin")

func postcall_gate(expected_owner: Control, expected_bg: int, expected_child: int, expected_effective: int) -> bool:
    if root.gui_get_focus_owner() != expected_owner or background.focus_behavior_recursive != expected_bg or opener.focus_behavior_recursive != expected_child or opener.get_focus_mode_with_override() != expected_effective:
        finished = true
        print("FAILURE_JSON=" + JSON.stringify({"phase": phase, "reason": "postcall capability/oracle gate", "trace": rows}))
        quit(2)
        return false
    return true

func begin() -> void:
    marker("initial")
    if not postcall_gate(null, 2, 0, 2): return
    marker("before_baseline_grab")
    opener.grab_focus()
    marker("baseline_after_grab")
    if not postcall_gate(opener, 2, 0, 2): return
    marker("before_parent_disable")
    background.focus_behavior_recursive = Control.FOCUS_BEHAVIOR_DISABLED
    marker("after_parent_disable")
    if not postcall_gate(null, 1, 0, 0): return
    marker("before_modal_grab")
    fallback.grab_focus()
    marker("modal_after_grab")
    if not postcall_gate(fallback, 1, 0, 0): return
    marker("before_child_enable")
    opener.focus_behavior_recursive = Control.FOCUS_BEHAVIOR_ENABLED
    marker("after_child_enable")
    if not postcall_gate(fallback, 1, 2, 2): return
    marker("before_naive_grab")
    opener.grab_focus()
    marker("naive_after_grab")
    if not postcall_gate(opener, 1, 2, 2): return
    call_deferred("observe_final")

func observe_final() -> void:
    marker("deferred_final")
    if not postcall_gate(opener, 1, 2, 2): return
    finished = true
    print("RESULT_JSON=" + JSON.stringify({"version": Engine.get_version_info(),
        "display_server": DisplayServer.get_name(), "viewport_id": root.get_instance_id(),
        "root_parent_id": root.get_instance_id(), "trace": rows}))
    quit(0)

func _process(_delta: float) -> bool:
    ticks += 1
    if ticks > 120 and not finished:
        push_error("recursive focus watchdog")
        quit(2)
    return false
