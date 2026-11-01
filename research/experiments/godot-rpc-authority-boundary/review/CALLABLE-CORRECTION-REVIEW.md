# Callable/Node return-contract correction review

2026-11-01 00:22 UTC. Accepted endpoint.gd SHA256 `5694668f6e561e371152dbe97fc7dea5e80de41d8377546e7cc31ceebd506eb5` for a separately authorized fresh attempt. Exact delta replaces four Callable method.rpc_id expressions with Node self.rpc_id(peer, method_name, arguments); the other eight frozen sources are byte-identical. Protocol, annotations, arguments, ports, timeout and finite oracle are unchanged.

Independently read first failed UUID cee0c49d-8f19-4f76-aeee-76d302a255ca receipt/raw: version exit0, server four parse diagnostics for assigning a void return, then owned-group termination/reaped return -9. No READY or client launch is recorded. This is a fixture API mistake missed by initial source review, not evidence about network/bind capability, a successful RPC exchange or an engine defect.

Direct official Godot4.6 Callable.rpc_id documentation declares void; Node.rpc_id declares Error and an explicit method name. The new call sites use that documented distinction without dropping the return-code checks. Sources: https://docs.godotengine.org/en/4.6/classes/class_callable.html#class-callable-method-rpc-id and https://docs.godotengine.org/en/4.6/classes/class_node.html#class-node-method-rpc-id, accessed2026-11-01.

Verified all nine historical source hashes against the failed receipt and exact preserved receipt/raw bytes against the original invocation. Independently reran seven pure methods normal and -O, both passing; those tests do not compile GDScript and do not prove native correction success. No engine/version/socket invocation by this reviewer. The failed attempt remains failed; fresh runtime authorization must come separately from the coordinator.
