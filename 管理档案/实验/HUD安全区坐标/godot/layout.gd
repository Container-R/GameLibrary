extends SceneTree

# Mock physical pixels and an explicit 2:1 conversion, NOT a platform safe area.
const PHYSICAL_WINDOW = Rect2(0, 0, 2400, 1600)
const PHYSICAL_SAFE = Rect2(120, 80, 2160, 1440)
const PIXELS_PER_UI_UNIT = 2.0
var viewport: SubViewport
var nodes: Dictionary = {}

func _initialize() -> void:
    call_deferred("build")

func full_child(parent: Control, node_name: String, inset: Vector2) -> Control:
    var c = Control.new()
    c.name = node_name
    parent.add_child(c)
    c.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    c.offset_left = inset.x
    c.offset_top = inset.y
    c.offset_right = -inset.x
    c.offset_bottom = -inset.y
    nodes[node_name] = c
    return c

func build() -> void:
    viewport = SubViewport.new()
    viewport.size = Vector2i(1200, 800)
    root.add_child(viewport)
    var full = Control.new()
    full.name = "full_parent"
    viewport.add_child(full)
    full.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
    nodes[full.name] = full
    var inset = PHYSICAL_SAFE.position / PIXELS_PER_UI_UNIT
    full_child(full, "full_parent_correct_child", inset)
    var safe_parent = full_child(full, "already_inset_parent", inset)
    full_child(safe_parent, "inset_parent_correct_child", Vector2.ZERO)
    full_child(safe_parent, "inset_parent_duplicate_inset_child", inset)
    # Wait for actual engine deferred Control layout notifications to settle.
    await process_frame
    await process_frame
    verify()

func vec(v: Vector2) -> Array:
    return [v.x, v.y]

func rect(r: Rect2) -> Array:
    return [r.position.x, r.position.y, r.size.x, r.size.y]

func verify() -> void:
    var expected = {
        "full_parent": [Rect2(0,0,1200,800), Vector2(0,0)],
        "full_parent_correct_child": [Rect2(60,40,1080,720), Vector2(60,40)],
        "already_inset_parent": [Rect2(60,40,1080,720), Vector2(60,40)],
        "inset_parent_correct_child": [Rect2(60,40,1080,720), Vector2(0,0)],
        "inset_parent_duplicate_inset_child": [Rect2(120,80,960,640), Vector2(60,40)],
    }
    var observed = {}
    for key in expected:
        var c: Control = nodes[key]
        var global_expected: Rect2 = expected[key][0]
        if c.get_global_rect() != global_expected or c.position != expected[key][1] or c.size != global_expected.size:
            push_error("Layout mismatch: " + key + " actual=" + str(c.get_global_rect()))
            quit(1)
            return
        observed[key] = {"local_position":vec(c.position), "size":vec(c.size),
            "global_rect":rect(c.get_global_rect()),
            "anchors":[c.anchor_left,c.anchor_top,c.anchor_right,c.anchor_bottom],
            "offsets":[c.offset_left,c.offset_top,c.offset_right,c.offset_bottom]}
    var result = {"engine":Engine.get_version_info().string,
        "scope":"actual headless Godot Control layout; mocked physical rectangle; no mobile platform safe-area query",
        "mock_physical_window":rect(PHYSICAL_WINDOW), "mock_physical_safe":rect(PHYSICAL_SAFE),
        "physical_pixels_per_ui_unit":PIXELS_PER_UI_UNIT,
        "subviewport_size":[viewport.size.x,viewport.size.y], "process_frames_waited":2,
        "nodes":observed,"exact_assertions_passed":true}
    print("OBSERVED " + JSON.stringify(result))
    quit(0)
