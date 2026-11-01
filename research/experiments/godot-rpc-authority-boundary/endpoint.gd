extends Node
# Original finite localhost fixture. Peer IDs are not authenticated accounts.
var role: String
var stop_file: String
var peer: ENetMultiplayerPeer
var trace: Array = []
var sequence := 0
var started := 0
var observation_closed := false
var stopping := false
var counterpart_seen := false
var connected := false
var welcomed := false
var client_id := 0
var owners: Dictionary = {}
var naive := {"A": 0, "B": 0}
var guarded := {"A": 0, "B": 0}
var pending: Dictionary = {}
var received := 0
var processed := 0
var sent := 0
var outcomes := 0
const ACTORS = ["A", "B", "A"]
const AXES = [1, 1, 10000]
const REASONS = ["accepted", "ownership", "input_bound"]
const NAIVE = [{"A": 1, "B": 0}, {"A": 1, "B": 1}, {"A": 10001, "B": 1}]
const GUARDED = {"A": 1, "B": 0}

func record(kind: String, fields: Dictionary = {}) -> void:
    if observation_closed:
        return
    sequence += 1
    var row := {"sequence": sequence, "role": role, "kind": kind}
    row.merge(fields)
    trace.append(row)
    print("EVENT_JSON=" + JSON.stringify(row))

func fail(reason: String) -> void:
    if stopping:
        return
    stopping = true
    print("FAILURE_JSON=" + JSON.stringify({"role": role, "reason": reason, "trace": trace}))
    if peer != null:
        peer.close()
    get_tree().quit(2)

func require_value(ok: bool, reason: String) -> bool:
    if not ok:
        fail(reason)
        return false
    return true

func begin(which: String, stop_path: String) -> void:
    role = which
    stop_file = stop_path
    started = Time.get_ticks_msec()
    if not require_value(not FileAccess.file_exists(stop_file), "preexisting STOP"):
        return
    multiplayer.allow_object_decoding = false
    multiplayer.peer_connected.connect(on_peer_connected)
    multiplayer.connected_to_server.connect(on_connected)
    multiplayer.connection_failed.connect(func(): fail("connection failed"))
    multiplayer.server_disconnected.connect(on_disconnected)
    multiplayer.peer_disconnected.connect(func(_id: int): on_disconnected())
    peer = ENetMultiplayerPeer.new()
    peer.set_bind_ip("127.0.0.1")
    var error: int
    if role == "server":
        error = peer.create_server(32187, 1, 1)
    else:
        error = peer.create_client("127.0.0.1", 32187, 1, 0, 0, 32188)
    record("CREATE", {"return_code": error, "requested_bind_ip": "127.0.0.1", "requested_local_port": 32187 if role == "server" else 32188,
        "destination": "127.0.0.1:32187" if role == "client" else "none"})
    if not require_value(error == OK, "create failed"):
        return
    multiplayer.multiplayer_peer = peer
    var local_port := peer.host.get_local_port()
    if not require_value(local_port == (32187 if role == "server" else 32188), "local port"):
        return
    if not require_value(not multiplayer.allow_object_decoding and not multiplayer.auth_callback.is_valid(), "configuration"):
        return
    if not require_value(get_path() == NodePath("/root/Fixture/Endpoint") and get_multiplayer_authority() == 1, "endpoint"):
        return
    record("READY" if role == "server" else "CLIENT_BOUND", {"local_port": local_port, "unique_id": multiplayer.get_unique_id(),
        "authority": get_multiplayer_authority(), "path": str(get_path()), "allow_object_decoding": multiplayer.allow_object_decoding,
        "auth_callback_valid": multiplayer.auth_callback.is_valid(), "is_server": multiplayer.is_server()})

