extends SceneTree
const Endpoint = preload("res://endpoint.gd")
func _initialize() -> void:
    var args := OS.get_cmdline_user_args()
    if args.size() != 2 or args[0] not in ["server", "client"]:
        push_error("invalid finite fixture arguments")
        quit(2)
        return
    var fixture := Node.new()
    fixture.name = "Fixture"
    root.add_child(fixture, true)
    var endpoint := Endpoint.new()
    endpoint.name = "Endpoint"
    fixture.add_child(endpoint, true)
    endpoint.call_deferred("begin", args[0], args[1])
