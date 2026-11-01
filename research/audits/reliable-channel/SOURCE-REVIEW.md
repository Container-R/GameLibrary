# Reliable channels and entity readiness — source review

2026-11-01 UTC. **ACCEPT the standalone source-note gate.** Reviewed gate SHA256 `0639ccaa077241a325236c46987e506ac06a93ea261eb8cea3f40713553db787`. No correction required.

## Originals independently read

The upstream tag API resolves ENet `v1.3.18` to `2662c0de09e36f2a2030ccc2c528a3e4c9e8138a`.

- [Design: Sequencing / Channels / Reliability](https://github.com/lsalzman/enet/blob/2662c0de09e36f2a2030ccc2c528a3e4c9e8138a/docs/design.dox#L39-L83): independent channel sequencing and receipt acknowledgements support the proposed distinction; retransmission does not certify application completion.
- [ENetChannel](https://github.com/lsalzman/enet/blob/2662c0de09e36f2a2030ccc2c528a3e4c9e8138a/include/enet/enet.h#L242-L252), [outgoing command setup](https://github.com/lsalzman/enet/blob/2662c0de09e36f2a2030ccc2c528a3e4c9e8138a/peer.c#L637-L658), [incoming reliable dispatch](https://github.com/lsalzman/enet/blob/2662c0de09e36f2a2030ccc2c528a3e4c9e8138a/peer.c#L808-L843): selected-channel sequence state and contiguous completed-command dispatch agree with the design. The special control-channel branch is not an entity-readiness mechanism. No application creation milestone is checked in these inspected branches.
- [Godot 4.6 High-level multiplayer](https://docs.godotengine.org/en/4.6/tutorials/networking/high_level_multiplayer.html#channels): Channels (227–234), matching NodePath requirements (160–164), and modified ENet statement (44) independently read. The documented independent streams support the high-level concern; upstream ENet is not thereby established as the exact Godot implementation. No immutable Godot implementation identity is inferred.

## Scenario and intervention boundaries

Two ordinary messages to an already-existing dispatcher avoid confusing entity readiness with a missing RPC target. Under the explicit delayed-A/no-gap-B premise, cross-channel ordering permits ApplyAction to be delivered first. This is an allowed ordering, not an observed packet trace, frequency, mandatory outcome or claim about MultiplayerSpawner internals. Channel independence means absence of that sequencing dependency, not independent bandwidth, congestion resources or guaranteed low latency.

Same-channel reliable delivery orders the messages, but cannot make an asynchronously initiated create operation complete before application handling of the next message. A readiness acknowledgement must denote an application-defined milestone, not a transport ACK. The gate appropriately keeps its validity at action handling, session/entity/generation identity, expiry and retirement as separate questions.

Generation distinguishes incarnations; it neither creates readiness nor authorizes a sender. The rejection/defer/resynchronization choices remain original proposals rather than a verified lifecycle implementation. No recommendation to consolidate all traffic or promise eventual success follows.

The existing prediction/dependency-time/RPC scope is not upgraded. A compact standalone note can add this precise ordering/readiness distinction without another packet model or native test. No executable code, packet session, engine invocation, installation, experiments or remote writes performed.
