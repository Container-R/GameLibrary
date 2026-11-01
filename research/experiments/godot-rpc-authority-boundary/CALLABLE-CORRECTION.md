# First native attempt: Callable/Node return contract correction

Author attempt `cee0c49d-8f19-4f76-aeee-76d302a255ca` is FAIL. Version returned 0; server produced four GDScript parse errors assigning the void return of `method.rpc_id(...)`. Parent terminated the owned server (observed -9); no READY or client process occurred. No successful RPC exchange is established by this attempt. Exact sources, output and receipt are retained under `historical-callable-return-failure/`.

Read 2026-11-01: [Callable 4.6 rpc_id](https://docs.godotengine.org/en/4.6/classes/class_callable.html#class-callable-method-rpc-id) has no return value; [Node 4.6 rpc_id](https://docs.godotengine.org/en/4.6/classes/class_node.html#class-node-method-rpc-id) returns Error and takes an explicit method name. The fixture incorrectly conflated these two API forms. This is an author implementation error, not an engine/network failure.

Only four send expressions now use `self.rpc_id(peer_id, "method", ...)`. Existing annotations, payloads, send return-code checks, ports, timing, protocol and semantic oracle are unchanged. Seven pure methods normal/-O pass; these do not compile GDScript or establish the correction works in the actual engine. Independent correction review and a separate authorization are required before any fresh native attempt.
