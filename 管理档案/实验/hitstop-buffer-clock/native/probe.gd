extends SceneTree

class Receiver extends Node:
	var log: Array[Dictionary] = []

	func _input(event: InputEvent) -> void:
		if event.has_meta("fixture_event_ms"):
			log.append({
				"clock_usec": Time.get_ticks_usec(),
				"source_ms": int(event.get_meta("fixture_event_ms"))
			})

func _initialize() -> void:
	run.call_deferred()

func run() -> void:
	var receiver := Receiver.new()
	root.add_child(receiver)
	Input.use_accumulated_input = true
	var results: Array[int] = []
	for n in [0, 50]:
		var req := InputEventKey.new()
		req.physical_keycode = KEY_K
		req.pressed = true
		req.set_meta("fixture_event_ms", 85)
		var before := Time.get_ticks_usec()
		Input.parse_input_event(req)
		var count_before_flush := receiver.log.size()
		if n > 0:
			OS.delay_msec(n) # No frame boundary or automatic flush in this probe.
		Input.flush_buffered_events()
		var count_after_flush := receiver.log.size()
		if count_before_flush != results.size() or count_after_flush != results.size() + 1:
			printerr("unexpected callback count: ", count_before_flush, "/", count_after_flush)
			quit(1)
			return
		var rec := receiver.log.back() as Dictionary
		if rec["source_ms"] != 85:
			quit(1)
			return
		var elapsed := int(rec["clock_usec"]) - before
		results.append(elapsed)
		print("explicit_wait_ms=%d fixed_fixture_event_ms=%d callbacks_before=%d callbacks_after=%d elapsed_bucket=%s" %
			[n, rec["source_ms"], count_before_flush, count_after_flush,
			"gte_50ms" if elapsed >= 50000 else "lt_50ms"])
	var ok := results[1] >= 50000 and results[1] > results[0]
	print("same_fixture_stamp=true delayed_receipt_observed=%s" % ok)
	quit(0 if ok else 1)
