extends SceneTree

const SEED := 19731
const OTHER_SEED := 73491

func make_rng(value: int) -> RandomNumberGenerator:
    var rng := RandomNumberGenerator.new()
    rng.seed = value
    return rng

func row(rng: RandomNumberGenerator, case_name: String, tick: int, event: String,
        caller: String, stream: String) -> int:
    var before := rng.state
    var value := rng.randi()
    print(JSON.stringify({"case": case_name, "tick": tick, "event": event,
        "caller": caller, "stream": stream, "before": str(before),
        "after": str(rng.state), "raw": value}))
    return value

func run_case(case_name: String, extra_preview: bool, split: bool) -> Array[int]:
    var loot := make_rng(SEED)
    var preview := make_rng(OTHER_SEED) if split else loot
    var first := row(loot, case_name, 10, "open_a", "reward", "reward")
    if extra_preview:
        row(preview, case_name, 11, "sparkle", "preview", "visual" if split else "reward")
    var second := row(loot, case_name, 12, "open_b", "reward", "reward")
    var third := row(loot, case_name, 14, "open_c", "reward", "reward")
    return [first, second, third]

func restored(seed_value: int, raw_state: String) -> RandomNumberGenerator:
    var rng := make_rng(seed_value)
    rng.state = raw_state.to_int()
    return rng

func _initialize() -> void:
    var baseline := run_case("baseline", false, false)
    var shared := run_case("shared", true, false)
    var split := run_case("isolated", true, true)
    var reward := make_rng(SEED)
    var route := make_rng(OTHER_SEED)
    reward.randi()
    route.randi()
    var snapshot := JSON.stringify({"reward": str(reward.state), "route": str(route.state)})
    var decoded: Dictionary = JSON.parse_string(snapshot)
    var expected := [reward.randi(), route.randi()]
    var seed_only := [make_rng(SEED).randi(), make_rng(OTHER_SEED).randi()]
    var partial := [restored(SEED, decoded["reward"]).randi(), make_rng(OTHER_SEED).randi()]
    var full := [restored(SEED, decoded["reward"]).randi(), restored(OTHER_SEED, decoded["route"]).randi()]
    print(JSON.stringify({"case": "checkpoint", "expected": expected,
        "seed_only": seed_only, "partial": partial, "full": full,
        "baseline_bucket_b": baseline[1] % 2, "shared_bucket_b": shared[1] % 2}))
    var ok: bool = baseline == split and shared[0] == baseline[0] and shared[1] == baseline[2] \
        and shared[1] != baseline[1] and shared[1] % 2 == baseline[1] % 2 \
        and partial[0] == expected[0] and partial[1] != expected[1] \
        and seed_only[0] != expected[0] and full == expected
    quit(0 if ok else 1)
