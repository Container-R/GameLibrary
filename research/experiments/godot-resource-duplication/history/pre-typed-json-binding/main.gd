extends SceneTree

func ident(object):
	return str(object.get_instance_id())

func gradient(resource):
	var colors = []
	var offsets = []
	for index in range(resource.get_point_count()):
		var c = resource.get_color(index)
		colors.append([c.r, c.g, c.b, c.a])
		offsets.append(resource.get_offset(index))
	return {"id": ident(resource), "class": resource.get_class(), "count": resource.get_point_count(), "colors": colors, "offsets": offsets}

func graph(root):
	return {"root_id": ident(root), "script_id": ident(root.get_script()), "length": root.entries.size(),
		"first3_ids": [ident(root.entries[0]), ident(root.entries[1]), ident(root.entries[2])],
		"slot3": root.entries[3] if root.entries.size() == 4 else null,
		"values": [gradient(root.entries[0]), gradient(root.entries[1]), gradient(root.entries[2])]}

func metadata(resource):
	return {"id": ident(resource), "class": resource.get_class(), "path": resource.resource_path,
		"built_in": resource.is_built_in(), "local_to_scene": resource.resource_local_to_scene}

func snapshot(label, a, a2, d, b, c, cc):
	return {"stage": label, "a": graph(a), "a2": graph(a2), "d": graph(d),
		"cached_root_id": ident(ResourceLoader.get_cached_ref("res://config.tres")),
		"held_b": gradient(b), "held_c": gradient(c), "cached_c": gradient(cc),
		"same_array": is_same(a.entries, d.entries)}


func valid_gradient(resource, first):
	if not resource is Gradient or resource.get_point_count() != 2:
		return false
	return resource.get_offset(0) == 0.0 and resource.get_offset(1) == 1.0 and resource.get_color(0) == first and resource.get_color(1) == Color(1, 1, 1, 1)

func reject(message):
	push_error(message)
	quit(1)

func _initialize():
	var args = OS.get_cmdline_user_args()
	if args.size() != 2 or not args[0] in ["shallow", "internal", "all"]:
		push_error("exact mode and invocation UUID required")
		quit(1)
		return
	var mode = args[0]
	var a = ResourceLoader.load("res://config.tres", "", ResourceLoader.CACHE_MODE_REUSE)
	var a2 = ResourceLoader.load("res://config.tres", "", ResourceLoader.CACHE_MODE_REUSE)
	if a == null or a2 == null or not a.get("entries") is Array or a.entries.size() != 3:
		push_error("input root unavailable or malformed")
		quit(1)
		return
	var b = a.entries[0]
	var c = a.entries[2]
	var cc = ResourceLoader.get_cached_ref("res://external.tres")
	var property_record = {}
	for entry in a.get_property_list():
		if entry["name"] == "entries":
			property_record = {"name": str(entry["name"]), "type": entry["type"], "usage": entry["usage"]}
	# Fail before any duplication or payload edit if the assumed input graph differs.
	if a != a2 or a != ResourceLoader.get_cached_ref("res://config.tres") or a.entries[1] != b or c != cc:
		reject("baseline live identity mismatch")
		return
	if not valid_gradient(b, Color(1, 0, 0, 1)) or not valid_gradient(c, Color(0, 1, 0, 1)):
		reject("baseline Gradient type/value mismatch")
		return
	if a.get_class() != "Resource" or a.get_script() == null or a.get_script().resource_path != "res://config.gd":
		reject("native class/script mismatch")
		return
	if a.resource_path != "res://config.tres" or not b.resource_path.begins_with("res://config.tres::") or not b.is_built_in() or c.resource_path != "res://external.tres" or c.is_built_in():
		reject("baseline resource path classification mismatch")
		return
	if a.resource_local_to_scene or b.resource_local_to_scene or c.resource_local_to_scene or a.entries.is_typed():
		reject("scene-local/typed-array input outside protocol")
		return
	if property_record.is_empty() or property_record.type != TYPE_ARRAY or (property_record.usage & PROPERTY_USAGE_STORAGE) == 0 or (property_record.usage & (PROPERTY_USAGE_ALWAYS_DUPLICATE | PROPERTY_USAGE_NEVER_DUPLICATE)) != 0:
		reject("entries storage flags mismatch")
		return
	var result = {"schema": 1, "invocation_uuid": args[1], "mode": mode, "process_id": OS.get_process_id(),
		"engine_version": Engine.get_version_info(),
		"constants": {"type_array": TYPE_ARRAY, "storage": PROPERTY_USAGE_STORAGE,
			"always": PROPERTY_USAGE_ALWAYS_DUPLICATE, "never": PROPERTY_USAGE_NEVER_DUPLICATE,
			"none": Resource.DEEP_DUPLICATE_NONE, "internal": Resource.DEEP_DUPLICATE_INTERNAL, "all": Resource.DEEP_DUPLICATE_ALL},
		"setup": {"property": property_record, "typed_array": a.entries.is_typed(),
			"a": metadata(a), "b": metadata(b), "c": metadata(c),
			"script_path": a.get_script().resource_path, "a_graph": graph(a), "a2_graph": graph(a2),
			"held_b": gradient(b), "held_c": gradient(c), "cached_c": gradient(cc),
			"cached_root_id": ident(ResourceLoader.get_cached_ref("res://config.tres"))}, "stages": []}
	var d
	if mode == "shallow":
		d = a.duplicate(false)
	elif mode == "internal":
		d = a.duplicate(true)
	else:
		d = a.duplicate_deep(Resource.DEEP_DUPLICATE_ALL)
	if d == null:
		push_error("duplicate returned null")
		quit(1)
		return
	if d == a or not d.get("entries") is Array or d.entries.size() != 3 or d.get_script() != a.get_script():
		reject("duplicate root/array/script shape mismatch before mutation")
		return
	if d.entries[0] != d.entries[1] or not valid_gradient(d.entries[0], Color(1, 0, 0, 1)) or not valid_gradient(d.entries[2], Color(0, 1, 0, 1)):
		reject("duplicate payload shape mismatch before mutation")
		return
	result.stages.append(snapshot("copied", a, a2, d, b, c, cc))
	d.entries.append(137)
	result.stages.append(snapshot("append", a, a2, d, b, c, cc))
	d.entries[0].set_color(0, Color(0, 0, 1, 1))
	result.stages.append(snapshot("internal_edit", a, a2, d, b, c, cc))
	d.entries[2].set_color(0, Color(1, 0, 1, 1))
	result.stages.append(snapshot("external_edit", a, a2, d, b, c, cc))
	print("RESULT_JSON:" + JSON.stringify(result))
	quit(0)
