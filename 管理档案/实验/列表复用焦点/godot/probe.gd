extends SceneTree

var ui: Control
var parking: Control
var slots: Array[Button] = []
var logical = "B"
var pending = false
var guarded = false
var serial = 0
var guard_press = false
var armed: Dictionary = {}
var actions: Array[String] = []
var observed: Dictionary = {}

func _initialize() -> void:
    run.call_deferred()

func sample() -> Dictionary:
    var control := root.gui_get_focus_owner()
    return {
        "logical": logical,
        "node": String(control.name) if control else "none",
        "bound_item": String(control.get_meta("item", "")) if control else "",
        "pending": pending
    }

func bind(slot: Button, item: String) -> void:
    slot.set_meta("generation", int(slot.get_meta("generation", 0)) + 1)
    slot.set_meta("item", item)
    slot.text = "Item " + item

func arm(slot: Button) -> void:
    armed = {"slot": slot, "item": String(slot.get_meta("item", "")),
             "gen": int(slot.get_meta("generation", 0)), "intent": serial}

func on_pressed(slot: Button) -> void:
    var item := String(slot.get_meta("item", ""))
    if guarded and (pending or item != logical or root.gui_get_focus_owner() != slot):
        return
    if guard_press and (armed.get("slot") != slot or armed.get("item") != item
            or armed.get("gen") != int(slot.get_meta("generation", 0)) or armed.get("intent") != serial):
        armed.clear()
        return
    armed.clear()
    actions.append(item)

func key_edge(down: bool) -> void:
    var event := InputEventAction.new()
    event.action = &"ui_accept"
    event.pressed = down
    Input.parse_input_event(event)
    await process_frame

func accept_action() -> void:
    await key_edge(true)
    await key_edge(false)

func move_logical(item: String, slot: Button) -> void:
    serial += 1
    logical = item
    pending = false
    slot.grab_focus()

func finish_scroll(token: int, expected: String, slot: Button, binding_generation: int) -> bool:
    if token != serial or logical != expected or not pending:
        return false
    if String(slot.get_meta("item", "")) != expected or int(slot.get_meta("generation", 0)) != binding_generation:
        return false
    slot.grab_focus()
    pending = root.gui_get_focus_owner() != slot
    return not pending

func run() -> void:
    ui = Control.new()
    root.add_child(ui)
    parking = Control.new()
    parking.name = &"ListSurface"
    parking.focus_mode = Control.FOCUS_ALL
    ui.add_child(parking)
    for i in range(2):
        var row := Button.new()
        row.name = "Slot" + str(i)
        row.position = Vector2(5, 36*i+10)
        row.size = Vector2(100,32)
        row.focus_mode = Control.FOCUS_ALL
        ui.add_child(row)
        slots.append(row)
        row.action_mode = BaseButton.ACTION_MODE_BUTTON_RELEASE
        row.button_down.connect(arm.bind(row))
        row.pressed.connect(on_pressed.bind(row))
    await process_frame

    bind(slots[0], "A")
    bind(slots[1], "B")
    slots[1].grab_focus()
    await accept_action()
    assert(actions == ["B"])
    observed["baseline"] = [sample(), actions.duplicate()]

    # Slot1 still has real focus, but the scroller reassigns it from B to D.
    bind(slots[0], "C")
    bind(slots[1], "D")
    await accept_action()
    assert(root.gui_get_focus_owner() == slots[1] and actions == ["B","D"])
    observed["unstyled_rebind"] = [sample(), actions.duplicate()]

    guarded = true
    actions.clear()
    bind(slots[0], "A")
    bind(slots[1], "B")
    move_logical("B", slots[1])
    pending = true
    serial += 1
    var scroll_token = serial
    parking.grab_focus()
    bind(slots[0], "C")
    bind(slots[1], "D")
    await accept_action()
    assert(actions.is_empty() and root.gui_get_focus_owner() == parking)
    observed["pending_rebind"] = [sample(), actions.duplicate()]

    # A later explicit move takes precedence before the old scroll completes.
    move_logical("C", slots[0])
    bind(slots[1], "B")
    var accepted_old = finish_scroll(scroll_token, "B", slots[1], int(slots[1].get_meta("generation")))
    await accept_action()
    assert(not accepted_old and actions == ["C"])
    observed["late_scroll_after_new_intent"] = [sample(), accepted_old, actions.duplicate()]

    # One target B persists, but the row went B -> X -> B during async work.
    parking.grab_focus()
    logical = "B"
    serial += 1
    pending = true
    var intent = serial
    var stale_binding = int(slots[1].get_meta("generation"))
    bind(slots[1], "X")
    bind(slots[1], "B")
    var accepted_stale = finish_scroll(intent, "B", slots[1], stale_binding)
    var accepted_current = finish_scroll(intent, "B", slots[1], int(slots[1].get_meta("generation")))
    await accept_action()
    assert(not accepted_stale and accepted_current and actions == ["C","B"])
    observed["same_item_new_binding"] = [sample(), accepted_stale, accepted_current, actions.duplicate()]

    # A key was already down when a view update reuses the same focused widget.
    actions.clear()
    bind(slots[1], "B")
    move_logical("B", slots[1])
    await key_edge(true)
    assert(actions.is_empty() and armed["item"] == "B")
    bind(slots[1], "D")
    move_logical("D", slots[1])
    await key_edge(false)
    assert(actions == ["D"])
    observed["half_press_only_checks_release"] = [sample(), actions.duplicate()]

    guard_press = true
    actions.clear()
    bind(slots[1], "B")
    move_logical("B", slots[1])
    await key_edge(true)
    bind(slots[1], "D")
    move_logical("D", slots[1])
    await key_edge(false)
    assert(actions.is_empty())
    observed["half_press_cancels_stale_release"] = [sample(), actions.duplicate()]
    await accept_action()
    assert(actions == ["D"])
    observed["fresh_press_on_new_row"] = [sample(), actions.duplicate()]

    print("OBSERVED ", JSON.stringify(observed))
    quit()
