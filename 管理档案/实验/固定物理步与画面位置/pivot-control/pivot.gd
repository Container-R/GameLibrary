extends SceneTree

class Rig extends Node3D:
	const RADIUS := 4.0
	const STEP := PI / 6.0
	const SHIFT := Vector3(0.24, 0.10, 0.0)
	var arm := Node3D.new()
	var marker := Node3D.new()
	var tick := 0
	var count := 0
	var min_chord := RADIUS
	var max_rigid_error := 0.0
	var max_composed_error := 0.0
	var midpoints := 0

	func _ready() -> void:
		add_child(arm)
		marker.position = Vector3(RADIUS, 0.0, 0.0)
		arm.add_child(marker)
		arm.reset_physics_interpolation()
		print("tick alpha api_radius chord_radius api_vs_composed")

	func pose(n: int) -> Transform3D:
		return Transform3D(Basis(Vector3.BACK, n * STEP), n * SHIFT)

	func _physics_process(_dt: float) -> void:
		tick += 1
		arm.transform = pose(tick)

	func _process(_dt: float) -> void:
		var p := arm.get_global_transform_interpolated()
		var m := marker.get_global_transform_interpolated()
		if tick < 2:
			return
		var alpha := Engine.get_physics_interpolation_fraction()
		var a := pose(tick - 1)
		var b := pose(tick)
		var chord := (a * marker.position).lerp(b * marker.position, alpha)
		var measured_radius := p.origin.distance_to(m.origin)
		var chord_radius := a.origin.lerp(b.origin, alpha).distance_to(chord)
		var composed_error := m.origin.distance_to(p * marker.position)
		min_chord = minf(min_chord, chord_radius)
		max_rigid_error = maxf(max_rigid_error, absf(measured_radius - RADIUS))
		max_composed_error = maxf(max_composed_error, composed_error)
		if absf(alpha - 0.5) < 0.00001:
			midpoints += 1
			print("%d %.6f %.6f %.6f %.6f" % [tick, alpha, measured_radius, chord_radius, composed_error])
		count += 1
		if count == 24:
			print("samples=%d midpoints=%d min_chord=%.6f max_rigid_error=%.6f max_composed_error=%.6f" % [count, midpoints, min_chord, max_rigid_error, max_composed_error])
			var pass_test := midpoints > 0 and absf(min_chord - RADIUS * cos(STEP / 2.0)) < 0.0001 and max_rigid_error < 0.0001 and max_composed_error < 0.0001
			get_tree().quit(0 if pass_test else 1)

func _initialize() -> void:
	root.add_child.call_deferred(Rig.new())
