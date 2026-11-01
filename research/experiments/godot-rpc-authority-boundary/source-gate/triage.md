# RPC authority triage: transport permission is not command authorization

2026-11-01. Source/read-only gate only. **No new code, engine/version invocation, socket creation, port binding or packet transmission.** Recommend a conditional finite loopback observation, not a prediction or physics fixture.

## Existing evidence, exact applicability

Inspected `gamelibrary-work/solutions/programming/client-prediction-authority-boundary.md`, SHA256 `833d6d37ee69bc6f6665fb7516f54fd3f81deb71c1f36c296528bd158cdcc3ae`. Verbatim metadata:

> verification_method: 原始来源核对与既有原创离散协议模型16项测试；跨实体依赖补充为未执行手算与验收提案；未进行引擎、真实网络或跨平台物理验证

Existing `research/experiments/client-prediction/test_prediction.py` SHA `a96b23caa10d1a6bbe7b3b4b6c6340f2a10fff6b6db445f9a88eeb701e2b87f6`; archived `test-output.txt` SHA `ab19aeaae528d1ba518fa4917f8bc8b906509c61f325870e5e98c048f2296934`. Read the Server.receive/step and Client.issue/reconcile implementation: this is one-dimensional integer state, epoch/sequence window and bounded axis handling, no socket or sender ownership map. It intentionally finalizes invalid axes as no-op; it does not bind a network sender to an actor. The article explicitly excludes connection authentication/actor binding. Its separate seeded adversarial model review does not fill this native gap either.

Therefore a limited native RPC experiment would supplement **one command ingress boundary**. It would not demonstrate movement prediction, reconciliation/ack correctness, partial snapshots, network impairment tolerance or collision determinism. The current model-only wording is correct for the existing evidence.

## Concrete question and prospective finite outcome

An endpoint keeps default server multiplayer authority but uses `@rpc("any_peer", "call_remote", "reliable", 0)` to receive input. If a connected client supplies another actor ID or an out-of-range integer axis, does actual RPC delivery itself reject those game-invalid requests? Proposed counterexample: all three requests actually enter the handler, while a server-owned sender-to-actor map and explicit range check distinguish accepted game commands.

One server and one client process, matching endpoint NodePath and identical RPC declarations. Three requests in an acknowledged application handshake, one outstanding at a time:

| Request | Server-owned actor relation | Axis | Expected original application decision |
|---|---|---:|---|
| own actor | assigned to actual connected sender | +1 | accepted |
| other actor | assigned to server, not client | +1 | rejected: ownership |
| own actor | assigned to actual connected sender | 10000 | rejected: input bound |

Each server handler captures `get_remote_sender_id()` immediately, before any await/deferred handoff. It records actual sender, endpoint authority, request values and accepted/rejected outcome. A deliberately naive in-memory accumulator trusts all payloads; a guarded accumulator accepts only the first. With initial A=B=0, prospective naive result A=10001/B=1 versus guarded A=1/B=0 is a hand-enumerated **application policy illustration**, not physical movement or production authorization. Under the selected queued refinement below, both calculations occur in the deferred processing callback, after actual RPC ingress captures sender context; no additional native scenarios are needed.

The useful native facts would be remote handler entry and sender/authority context, paired with server-owned actor mapping. A client-authored `claimed_sender` field would not substitute for the captured peer ID. The two-process fixture has only one real client; the server-owned second actor is enough to make the foreign-actor request meaningful without inventing a second authenticated player.

A server-to-client authority-mode result RPC could acknowledge each outcome. Awaiting the actual outcome before sending the next request avoids timing-luck sleeps; it does not prove exactly-once or arbitrary-loss reliability. Separate ready/connected/assigned/processed/outcome/finished stages must be frozen before implementation. RPC return OK alone is not remote execution evidence.

## Official versioned sources actually read

Accessed 2026-11-01. Godot 4.6 documentation; pinned source comparison `35e80b3a8822a9df9be390814b62f44c0a9c69e8` is not authenticated source of the installed binary.

