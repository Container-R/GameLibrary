extends SceneTree
# Original ownership probe. Main-thread mutation only after threaded load completes.
var active: GradientTexture1D
var active_gradient: Gradient
var active_id: int
var mode: int
var case_name: String
var frames: int = 0
var statuses: Array = []
var requested: bool = false
var finished: bool = false
var initial: Dictionary

func rgba(c: Color) -> Array:
    return [c.r, c.g, c.b, c.a]

func fail(message: String) -> void:
    push_error(message)
    finished = true
    quit(1)

func _initialize() -> void:
    var args := OS.get_cmdline_user_args()
    if args.size() != 1 or args[0] not in ["ignore", "ignore-deep"]:
        fail("one known case required")
        return
    case_name = args[0]
    mode = ResourceLoader.CACHE_MODE_IGNORE if case_name == "ignore" else ResourceLoader.CACHE_MODE_IGNORE_DEEP
    active = ResourceLoader.load("res://candidate.tres", "GradientTexture1D", ResourceLoader.CACHE_MODE_REUSE) as GradientTexture1D
    if active == null or active.gradient == null:
        fail("active graph missing")
        return
    active_gradient = active.gradient
    active_id = active.get_instance_id()
    initial = {"root_id": active_id, "gradient_id": active_gradient.get_instance_id(),
        "color": rgba(active_gradient.get_color(0)), "point_count": active_gradient.get_point_count()}
    var request_result := ResourceLoader.load_threaded_request("res://candidate.tres", "GradientTexture1D", false, mode)
    print("REQUEST_JSON=" + JSON.stringify({"case": case_name, "mode": mode, "return": request_result, "initial": initial}))
    if request_result != OK:
        fail("threaded request failed")
        return
    requested = true

func _process(_delta: float) -> bool:
    if finished or not requested:
        return false
    frames += 1
    if frames > 600:
        fail("frame budget exceeded")
        return false
    var status := ResourceLoader.load_threaded_get_status("res://candidate.tres")
    statuses.append(status)
    if status == ResourceLoader.THREAD_LOAD_FAILED or status == ResourceLoader.THREAD_LOAD_INVALID_RESOURCE:
        fail("threaded status failure: " + str(status))
        return false
    if status != ResourceLoader.THREAD_LOAD_LOADED:
        return false
    var candidate := ResourceLoader.load_threaded_get("res://candidate.tres") as GradientTexture1D
    if candidate == null or candidate.gradient == null:
        fail("candidate graph missing")
        return false
    var before := {"active_color": rgba(active_gradient.get_color(0)),
        "candidate_color": rgba(candidate.gradient.get_color(0)),
        "active_root_id": active.get_instance_id(), "candidate_root_id": candidate.get_instance_id(),
        "active_gradient_id": active_gradient.get_instance_id(), "candidate_gradient_id": candidate.gradient.get_instance_id()}
    # Do not assign candidate to active. This is the only content mutation.
    candidate.gradient.set_color(0, Color(0, 0, 1, 1))
    var after := {"active_color": rgba(active.gradient.get_color(0)),
        "held_gradient_color": rgba(active_gradient.get_color(0)),
        "candidate_color": rgba(candidate.gradient.get_color(0)),
        "active_root_id": active.get_instance_id(), "active_gradient_id": active.gradient.get_instance_id(),
        "candidate_root_id": candidate.get_instance_id(), "candidate_gradient_id": candidate.gradient.get_instance_id()}
    print("RESULT_JSON=" + JSON.stringify({"case": case_name, "mode": mode,
        "version": Engine.get_version_info(), "initial": initial, "before": before, "after": after,
        "statuses": statuses, "frames": frames, "request_count": 1, "get_count": 1,
        "use_sub_threads": false, "initial_active_id": active_id}))
    finished = true
    quit(0)
    return false