func on_peer_connected(id: int) -> void:
    if not require_value(not observation_closed, "late connection"):
        return
    if role == "server":
        if not require_value(id > 1 and client_id == 0, "single client"):
            return
        client_id = id
        owners = {"A": id, "B": 1}
        record("PEER_CONNECTED", {"peer_id": id, "owners": owners.duplicate(true), "actual_peers": Array(multiplayer.get_peers())})
        var error = self.rpc_id(client_id, "welcome", client_id, "A", "B")
        record("CONTROL_SENT", {"method": "welcome", "target": client_id, "return_code": error})
        require_value(error == OK, "welcome send")
    else:
        if not require_value(id == 1, "client counterpart"):
            return
        counterpart_seen = true
        record("PEER_CONNECTED", {"peer_id": id})
        try_send()

func on_connected() -> void:
    if not require_value(role == "client" and not connected, "connected event"):
        return
    connected = true
    record("CONNECTED", {"unique_id": multiplayer.get_unique_id(), "actual_peers": Array(multiplayer.get_peers())})
    try_send()

@rpc("authority", "call_remote", "reliable", 0)
func welcome(assigned, own_actor, other_actor) -> void:
    var sender := multiplayer.get_remote_sender_id()
    if not require_value(role == "client" and not welcomed and sender == 1 and typeof(assigned) == TYPE_INT and assigned > 1,
        "welcome sender/type"):
        return
    if not require_value(assigned == multiplayer.get_unique_id() and typeof(own_actor) == TYPE_STRING and own_actor == "A" and typeof(other_actor) == TYPE_STRING and other_actor == "B", "welcome payload"):
        return
    client_id = assigned
    welcomed = true
    record("WELCOME", {"sender": sender, "assigned": assigned, "authority": get_multiplayer_authority()})
    try_send()

func try_send() -> void:
    if not counterpart_seen or not connected or not welcomed or sent != outcomes or sent >= 3:
        return
    sent += 1
    var error = self.rpc_id(1, "submit", sent, ACTORS[sent - 1], AXES[sent - 1])
    record("SUBMIT_SENT", {"index": sent, "actor": ACTORS[sent - 1], "axis": AXES[sent - 1], "target": 1, "return_code": error})
    require_value(error == OK, "submit send")

@rpc("any_peer", "call_remote", "reliable", 0)
func submit(index, actor, axis) -> void:
    var sender := multiplayer.get_remote_sender_id()
    if not require_value(role == "server" and multiplayer.is_server() and sender == client_id and sender > 1 and get_multiplayer_authority() == 1, "ingress context"):
        return
    if not require_value(typeof(index) == TYPE_INT and typeof(actor) == TYPE_STRING and typeof(axis) == TYPE_INT, "ingress scalar types"):
        return
    if not require_value(index == received + 1 and index >= 1 and index <= 3 and pending.is_empty() and processed == received, "ingress order"):
        return
    if not require_value(actor == ACTORS[index - 1] and axis == AXES[index - 1], "finite request envelope"):
        return
    received += 1
    record("RPC_ENTER", {"index": index, "sender": sender, "authority": get_multiplayer_authority(), "actor": actor, "axis": axis,
        "naive": naive.duplicate(true), "guarded": guarded.duplicate(true)})
    pending = {"index": index, "actor": actor, "axis": axis, "captured_sender": sender}
    record("ENQUEUED", pending.duplicate(true))
    call_deferred("process_pending")
    record("RPC_END", {"index": index, "sender": multiplayer.get_remote_sender_id()})