1. [High-level multiplayer](https://docs.godotengine.org/en/4.6/tutorials/networking/high_level_multiplayer.html), Initializing the network / Managing connections / Remote procedure calls: client/server peer setup, server peer ID1, matching NodePath and RPC configuration/signatures, any_peer versus authority and call_remote. No model-specific actor authorization is provided by choosing an annotation. Current page's RPC default text is not needed: proposed annotations would be fully explicit.
2. [MultiplayerAPI](https://docs.godotengine.org/en/4.6/classes/class_multiplayerapi.html), RPCMode and get_remote_sender_id: ANY_PEER accepts calls regardless of node authority; AUTHORITY restricts the sender to node authority. Sender ID is contextual to the executing RPC and can be lost outside it. That ID is a connection peer identifier, not proof of an authenticated human/account.
3. [Pinned RPC dispatch](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/multiplayer/scene_rpc_interface.cpp#L240-L295): can_call switches on RPC mode before decoding arguments and invoking the handler; ANY_PEER permits that dispatch, AUTHORITY compares p_from with node authority. This inspected branch does not perform the proposed game's actor-ownership/range rule. No universal claim is made about every layer of validation in the engine.
4. [ENetMultiplayerPeer 4.6](https://docs.godotengine.org/en/4.6/classes/class_enetmultiplayerpeer.html), create_server/create_client/set_bind_ip: ENet uses UDP; server defaults to wildcard unless changed; creation returns explicit errors; client accepts a local-port parameter. [Pinned create_server/client](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/enet/enet_multiplayer_peer.cpp#L60-L98) passes bind_ip to the bound host; client uses that bound-host branch only if local_port is nonzero. Thus merely setting bind_ip and leaving local_port0 is not evidence the client socket was explicitly loopback-bound.
5. [ENetConnection 4.6](https://docs.godotengine.org/en/4.6/classes/class_enetconnection.html), create_host_bound/get_local_port: host creation and bound port observation. Useful for recording actual selected port, not permission to scan arbitrary ports or proof that an OS bind will succeed here.

## Capability, permissions and safe stop

Prior accepted headless fixtures identify installed `/usr/local/bin/godot`, self-report `4.6.3.stable.official.7d41c59c4`, binary SHA `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`. This gate did not re-run or rehash it. Existing native capability does **not** establish ENet availability or permission to bind local sockets under this execution policy. Network restrictions are active; localhost behavior has not been tested or inferred from ordinary web access.

Conditional design: both peers explicitly set bind_ip127.0.0.1; choose two distinct unprivileged ports in the reviewed protocol, with availability untested until the exact binds, and pass nonzero local_port to the client so the inspected bound-host branch applies. No wildcard bind, UPNP, NAT traversal, external hostname, router/firewall change, account/credential or third-party destination. No preliminary port scan. If either specific bind fails or policy denies execution, retain that capability failure and stop; do not retry a range, widen interfaces, escalate privileges or substitute a single-process model and call it network evidence.

Parent must accept this gate and a frozen protocol before code, then review code before exactly one bounded server/client attempt and separately counted version query. Run with isolated writable locations, explicit minimal environment, timeout/cleanup for both owned child groups, actual readiness rather than arbitrary sleep, full per-process streams and source/binary identity. Keep failed attempts separate from accepted observations.

Stop at either the first capability/oracle failure or one completed three-request sequence. No fuzzing, security exploit against another service, actual player identity/authentication, malicious packet serialization, encryption, replay protection, rate limiting, reconnection, WAN loss/latency, prediction, physics or general anti-cheat claim. This is valuable only if genuine remote handler/sender observations are established; otherwise retain a source-only boundary note and defer runtime evidence.

## Main-requested refinement: capture sender before queue handoff

Additional source read 2026-11-01: pinned [SceneMultiplayer packet processing](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/multiplayer/scene_multiplayer.cpp#L130-L135) assigns remote_sender_id around synchronous packet handling and resets it to0 afterwards. This directly complements the MultiplayerAPI method documentation; it does not prove arbitrary threading contexts or authenticated identity.

Recommended refinement to the same three-request sequence: inside the actual RPC, capture its sender immediately into a server-owned queued record containing only the finite request index/actor/integer axis and captured peer ID. Defer processing with no await in the handler. At that separate processing point record both the saved sender and a fresh contextual getter. The prospective result is actual captured connected-peer ID versus fresh getter0; validation uses the former plus the server's ownership map.

This is materially more useful than merely proving a bad actor field can arrive: gameplay command processing often occurs after ingress. A validator that re-queries sender outside RPC may lose the identity needed even for the legitimate request. Keep that as an observed context comparison, not a third broad policy implementation. The naive payload-trusting accumulator and captured-sender guarded accumulator still use the same three requests and hand-enumerated final values above.

[Object 4.6 call_deferred](https://docs.godotengine.org/en/4.6/classes/class_object.html#class-object-method-call-deferred) describes idle-time execution; it is not a guarantee of one full-frame delay. Prospective trace must distinguish RPC entry/enqueue/end marker, subsequent queued callback and result acknowledgment. Getter0 is a prospective asserted outside-context result to verify, not a value to substitute if unexpected. If the actual callback context differs, stop and preserve it rather than retry with arbitrary extra frames. Capture does not make a connection ID a stable account identity or bypass later disconnect/ownership changes; those are excluded from the single-connection fixture.
