extends SceneTree

func _initialize() -> void:
	run.call_deferred()

func measure(ts: TextServer, content: String, fonts: Array[RID], thai: RID) -> Array:
	var line := ts.create_shaped_text()
	assert(ts.shaped_text_add_string(line, content, fonts, 32))
	assert(ts.shaped_text_shape(line))
	var used_thai := 0
	var used_latin := 0
	var missing := 0
	for item in ts.shaped_text_get_glyphs(line):
		missing += int(item.index == 0 or not item.font_rid.is_valid())
		used_thai += int(item.font_rid == thai)
		used_latin += int(item.font_rid == fonts[0])
	var out := [ts.shaped_text_get_ascent(line),ts.shaped_text_get_descent(line),used_latin,used_thai,missing]
	ts.free_rid(line)
	return out

func run() -> void:
	var argv := OS.get_cmdline_user_args()
	if argv.size() != 2:
		push_error("Supply Latin and Thai font paths after --")
		quit(1)
		return
	var latin := FontFile.new()
	var thai := FontFile.new()
	assert(latin.load_dynamic_font(argv[0]) == OK)
	assert(thai.load_dynamic_font(argv[1]) == OK)
	var l := latin.get_rids()[0]
	var t := thai.get_rids()[0]
	var ts := TextServerManager.get_primary_interface()
	ts.font_set_allow_system_fallback(l, false)
	ts.font_set_allow_system_fallback(t, false)
	print("text server: ", ts.get_name())
	print("metrics: ascent,descent,latin glyphs,thai glyphs,missing")
	var pure := measure(ts,"Ag",[l,t],t)
	var mix := measure(ts,"Ag กิ๊ กุ",[l,t],t)
	print("latin: ",pure)
	print("mixed: ",mix)
	var ok: bool = pure[2]>0 and pure[3]==0 and pure[4]==0 and mix[2]>0 and mix[3]>0 and mix[4]==0 and (mix[0]>pure[0] or mix[1]>pure[1])
	quit(0 if ok else 1)