func process_pending() -> void:
    if not require_value(role == "server" and not pending.is_empty(), "queued state"):
        return
    var command := pending.duplicate(true)
    var index: int = command.index
    var fresh_sender := multiplayer.get_remote_sender_id()
    if not require_value(command.captured_sender == client_id and fresh_sender == 0 and index == processed + 1, "deferred sender/order"):
        return
    record("DEFERRED", {"index": index, "captured_sender": command.captured_sender, "fresh_sender": fresh_sender,
        "owners": owners.duplicate(true), "authority": get_multiplayer_authority()})
    var before_naive := naive.duplicate(true)
    var before_guarded := guarded.duplicate(true)
    naive[command.actor] += command.axis
    var reason: String
    if owners[command.actor] != command.captured_sender:
        reason = "ownership"
    elif typeof(command.axis) != TYPE_INT or command.axis not in [-1, 0, 1]:
        reason = "input_bound"
    else:
        reason = "accepted"
        guarded[command.actor] += command.axis
    if not require_value(reason == REASONS[index - 1] and naive == NAIVE[index - 1] and guarded == GUARDED, "literal policy outcome"):
        return
    processed += 1
    pending.clear()
    record("DECISION", {"index": index, "reason": reason, "before_naive": before_naive, "before_guarded": before_guarded,
        "naive": naive.duplicate(true), "guarded": guarded.duplicate(true), "captured_sender": command.captured_sender})
    var error = self.rpc_id(client_id, "outcome", index, reason, naive.duplicate(true), guarded.duplicate(true))
    record("CONTROL_SENT", {"method": "outcome", "index": index, "target": client_id, "return_code": error})
    require_value(error == OK, "outcome send")

@rpc("authority", "call_remote", "reliable", 0)
func outcome(index, reason, naive_state, guarded_state) -> void:
    var sender := multiplayer.get_remote_sender_id()
    if not require_value(role == "client" and sender == 1 and typeof(index) == TYPE_INT and typeof(reason) == TYPE_STRING and typeof(naive_state) == TYPE_DICTIONARY and typeof(guarded_state) == TYPE_DICTIONARY, "outcome envelope"):
        return
    if not require_value(index == outcomes + 1 and index == sent and index <= 3, "outcome order"):
        return
    for data in [naive_state, guarded_state]:
        if not require_value(data.size() == 2 and data.has("A") and data.has("B") and typeof(data.A) == TYPE_INT and typeof(data.B) == TYPE_INT, "state scalar types"):
            return
    if not require_value(reason == REASONS[index - 1] and naive_state == NAIVE[index - 1] and guarded_state == GUARDED, "client literal outcome"):
        return
    outcomes += 1
    record("OUTCOME", {"index": index, "sender": sender, "reason": reason, "naive": naive_state, "guarded": guarded_state})
    if outcomes == 3:
        record("CLIENT_RECEIVED_ALL", {"outcomes": outcomes})
        var error = self.rpc_id(1, "finish", 3)
        record("CONTROL_SENT", {"method": "finish", "target": 1, "return_code": error})
        if not require_value(error == OK, "finish send"):
            return
        publish()
    else:
        try_send()

@rpc("any_peer", "call_remote", "reliable", 0)
func finish(last_index) -> void:
    var sender := multiplayer.get_remote_sender_id()
    if not require_value(role == "server" and sender == client_id and typeof(last_index) == TYPE_INT and last_index == 3 and received == 3 and processed == 3 and pending.is_empty(), "finish confirmation"):
        return
    record("SERVER_FINISH_CONFIRMED", {"sender": sender, "last_index": last_index, "naive": naive.duplicate(true), "guarded": guarded.duplicate(true)})
    publish()

func publish() -> void:
    if not require_value(not observation_closed, "duplicate final"):
        return
    observation_closed = true
    print("RESULT_JSON=" + JSON.stringify({"role": role, "version": Engine.get_version_info(), "unique_id": multiplayer.get_unique_id(),
        "client_id": client_id, "authority": get_multiplayer_authority(), "path": str(get_path()), "trace": trace}))

func _process(_delta: float) -> void:
    if started == 0 or stopping:
        return
    if FileAccess.file_exists(stop_file):
        if not require_value(observation_closed, "STOP before final"):
            return
        stopping = true
        peer.close()
        get_tree().quit(0)
    elif Time.get_ticks_msec() - started > 15000:
        fail("finite watchdog")

func on_disconnected() -> void:
    # Only the coordinator-owned terminal barrier authorizes teardown.
    if observation_closed and FileAccess.file_exists(stop_file):
        return
    fail("unexpected disconnect before terminal barrier")
