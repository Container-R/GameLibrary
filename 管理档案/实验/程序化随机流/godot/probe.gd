extends SceneTree
const BASE_SEED = 424242
const DECOR_SEED = 701293

func make_rng(value: int) -> RandomNumberGenerator:
    var r = RandomNumberGenerator.new()
    r.seed = value
    return r

func rooms(r: RandomNumberGenerator, count: int) -> Array:
    var out = []
    for k in range(count):
        out.append(r.randi_range(0, 999999))
    return out

func shared(extra_decoration: bool) -> Dictionary:
    var r = make_rng(BASE_SEED)
    var prefix = rooms(r, 2)
    var decoration = []
    if extra_decoration:
        decoration.append(r.randi_range(0, 999999))
    return {"prefix":prefix,"decoration":decoration,"remaining_rooms":rooms(r,6)}

func separate(extra_decoration: bool) -> Dictionary:
    var layout = make_rng(BASE_SEED)
    var decor = make_rng(DECOR_SEED)
    var prefix = rooms(layout,2)
    var decoration = []
    if extra_decoration:
        decoration.append(decor.randi_range(0,999999))
    return {"prefix":prefix,"decoration":decoration,"remaining_rooms":rooms(layout,6)}

func _initialize() -> void:
    var normal = shared(false)
    var perturbed = shared(true)
    var isolated = separate(false)
    var isolated_extra = separate(true)
    var r = make_rng(BASE_SEED)
    var consumed = rooms(r,3)
    var saved_state = r.state
    var first = rooms(r,5)
    r.state = saved_state
    var replay = rooms(r,5)
    var checks = {
        "pinned_build_sequence_exact":normal.prefix+normal.remaining_rooms==[751541,756337,149008,865485,462888,51428,904232,692613],
        "shared_prefix_equal":normal.prefix==perturbed.prefix,
        "shared_suffix_changed":normal.remaining_rooms!=perturbed.remaining_rooms,
        "decoration_took_next_layout_value":perturbed.decoration[0]==normal.remaining_rooms[0],
        "shared_suffix_shifted_by_one":perturbed.remaining_rooms.slice(0,5)==normal.remaining_rooms.slice(1,6),
        "separate_layout_unchanged":isolated.remaining_rooms==isolated_extra.remaining_rooms,
        "separate_layout_matches_baseline":isolated.remaining_rooms==normal.remaining_rooms,
        "same_build_state_replay_exact":first==replay,
        "fresh_seed_repeats_exactly":shared(false)==normal,
    }
    for key in checks:
        if not checks[key]:
            push_error("Failed: "+key)
            quit(1)
            return
    print("OBSERVED "+JSON.stringify({
        "engine":Engine.get_version_info().string,
        "engine_hash":Engine.get_version_info().hash,
        "scope":"Actual built-in Godot RNG, no cross-build guarantee or statistical-independence claim",
        "base_seed":BASE_SEED,"decoration_seed":DECOR_SEED,
        "operation":"randi_range(0,999999), same calls throughout",
        "shared_without_extra":normal,"shared_with_extra":perturbed,
        "separate_without_extra":isolated,"separate_with_extra":isolated_extra,
        "restore":{"prefix":consumed,"state_decimal_string":str(saved_state),"first":first,"replay":replay},
        "checks":checks}))
    quit(0)
