extends SceneTree

class Probe extends Node3D:
	const DX := 0.12
	const OFFSET := 2.0
	const TELEPORT := 100.0
	const JUMP_TICK := 120
	var target := Node3D.new()
	var smooth_jump := Node3D.new()
	var cut_jump := Node3D.new()
	var tick := 0
	var process_index := 0
	var previous_held := 0.0
	var previous_view := 0.0
	var held_buckets := {}
	var view_buckets := {}
	var max_same_basis_error := 0.0
	var min_mixed := INF
	var max_mixed := -INF
	var jump_blend_error := INF
	var jump_cut_error := INF

	func _ready() -> void:
		for marker in [target, smooth_jump, cut_jump]:
			add_child(marker)
			marker.reset_physics_interpolation()
		print("frame tick alpha latest view held_dx view_dx mixed_relative same_relative")

	func _physics_process(_dt: float) -> void:
		tick += 1
		target.position.x = tick * DX
		if tick == JUMP_TICK:
			smooth_jump.position.x = TELEPORT
			cut_jump.position.x = TELEPORT
			cut_jump.reset_physics_interpolation()

	func _process(_dt: float) -> void:
		var held := target.global_position.x
		var view := target.get_global_transform_interpolated().origin.x
		var no_cut := smooth_jump.get_global_transform_interpolated().origin.x
		var cut := cut_jump.get_global_transform_interpolated().origin.x
		var alpha := Engine.get_physics_interpolation_fraction()
		var mixed := view - (held - OFFSET)
		var same := view - (view - OFFSET)
		if tick == JUMP_TICK:
			jump_blend_error = absf(no_cut - TELEPORT * alpha)
			jump_cut_error = absf(cut - TELEPORT)
			print("teleport alpha=%.6f no_cut=%.6f cut=%.6f" % [alpha, no_cut, cut])
		if tick > JUMP_TICK:
			print("held_deltas=%s interp_deltas=%s mixed=[%.6f,%.6f] same_error=%.6f" % [held_buckets, view_buckets, min_mixed, max_mixed, max_same_basis_error])
			var ok := held_buckets.size() == 2 and held_buckets.has("0.00") and held_buckets.has("0.12") and view_buckets.size() == 1 and view_buckets.has("0.10") and max_mixed - min_mixed > 0.09 and max_same_basis_error < 0.0001 and jump_blend_error < 0.0001 and jump_cut_error < 0.0001
			get_tree().quit(0 if ok else 1)
		if process_index >= 13 and process_index <= 132:
			var dh := held - previous_held
			var dv := view - previous_view
			var held_key := "%.2f" % dh
			var view_key := "%.2f" % dv
			held_buckets[held_key] = held_buckets.get(held_key, 0) + 1
			view_buckets[view_key] = view_buckets.get(view_key, 0) + 1
			max_same_basis_error = maxf(max_same_basis_error, absf(same - OFFSET))
			min_mixed = minf(min_mixed, mixed)
			max_mixed = maxf(max_mixed, mixed)
			if process_index <= 24:
				print("%d %d %.6f %.6f %.6f %.6f %.6f %.6f %.6f" % [process_index, tick, alpha, held, view, dh, dv, mixed, same])
		previous_held = held
		previous_view = view
		process_index += 1

func _initialize() -> void:
	root.add_child.call_deferred(Probe.new())
