# First native author attempt: parse failure, no ingress evidence

2026-11-01 00:21 UTC. Main invoked corrected runner once after code acceptance. UUID cee0c49d-8f19-4f76-aeee-76d302a255ca. Version query returned0; server script emitted four parse diagnostics at endpoint.gd97/131/181/201 because Callable.rpc_id has no return value. Parent stopped on stderr, sent killpg and confirmed server exit-9. Main tool session itself ended1. Client was never launched; no READY, command, outcome or accepted networking sequence exists. Source and binary before/after hashes agree.

This is an API-form error in the original fixture, missed in pre-native source review. It is not evidence that ENet, local binding, authority policy or deferred sender semantics failed. No parse-only rerun or port retry was performed.

Main directly opened Godot4.6 Callable rpc_id257–258 (void) and Node rpc_id1546–1549 (Error). A narrow correction can preserve the protocol's local send-return check by using Node.rpc_id(peer_id, method_name, ...), instead of assigning the Callable convenience form. Exactly four callsites may change; fixed protocol, ports, timing, payloads and expected observations stay unchanged. Failed source/raw artifacts must remain separately bound; retry requires independent correction review and fresh authorization.

Sources: https://docs.godotengine.org/en/4.6/classes/class_callable.html#class-callable-method-rpc-id and https://docs.godotengine.org/en/4.6/classes/class_node.html#class-node-method-rpc-id . No copied third-party implementation.
