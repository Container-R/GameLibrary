extends Node
# ALWAYS adapter; Gameplay child explicitly PAUSABLE, not inherited ALWAYS.
var stage: int = 0
var epoch: int = 0
var naive_queue: Array = []
var guarded_queue: Array = []
var inputs: Array = []
var trace: Array = []
var frames: int = 0
var pause_heartbeats: int = 0
var pause_tick: int = -1
var resume_tick: int = -1
var fresh_tick: int = -1
var naive_before_fresh: Array = []
var guarded_before_fresh: Array = []
@onready var gameplay: Node = $Gameplay

func _ready() -> void:
    InputMap.add_action(&"fixture_attack")
    Input.use_accumulated_input = false

func _input(event: InputEvent) -> void:
    if event is InputEventAction and event.action == &"fixture_attack":
        var label: String = event.get_meta("label")
        inputs.append({"label": label, "pressed": event.pressed,
            "paused": get_tree().paused, "epoch": epoch})
        if event.pressed:
            naive_queue.append({"label": label})
            guarded_queue.append({"label": label, "epoch": epoch})

func inject_pair(label: String) -> void:
    for pressed: bool in [true, false]:
        var event := InputEventAction.new()
        event.action = &"fixture_attack"
        event.pressed = pressed
        event.set_meta("label", label)
        Input.parse_input_event(event)
    # Explicit engine API flush, not sleeping for guessed input delivery latency.
    Input.flush_buffered_events()
    trace.append({"kind": "injected_pair", "label": label,
        "paused": get_tree().paused, "global_pressed": Input.is_action_pressed(&"fixture_attack")})

func transition_pause(paused: bool) -> void:
    # Product policy: both boundaries invalidate queued gameplay commands.
    epoch += 1
    guarded_queue.clear()
    get_tree().paused = paused
    trace.append({"kind": "pause_boundary", "paused": paused,
        "epoch": epoch, "gameplay_tick": gameplay.ticks})

func _physics_process(delta: float) -> void:
    if get_tree().paused:
        pause_heartbeats += 1
        trace.append({"kind": "paused_heartbeat", "count": pause_heartbeats,
            "gameplay_tick": gameplay.ticks, "delta": delta})

func _process(delta: float) -> void:
    frames += 1
    trace.append({"kind": "controller_process", "stage": stage,
        "paused": get_tree().paused, "gameplay_tick": gameplay.ticks, "delta": delta})
    if frames > 200:
        push_error("stage barrier watchdog")
        get_tree().quit(2)
        return
    match stage:
        0:
            if gameplay.ticks < 1:
                return
            inject_pair("pre_pause")
            transition_pause(true)
            pause_tick = gameplay.ticks
            inject_pair("during_pause")
            stage = 1
        1:
            # Observe actual fixed scheduling opportunities, not merely a main frame.
            if pause_heartbeats < 2:
                return
            trace.append({"kind": "pause_observation", "before": pause_tick,
                "after": gameplay.ticks, "queued_naive": naive_queue.size(),
                "queued_guarded": guarded_queue.size()})
            transition_pause(false)
            resume_tick = gameplay.ticks
            stage = 2
        2:
            if gameplay.ticks <= resume_tick:
                return
            naive_before_fresh = gameplay.naive_events.duplicate()
            guarded_before_fresh = gameplay.guarded_events.duplicate()
            inject_pair("fresh")
            fresh_tick = gameplay.ticks
            stage = 3
        3:
            if gameplay.ticks <= fresh_tick:
                return
            print("RESULT_JSON=" + JSON.stringify({"version": Engine.get_version_info(),
                "controller_mode": process_mode, "gameplay_mode": gameplay.process_mode,
                "accumulated_input": Input.use_accumulated_input,
                "physics_hz": Engine.physics_ticks_per_second, "paused_heartbeats": pause_heartbeats,
                "jitter_fix": Engine.physics_jitter_fix, "epoch": epoch,
                "controller_inputs": inputs, "gameplay_inputs": gameplay.inputs,
                "naive_before_fresh": naive_before_fresh,
                "guarded_before_fresh": guarded_before_fresh,
                "naive_events": gameplay.naive_events, "guarded_events": gameplay.guarded_events,
                "trace": trace, "process_callbacks": frames, "physics_callbacks": gameplay.ticks}))
            get_tree().quit(0)
