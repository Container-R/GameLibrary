extends SceneTree

class PositionPass extends SkeletonModifier3D:
	var bone: int
	var target: Transform3D
	func _process_modification_with_delta(_delta: float) -> void:
		get_skeleton().set_bone_global_pose(bone, target)

class FollowPass extends SkeletonModifier3D:
	var primary: int
	var wrist: int
	var grip_local: Transform3D
	var palm_local: Transform3D
	func _process_modification_with_delta(_delta: float) -> void:
		var s := get_skeleton()
		var grip := s.get_bone_global_pose(primary) * grip_local
		s.set_bone_global_pose(wrist, grip * palm_local.affine_inverse())

class LatePass extends SkeletonModifier3D:
	var bone: int
	func _process_modification_with_delta(_delta: float) -> void:
		var s := get_skeleton()
		var t := s.get_bone_global_pose(bone)
		t.origin += Vector3(0.06, -0.08, 0)
		s.set_bone_global_pose(bone, t)

var stage := 0
var grip_local := Transform3D(Basis.IDENTITY, Vector3(0, 0.30, 0))
var palm_local := Transform3D(Basis.IDENTITY, Vector3(0.04, 0, 0))
var sk := Skeleton3D.new()

func check(expected: Vector3, label: String) -> void:
	var wrist := sk.get_bone_global_pose(1)
	var desired := sk.get_bone_global_pose(0) * grip_local
	var palm := wrist * palm_local
	assert(wrist.origin.is_equal_approx(expected))
	var loc := roundi(wrist.origin.x * 100)
	var height := roundi(wrist.origin.y * 100)
	print("%s: wrist=(%d,%d) cm; palm error=%.2f cm" % [label, loc,height,palm.origin.distance_to(desired.origin)*100.0])

func _init() -> void:
	call_deferred("run")

func run() -> void:
	sk.modifier_callback_mode_process = Skeleton3D.MODIFIER_CALLBACK_MODE_PROCESS_MANUAL
	sk.add_bone("primary")
	sk.add_bone("support_wrist")
	sk.set_bone_pose_position(1,Vector3(0.01,0.02,0))
	sk.transform = Transform3D(Basis(Vector3.BACK,PI/2),Vector3(0.07,0.09,0))
	var primary := PositionPass.new()
	primary.bone = 0
	primary.target = Transform3D(Basis(Vector3.BACK, PI/2),Vector3(0.10,0,0))
	sk.add_child(primary)
	var follow := FollowPass.new()
	follow.primary = 0
	follow.wrist = 1
	follow.grip_local = grip_local
	follow.palm_local = palm_local
	sk.add_child(follow)
	var late := LatePass.new()
	late.bone = 1
	sk.add_child(late)
	root.add_child(sk)
	await process_frame
	follow.modification_processed.connect(func():
		assert(stage == 0)
		stage = 1
		check(Vector3(-0.20,-0.04,0),"after support pass")
	)
	sk.skeleton_updated.connect(func():
		assert(stage == 1)
		stage = 2
		check(Vector3(-0.14,-0.12,0),"final skeleton")
		call_deferred("outside")
	)
	sk.advance(0.0)

func outside() -> void:
	assert(stage == 2)
	var base := sk.get_bone_global_pose(1)
	assert(base.origin.is_equal_approx(Vector3(0.01,0.02,0)))
	print("after deferred update: restored base wrist=(1,2) cm")
	quit()
