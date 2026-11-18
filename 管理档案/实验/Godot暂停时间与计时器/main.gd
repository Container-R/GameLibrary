extends Node

var events: Dictionary = {}
var start_ms: int
var fired_counts: Dictionary = {}
var paused_process_calls := 0
var active_process_calls := 0

func _process(_delta: float) -> void:
    if get_tree().paused:
        paused_process_calls += 1
    else:
        active_process_calls += 1

func timer(label: String, during_pause: bool, unscaled: bool) -> void:
    get_tree().create_timer(0.08, during_pause, false, unscaled).timeout.connect(func():
        events[label] = get_tree().paused
        fired_counts[label] = fired_counts.get(label, 0) + 1
        print("timeout=", label, " paused=", get_tree().paused, " elapsed_ms=", Time.get_ticks_msec() - start_ms)
    )

func check(ok: bool, phase: String) -> bool:
    print("check=", phase, " ok=", ok)
    if not ok:
        get_tree().quit(1)
    return ok

func _ready() -> void:
    var tree := get_tree()
    await tree.process_frame
    await tree.process_frame
    Engine.time_scale = 0.05
    tree.paused = true
    start_ms = Time.get_ticks_msec()
    timer("always_unscaled", true, true)
    timer("always_scaled", true, false)
    timer("pause_unscaled", false, true)
    timer("pause_scaled", false, false)
    await tree.create_timer(0.25, true, false, true).timeout
    if not check(events == {"always_unscaled": true}, "short_pause"):
        return
    await tree.create_timer(1.75, true, false, true).timeout
    if not check(events == {"always_unscaled": true, "always_scaled": true}, "long_pause"):
        return
    tree.paused = false
    await tree.create_timer(0.30, true, false, true).timeout
    if not check(events == {"always_unscaled": true, "always_scaled": true, "pause_unscaled": false}, "resume_still_slow"):
        return
    Engine.time_scale = 1.0
    await tree.create_timer(0.30, true, false, true).timeout
    if not check(events == {"always_unscaled": true, "always_scaled": true, "pause_unscaled": false, "pause_scaled": false}, "resume"):
        return
    if not check(paused_process_calls == 0 and active_process_calls > 0, "node_process_active_but_not_while_paused"):
        return
    if not check(fired_counts == {"always_unscaled": 1, "always_scaled": 1, "pause_unscaled": 1, "pause_scaled": 1}, "once_each"):
        return
    tree.quit(0)
