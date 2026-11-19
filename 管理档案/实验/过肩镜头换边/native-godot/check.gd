extends SceneTree

const LEFT := Vector3(-1, 0, 3)
const RIGHT := Vector3(1, 0, 3)
const VIA := Vector3(0, 0, 2)
const FOCUS := Vector3(0, 0, -5)

func _initialize() -> void:
    call_deferred("run")

func add_prop(space: Node3D, where: Vector3, radius: float, layer: int) -> void:
    var body := StaticBody3D.new()
    body.position = where
    body.collision_layer = layer
    var col := CollisionShape3D.new()
    var s := SphereShape3D.new()
    s.radius = radius
    col.shape = s
    body.add_child(col)
    space.add_child(body)

func add_arm(space: Node3D, x: float, proxy: SphereShape3D) -> SpringArm3D:
    var arm := SpringArm3D.new()
    arm.position.x = x
    arm.spring_length = 3
    arm.collision_mask = 1
    arm.shape = proxy
    var view := Camera3D.new()
    arm.add_child(view)
    space.add_child(arm)
    return arm

func cast_clear(state: PhysicsDirectSpaceState3D, shape: Shape3D, a: Vector3, b: Vector3) -> bool:
    var p := PhysicsShapeQueryParameters3D.new()
    p.shape = shape
    p.transform = Transform3D(Basis.IDENTITY, a)
    p.motion = b - a
    p.collision_mask = 3
    var out := state.cast_motion(p)
    return out.size() == 2 and out[0] == 1.0 and out[1] == 1.0

func initial_overlap(state: PhysicsDirectSpaceState3D, shape: Shape3D, a: Vector3) -> bool:
    var p := PhysicsShapeQueryParameters3D.new()
    p.shape = shape
    p.transform = Transform3D(Basis.IDENTITY, a)
    p.collision_mask = 3
    return not state.intersect_shape(p, 1).is_empty()

func ray_clear(state: PhysicsDirectSpaceState3D, a: Vector3) -> bool:
    var p := PhysicsRayQueryParameters3D.create(a, FOCUS, 3)
    return state.intersect_ray(p).is_empty()

func run() -> void:
    var space := Node3D.new()
    root.add_child(space)
    var proxy := SphereShape3D.new()
    proxy.radius = 0.2
    add_prop(space, Vector3(0,0,3), 0.35, 1)
    add_prop(space, Vector3(0,0,-1), 0.2, 2)
    var l := add_arm(space, -1, proxy)
    var r := add_arm(space, 1, proxy)
    for i in range(8):
        await physics_frame
    var state := space.get_world_3d().direct_space_state
    var hit_l: float = l.get_hit_length()
    var hit_r: float = r.get_hit_length()
    var inside := Vector3(0, 0, 3)
    var result := {
      "engine": Engine.get_version_info().string,
      "physics": "GodotPhysics3D",
      "left_arm_unshortened": is_equal_approx(hit_l, 3.0),
      "right_arm_unshortened": is_equal_approx(hit_r, 3.0),
      "initial_overlap_detected": initial_overlap(state, proxy, inside),
      "cast_leaving_existing_overlap_reports_clear": cast_clear(state, proxy, inside, RIGHT),
      "direct_lateral_cast_clear": cast_clear(state, proxy, LEFT, RIGHT),
      "detour_casts_clear": [cast_clear(state, proxy, LEFT, VIA), cast_clear(state, proxy, VIA, RIGHT)],
      "left_mid_right_focus_rays_clear": [ray_clear(state, LEFT), ray_clear(state, VIA), ray_clear(state, RIGHT)]
    }
    print("OBSERVED " + JSON.stringify(result))
    if not result.left_arm_unshortened or not result.right_arm_unshortened or not result.initial_overlap_detected or not result.cast_leaving_existing_overlap_reports_clear or result.direct_lateral_cast_clear or result.detour_casts_clear != [true,true] or result.left_mid_right_focus_rays_clear != [true,false,true]:
        quit(1)
    else:
        quit(0)
