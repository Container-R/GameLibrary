# Candidate protocol: RPC ingress, queued sender identity and command acceptance

2026-11-01. **Draft pending acceptance. No fixture code, engine/version execution, socket binding or packet transmission.** Source gate is `research-drafts/rpc-authority-triage/triage.md`; independent source review `research-drafts/deep-qa/rpc-authority/SOURCE-REVIEW.md`, SHA256 `f8580697bf1a6d0a476d9f1df5d95b80a69e823c8643bc71c78ad5dc12f162a5`. Scope is one finite two-process loopback RPC exchange, not movement prediction.

## 1. Frozen prospective process/network scope

Exactly one version-query process, one server process and one client process per attempt. No service discovery, DNS, external destination, UPNP, router/firewall change, download or installation. No process restarts, alternate ports, scanning or interface widening if the specified bind fails.

- Installed executable `/usr/local/bin/godot`; expected prior/current file-only SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`; expected version self-report `4.6.3.stable.official.7d41c59c4`. Verify immediately before and after, and retain full Engine dictionary with typed schema. Public source comparison does not authenticate this binary.
- Server requests bind IP `127.0.0.1`, UDP port **32187**, max_clients1. Client requests bind IP `127.0.0.1`, nonzero local UDP port **32188**, connects only to `127.0.0.1:32187`. Client local_port must not default to0: inspected source uses the bound-host branch only for nonzero local_port.
- Record create return codes and actual `host.get_local_port()` for each peer; require requested nonzero ports. Record actual connection peer IDs. This is API/configuration and port-readback evidence, **not an independent OS socket-interface audit**.
- The two chosen ports are distinct and unprivileged, but availability remains untested until the exact binds. No pre-scan. Local networking permission/ENet capability remains unestablished. Any tool policy denial, creation error, wrong port, schema/identity/oracle/diagnostic or timeout failure ends the attempt with preserved evidence. No privilege escalation or implicit retry.

## 2. Original scene and endpoint

Both processes construct the same original Node tree `/root/Fixture/Endpoint`, using the identical endpoint script and fully explicit RPC annotations/signatures. Role is a process argument; node name/path and RPC declarations do not vary by role. Endpoint multiplayer authority remains the default server ID1 and is read back on both sides. No MultiplayerSpawner, scene replication, external assets, object decoding or physics nodes.

Endpoint methods, all call_remote/reliable/channel0:
- `welcome`: authority; server→client assignment handshake.
- `submit`: any_peer; client→server request ingress.
- `outcome`: authority; server→client processed result.
- `finish`: any_peer; client→server confirmation of receiving all three outcomes.

RPC arguments are finite scalar/dictionary data only, no objects/callables. Exact field names/type checks will be frozen with code before review. Connection peer ID is not a human/account identity. This fixture does not authenticate a player.

## 3. Explicit server-owned fictional data and requests

Server records the sole connected client's actual peer ID C from its peer-connected event; require C>1 and exactly one connected peer. It creates ownership map `{A:C, B:1}`. Both integer accumulators start `{A:0,B:0}`. Actor names A/B are fixed synthetic identifiers, not user records. Server sends welcome only after this assignment; client verifies welcome sender1 and its own actual unique peer ID equals C.

Three requests, one outstanding at a time:

| Request index | Actor | Integer axis | Guarded decision | Naive state after | Guarded state after |
|---:|---|---:|---|---|---|
| 1 | A | 1 | accepted | A1/B0 | A1/B0 |
| 2 | B | 1 | rejected: ownership | A1/B1 | A1/B0 |
| 3 | A | 10000 | rejected: input_bound | A10001/B1 | A1/B0 |

Client sends request1 only after actual connected-to-server and valid welcome. It sends request2 only after actually receiving/validating outcome1; request3 only after outcome2. No timeout resends, retries, randomization, additional valid/invalid inputs, intentional loss, authority-mode rejection probe or malformed network payload. The axis range for the fictional rule is exactly integer `{-1,0,1}`. Bool/float substitution is not an integer in the application validator; no new native type-variant cases are added.

The request index is a finite handshake association, **not a tested ack prefix, replay/dedup mechanism or simulation tick**. Naive accumulation is deliberately unsafe teaching behavior inside an isolated original fixture, not real gameplay or a recommended server rule.

## 4. Separate ingress from deferred validation

At each actual `submit` RPC entry:
1. Read `get_remote_sender_id()` immediately into a server-owned record; require it matches C, server is role/server peer1, endpoint authority1 and node path is exact. Record actual sender, request values/index and receive ordinal.
2. Copy the finite scalar request fields and captured sender into queued data. Do not read identity from a client-claimed sender/owner field. No await inside RPC.
3. Schedule exactly one deferred processing callback, then log an RPC-end marker immediately before returning. Handler does **not** mutate either accumulator or decide application acceptance.

In the deferred callback:
1. Log the captured sender and a fresh `get_remote_sender_id()` call. Require captured C and fresh contextual getter0, with callback after that request's RPC-end marker. A deferred callback is not assumed to imply a whole frame delay.
2. Check the literal pending index/actor/axis and ownership mapping. First apply naive arithmetic solely from actor/axis. Independently apply guarded logic using captured sender against server-owned ownership, then integer input bounds. No guard uses the fresh getter0 as an actor identity.
3. Require the exact table's decision and both poststates. Record before/after states, rejection reason, captured sender, fresh getter and node authority. Any unexpected state fails before proceeding to the next request.
4. Send the corresponding outcome RPC to C, record its send return code separately. A successful send call alone does not prove client receipt. Client logs the actual outcome handler, its sender1, index/reason/states and its own ID; parent compares these against server observations.

The runtime-specific question is whether actual any_peer dispatch admits all three input RPCs and exposes the sender only in its active context. Actor ownership/range acceptance is original application logic. If deferred getter is not0 or the finite ordering fails, preserve the result and stop; do not add arbitrary extra frames or overwrite the observation.

## 5. Readiness and terminal handshake without timing luck

Parent orchestrator launches server first. Server emits a structured READY event only after successful peer creation, assignment to MultiplayerAPI, actual local-port readback and exact endpoint/authority readback. Parent launches client only after validating READY. Client must successfully create its explicitly bound host and emit CONNECTED; both peers must observe the expected counterpart before request processing. Readiness event order and RPC cross-process order are checked by identities/indexes and causal messages, not by comparing wall-clock timestamps as if perfectly synchronized.

After actual receipt and validation of outcome3, client records `CLIENT_RECEIVED_ALL` and sends exactly one `finish` RPC to server1. Server accepts finish only from C and only after its three deferred processing outcomes match the table. It records `SERVER_FINISH_CONFIRMED` and emits its single final RESULT_JSON. Client emits its single final RESULT_JSON after recording the successful finish send request; server confirmation is independently required by parent, so that client send return is not treated as delivery.

Neither process quits merely after queuing its final result. Both continue polling their MultiplayerAPI and wait for a **parent-owned STOP file** inside the fresh invocation directory. STOP must be absent before any child launch. Parent creates this file only after both final RESULT_JSON payloads and the server finish confirmation validate. Normal process callbacks check the file; there is no blocking stdin read on the engine networking/main thread and no arbitrary fixed sleep used as a readiness substitute. This local barrier carries no request, actor, sender or decision data and is not a substitute for RPC observations.

On STOP, each child closes its owned peer and requests clean exit. Observation windows are explicit: gameplay/handshake trace ends at each final payload; later connection shutdown notifications must not mutate the frozen trace or invoke missing-node snapshots. Both streams remain subject to strict diagnostic rejection through process exit; the window guard is not a stderr filter. If parent sees failure or timeout before STOP, it attempts bounded termination/wait of both owned process groups and preserves partial traces. It must not leave a server listening while reporting completion.

## 6. Execution and receipt contract

- Exact additive `isolation.py` helper SHA256 `bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970`; explicit base PATH=/usr/bin:/bin, LANG=C, LC_ALL=C. Separate fresh five-location environments for version/server/client, no inherited loader variables or secret dumps. No sandbox/complete provenance claim.
- Source manifest before/after includes this protocol and all runner, scene, endpoint, project, oracle, consumer, pure-test and helper sources. Failed snapshots stay bound to their own bytes. Reject unexpected binary/source changes.
- Fresh UUID evidence directory. Remove stale PASS summary before optimized-mode rejection/local imports; runner `-O` stops before native/tool entry. Exact commands recorded after reviewed source freeze.
- Version query timeout20 seconds. Concurrent server/client attempt has a shared 20-second external deadline beginning at server launch; each child has a 15-second monotonic internal watchdog. These are termination bounds, not a successful-network timing guarantee. No arbitrary per-stage retries or sleeps.
- Parent uses bounded event-driven stdout/stderr collection and retains every raw byte, including launch/timeout/termination failures. Record UTC attempted/returned times, process exit/status, pid, create/RPC return codes and cleanup attempts. Kill/wait operations are bounded and cannot promise containment of escaped descendants.
- Expected successful streams contain only documented version/banner plus specified structured event/result lines. No expected engine warning/error; reject unrelated stdout/stderr diagnostics, duplicate final payloads, missing outcomes, wrong types or unexpected protocol events. JSON rejects duplicate keys, NaN/Infinity/overflow and bool/int substitutions in identity/count fields.
- PASS only after both children return0, all three requests and finish confirmation are bound across logs, literal table/context/identity checks succeed and source/binary after hashes match. Record one version and two behavior processes, not three independent gameplay scenarios. The fixture contains three command samples in one sequence: exactly three submit RPC invocations, separately one welcome assignment, three outcome RPCs and one finish control RPC (eight remote handler deliveries total if all stages succeed). No local RPC delivery is requested.
- A portable static consumer binds raw/parsed payloads, manifests/outputs, identities, argv/status and causal request/outcome association; no current executable dependency and no execution-authenticity guarantee. Synthetic negative/consumer/startup checks are not native networking attempts.

## 7. Sources and stopping boundary

Read official Godot4.6 High-level multiplayer RPC/connection sections; MultiplayerAPI RPCMode/get_remote_sender_id/poll; ENetMultiplayerPeer create_server/create_client/set_bind_ip; ENetConnection get_local_port; Object call_deferred. Comparison source commit `35e80b3a8822a9df9be390814b62f44c0a9c69e8`: scene_rpc_interface.cpp240–295, scene_multiplayer.cpp130–135, enet_multiplayer_peer.cpp60–98. Source gate preserves URLs and exact existing article/model hashes. No authority-mode misuse warning is intentionally triggered.

Stop after the first complete accepted finite exchange or any capability/schema/oracle/diagnostic/timeout failure. Independent repeat requires separate authorization. No authentication, account security, general anti-cheat, rate limiting, cryptographic transport, replays, disconnect/reconnect ownership, WAN latency/loss, prediction, server reconciliation, collision/physics or cross-platform determinism validation. Local fixed-port failure is not a reason to search or expose another interface.
