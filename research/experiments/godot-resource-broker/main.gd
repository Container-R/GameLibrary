extends SceneTree
# Original same-path request policy probe; no concurrent resource mutations.
const PATH := "res://gradient.tres"
var active: Gradient
var result1: Gradient
var result2: Gradient
var first_mode: int
var second_mode: int
var case_name: String
var frames: int = 0
var request_count: int = 0
var get_count: int = 0
var trace: Array = []
var initial: Dictionary
var finished := false
var ready_to_poll := false

func rgba(c: Color) -> Array:
    return [c.r, c.g, c.b, c.a]

func describe(resource: Gradient) -> Dictionary:
    if resource == null:
        return {"null": true}
    var colors: Array = []
    var offsets: Array = []
    for index in resource.get_point_count():
        colors.append(rgba(resource.get_color(index)))
        offsets.append(resource.get_offset(index))
    return {"id": resource.get_instance_id(), "type": resource.get_class(), "colors": colors, "offsets": offsets}

func record(value: Dictionary) -> void:
    trace.append(value)
    print("CALL_JSON=" + JSON.stringify(value))

func request(mode: int) -> int:
    request_count += 1
    var code := ResourceLoader.load_threaded_request(PATH, "Gradient", false, mode)
    record({"op": "request", "number": request_count, "mode": mode, "return": code})
    return code

func status(stage: String) -> int:
    var value := ResourceLoader.load_threaded_get_status(PATH)
    record({"op": "status", "stage": stage, "value": value})
    return value

func collect() -> Gradient:
    get_count += 1
    var resource := ResourceLoader.load_threaded_get(PATH) as Gradient
    record({"op": "get", "number": get_count, "resource": describe(resource)})
    return resource

func fail(message: String) -> void:
    push_error(message)
    finished = true
    quit(1)

func _initialize() -> void:
    var args := OS.get_cmdline_user_args()
    if args.size() != 1 or args[0] not in ["reuse-then-deep", "deep-then-reuse"]:
        fail("unknown case")
        return
    case_name = args[0]
    first_mode = ResourceLoader.CACHE_MODE_REUSE if case_name == "reuse-then-deep" else ResourceLoader.CACHE_MODE_IGNORE_DEEP
    second_mode = ResourceLoader.CACHE_MODE_IGNORE_DEEP if case_name == "reuse-then-deep" else ResourceLoader.CACHE_MODE_REUSE
    active = ResourceLoader.load(PATH, "Gradient", ResourceLoader.CACHE_MODE_REUSE) as Gradient
    if active == null:
        fail("active missing")
        return
    initial = describe(active)
    if request(first_mode) != OK:
        fail("first request rejected")
        return
    ready_to_poll = true

func _process(_delta: float) -> bool:
    if finished or not ready_to_poll:
        return false
    frames += 1
    if frames > 600:
        fail("frame budget exceeded")
        return false
    var first_status := status("first-poll")
    if first_status in [ResourceLoader.THREAD_LOAD_FAILED, ResourceLoader.THREAD_LOAD_INVALID_RESOURCE]:
        fail("first request load failed")
        return false
    if first_status != ResourceLoader.THREAD_LOAD_LOADED:
        return false
    # The first operation is complete but uncollected before the second request.
    if request(second_mode) != OK:
        fail("second request rejected")
        return false
    var second_status := status("after-second-request")
    if second_status != ResourceLoader.THREAD_LOAD_LOADED:
        fail("unexpected new pending load; preserve trace rather than block get")
        return false
    result1 = collect()
    var after_first := status("after-first-get")
    if result1 == null or after_first != ResourceLoader.THREAD_LOAD_LOADED:
        fail("first collection did not leave loaded request")
        return false
    result2 = collect()
    var after_second := status("after-second-get")
    if result2 == null:
        fail("second collection missing")
        return false
    print("RESULT_JSON=" + JSON.stringify({"case": case_name, "first_mode": first_mode, "second_mode": second_mode,
        "version": Engine.get_version_info(), "initial": initial, "active_after": describe(active),
        "result1": describe(result1), "result2": describe(result2), "trace": trace,
        "frames": frames, "request_count": request_count, "get_count": get_count,
        "use_sub_threads": false, "final_status": after_second}))
    finished = true
    quit(0)
    return false
