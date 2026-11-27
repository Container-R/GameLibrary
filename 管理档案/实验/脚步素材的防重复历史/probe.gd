extends SceneTree

func wav(frames: int) -> AudioStreamWAV:
	var s := AudioStreamWAV.new()
	s.format = AudioStreamWAV.FORMAT_8_BITS
	s.mix_rate = 8000
	var data := PackedByteArray()
	data.resize(frames)
	s.data = data
	return s

func randomizer(a: AudioStream, b: AudioStream) -> AudioStreamRandomizer:
	var r := AudioStreamRandomizer.new()
	r.playback_mode = AudioStreamRandomizer.PLAYBACK_RANDOM_NO_REPEATS
	r.add_stream(0, a, 9.0)
	r.add_stream(1, b, 1.0)
	return r

func pick(r: AudioStreamRandomizer) -> int:
	var playback := r.instantiate_playback()
	assert(playback != null)
	return roundi(r.get_length() * 8000)

func _init() -> void:
	var a := wav(800)
	var b := wav(1600)
	var shared := randomizer(a,b)
	var first := pick(shared) # logically A
	var second := pick(shared) # logically B, same resource
	var third := pick(shared) # A again
	assert(first != second and first == third)
	print("shared resource: A repeats, adjacent resource calls alternate")
	var ra := randomizer(a,b)
	var rb := randomizer(a,b)
	first = pick(ra)
	pick(rb)
	assert(first != pick(ra))
	print("separate resources: A's second call avoids A's first")
	var dup := randomizer(a,a)
	assert(pick(dup) == 800 and pick(dup) == 800)
	print("duplicate child resource: two entries can yield the same sound")
	var never_started := randomizer(a,b)
	first = pick(never_started)
	assert(first != pick(never_started))
	print("instantiate without start: still advances history")
	var counts := {800:0,1600:0}
	for index in range(100):
		var selected := pick(ra)
		counts[selected] += 1
	assert(counts == {800:50,1600:50})
	print("9:1 weights, 100 strict alternating selections: 50/50")
	quit()
