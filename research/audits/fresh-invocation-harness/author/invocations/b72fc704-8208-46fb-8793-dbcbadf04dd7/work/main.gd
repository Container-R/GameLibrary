extends Control
# Original fixture. Logical dialog only: no native Window/modal input isolation.
var mode: String
var page: Control
var modal: Control
var old: Button
var replacement: Button
var safe: Button
var close_button: Button
var old_id: int
var path: NodePath
var revision: int = 1
var request_revision: int = 1
var trace: Array = []
var sequence: int = 0
var frames: int = 0
var observed: bool = false
var restore_count: int = 0

func record(kind: String, extra: Dictionary = {}) -> void:
    sequence += 1
    var owner: Control = get_viewport().gui_get_focus_owner()
    var row: Dictionary = {"sequence": sequence, "kind": kind,
        "owner_id": owner.get_instance_id() if owner != null else 0,
        "owner_name": str(owner.name) if owner != null else "none"}
    row.merge(extra)
    trace.append(row)

func make_button(parent_node: Control, node_name: String, business: String) -> Button:
    var button := Button.new()
    button.name = node_name
    button.text = business
    button.focus_mode = Control.FOCUS_ALL
    button.size = Vector2(160, 40)
    button.set_meta("business", business)
    parent_node.add_child(button)
    button.focus_entered.connect(func(): record("focus_entered", {"target_id": button.get_instance_id()}))
    button.focus_exited.connect(func(): record("focus_exited", {"target_id": button.get_instance_id()}))
    return button

func _ready() -> void:
    mode = OS.get_cmdline_user_args()[0]
    page = Control.new(); page.name = "Page"; add_child(page)
    modal = Control.new(); modal.name = "LogicalModal"; add_child(modal)
    old = make_button(page, "Opener", "record-A")
    safe = make_button(page, "SafeReturn", "safe-return")
    close_button = make_button(modal, "Close", "close-dialog")
    old_id = old.get_instance_id()
    path = old.get_path()
    call_deferred("begin")

func begin() -> void:
    old.grab_focus()
    record("initial_focus", {"old_id": old_id, "path": str(path)})
    close_button.grab_focus()
    record("dialog_focus", {"close_id": close_button.get_instance_id()})
    if mode == "gate":
        observed = true
        return
    # This request remains current: only identity is invalidated below.
    record("restore_enqueued", {"revision": revision, "request_revision": request_revision})
    call_deferred("restore")
    page.remove_child(old)
    record("old_detached", {"inside_tree": old.is_inside_tree(), "old_id": old_id})
    old.queue_free()
    replacement = make_button(page, "Opener", "record-B")
    modal.hide()
    record("replacement_ready", {"new_id": replacement.get_instance_id(),
        "new_path": str(replacement.get_path()), "business": replacement.get_meta("business"),
        "inside_tree": replacement.is_inside_tree(), "visible_in_tree": replacement.is_visible_in_tree(),
        "focus_mode": replacement.get_focus_mode_with_override()})

func restore() -> void:
    restore_count += 1
    var candidate: Button = get_node_or_null(path)
    record("restore_started", {"revision": revision, "request_revision": request_revision,
        "candidate_id": candidate.get_instance_id(), "expected_id": old_id,
        "business": candidate.get_meta("business")})
    if mode == "guarded" and candidate.get_instance_id() != old_id:
        record("identity_mismatch")
        safe.grab_focus()
    else:
        candidate.grab_focus()
    record("restore_returned")
    call_deferred("observe")

func observe() -> void:
    record("deferred_observation")
    observed = true

func _process(_delta: float) -> void:
    frames += 1
    if frames > 100:
        push_error("focus fixture watchdog")
        get_tree().quit(2)
    if observed:
        record("process_observation")
        print("RESULT_JSON=" + JSON.stringify({"mode": mode, "version": Engine.get_version_info(),
            "display_server": DisplayServer.get_name(), "old_id": old_id,
            "new_id": replacement.get_instance_id() if replacement != null else 0,
            "safe_id": safe.get_instance_id(), "close_id": close_button.get_instance_id(),
            "restore_count": restore_count, "revision": revision, "trace": trace}))
        get_tree().quit(0)
