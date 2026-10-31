extends Node
# Original fixture: only this engine physics callback advances the integer core.
const END_TICK: int = 120
const AXES: Dictionary = {0: 1, 30: -1, 90: 0}
const PRESSES: Array[int] = [6, 8, 9]
var tick: int = 0
var x: int = 0
var axis: int = 0
var previous_x: int = 0
var events: Array[int] = []
var tick_states: Array = []
var frames: Array = []
var physics_deltas: Array[float] = []
var steps_since_present: int = 0
var read_only_ok: bool = true

func _physics_process(delta: float) -> void:
    if tick >= END_TICK:
        push_error("unexpected extra physics callback")
        get_tree().quit(2)
        return
    physics_deltas.append(delta)
    previous_x = x
    if AXES.has(tick):
        axis = AXES[tick]
    x += axis
    # An intentionally simple half-open attack eligibility window.
    if tick in PRESSES and tick >= 6 and tick < 9:
        events.append(tick)
    tick_states.append([tick, x, axis, events.duplicate()])
    tick += 1
    steps_since_present += 1
    if tick == END_TICK:
        set_physics_process(false)

func _process(delta: float) -> void:
    var before: Array = [tick, x, axis, previous_x, events.duplicate()]
    # Numeric presentation only. No rendering, physics body or device input.
    var alpha: float = clampf(Engine.get_physics_interpolation_fraction(), 0.0, 1.0)
    var presentation_x: float = lerpf(float(previous_x), float(x), alpha)
    read_only_ok = read_only_ok and before == [tick, x, axis, previous_x, events.duplicate()]
    frames.append({"delta": delta, "steps": steps_since_present, "tick": tick,
        "alpha": alpha, "presentation_x": presentation_x})
    steps_since_present = 0
    if tick == END_TICK:
        var result: Dictionary = {"version": Engine.get_version_info(),
            "physics_ticks_per_second": Engine.physics_ticks_per_second,
            "max_physics_steps_per_frame": Engine.max_physics_steps_per_frame,
            "physics_jitter_fix": Engine.physics_jitter_fix,
            "time_scale": Engine.time_scale, "ticks": tick, "x": x, "axis": axis,
            "events": events, "read_only_ok": read_only_ok,
            "frames": frames, "physics_deltas": physics_deltas, "tick_states": tick_states}
        print("RESULT_JSON=" + JSON.stringify(result))
        get_tree().quit(0)
