extends SceneTree

func vectors(values):
	var output = []
	if values != null:
		for value in values:
			output.append([value.x, value.y, value.z])
	return output

func surface_data(mesh, importer: bool):
	var surfaces = []
	for i in range(mesh.get_surface_count()):
		var a = mesh.get_surface_arrays(i) if importer else mesh.surface_get_arrays(i)
		var uv = a[Mesh.ARRAY_TEX_UV]
		surfaces.append({
			"primitive": mesh.get_surface_primitive_type(i) if importer else mesh.surface_get_primitive_type(i),
			"positions": vectors(a[Mesh.ARRAY_VERTEX]),
			"normals": vectors(a[Mesh.ARRAY_NORMAL]),
			"indices": Array(a[Mesh.ARRAY_INDEX]),
			"uv_type": type_string(typeof(uv)),
			"uv_count": 0 if uv == null else uv.size(),
			"position_type": type_string(typeof(a[Mesh.ARRAY_VERTEX])),
			"normal_type": type_string(typeof(a[Mesh.ARRAY_NORMAL])),
			"index_type": type_string(typeof(a[Mesh.ARRAY_INDEX]))
		})
	return {"class": mesh.get_class(), "surfaces": surfaces}

func _initialize():
	var doc = GLTFDocument.new()
	var state = GLTFState.new()
	var code = doc.append_from_file("res://mesh.gltf", state, 0, "res://")
	print("IMPORT_RETURN_CODE=" + str(code))
	var result = {"import_return_code": code, "engine_version": Engine.get_version_info()}
	result["state"] = {"meshes": state.get_meshes().size(), "nodes": state.get_nodes().size(), "accessors": state.get_accessors().size(), "buffer_views": state.get_buffer_views().size(), "buffer_lengths": []}
	for buffer in state.get_buffers():
		result["state"]["buffer_lengths"].append(buffer.size())
	if code != OK or state.get_meshes().size() != 1:
		print("RESULT_JSON=" + JSON.stringify(result))
		quit(2)
		return
	var gltf_mesh = state.get_meshes()[0]
	result["gltf_mesh_class"] = gltf_mesh.get_class()
	var importer = gltf_mesh.mesh
	if importer == null:
		print("RESULT_JSON=" + JSON.stringify(result))
		quit(3)
		return
	result["importer"] = surface_data(importer, true)
	var array_mesh = importer.get_mesh()
	result["array_mesh_null"] = array_mesh == null
	if array_mesh == null:
		print("RESULT_JSON=" + JSON.stringify(result))
		quit(4)
		return
	result["array_mesh"] = surface_data(array_mesh, false)
	result["array_mesh"]["surface_format"] = str(array_mesh.surface_get_format(0))
	var bounds = array_mesh.get_aabb()
	result["array_mesh"]["aabb"] = {"position": [bounds.position.x, bounds.position.y, bounds.position.z], "size": [bounds.size.x, bounds.size.y, bounds.size.z]}
	print("RESULT_JSON=" + JSON.stringify(result))
	quit(0)
