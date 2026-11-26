extends SceneTree

var events: Dictionary = {}
var tick: int = 0
var naive_active: bool = true
var guarded_active: bool = true
var lease: int = 17
var stale_events: int = 0

func _initialize() -> void:
	run.call_deferred()

func add_probe(label: String, once: bool) -> CPUParticles2D:
	var p := CPUParticles2D.new()
	p.name = label
	p.emitting = false
	p.one_shot = once
	p.lifetime = 0.3
	p.amount = 8
	p.explosiveness = 0.0
	p.randomness = 0.0
	p.use_fixed_seed = true
	p.seed = 123
	p.finished.connect(func():
		events[label].append(tick)
		print("%s t=%d finished emitting=%s" % [label, tick, p.emitting]))
	events[label] = []
	root.add_child(p)
	p.restart()
	return p

func complete_old(expected: int) -> void:
	naive_active = false
	if guarded_active and lease == expected:
		guarded_active = false
	else:
		stale_events += 1
	print("old timer t=%d requested=%d current=%d naive_active=%s guarded_active=%s" % [
		tick, expected, lease, naive_active, guarded_active])

func run() -> void:
	var natural := add_probe("natural_once", true)
	var stopped := add_probe("stop_once", true)
	var loop := add_probe("stop_loop", false)
	var replay := add_probe("restart_once", true)
	var bound := lease
	create_timer(0.24).timeout.connect(complete_old.bind(bound))
	var first_natural_off := -1
	for i in range(1, 90):
		await process_frame
		tick = i
		if not natural.emitting and first_natural_off == -1:
			first_natural_off = tick
			print("natural_once t=%d first emitting=false" % tick)
		if i == 6:
			stopped.emitting = false
			loop.emitting = false
			print("explicit stop t=%d once=%s loop=%s signals=%d/%d" % [
				tick, stopped.emitting, loop.emitting, events["stop_once"].size(), events["stop_loop"].size()])
		if i == 10:
			lease += 1
			replay.restart()
			print("reacquire t=%d lease=%d restart_once emitting=%s" % [tick, lease, replay.emitting])
	var ok: bool = (events["natural_once"].size() == 1
		and first_natural_off > 0 and events["natural_once"][0] > first_natural_off
		and events["stop_once"].size() == 1 and events["stop_once"][0] > 6
		and events["stop_loop"].size() == 1 and events["stop_loop"][0] > 6
		and events["restart_once"].size() == 1 and events["restart_once"][0] > events["natural_once"][0]
		and stale_events == 1 and not naive_active and guarded_active)
	print("summary ok=%s" % ok)
	quit(0 if ok else 1)
