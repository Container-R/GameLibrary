# Main source read: independent channel order versus readiness

2026-11-01 UTC. Directly read upstream ENet commit `2662c0de09e36f2a2030ccc2c528a3e4c9e8138a`: design.dox Sequencing/Channels/Reliability (35–86), ENetChannel state (242–252), ordinary acknowledged outgoing sequence assignment (peer.c 637–658), and contiguous completed reliable-prefix dispatch (808–843).

The branches select per-channel sequence state; dispatch moves that channel's completed prefix into the peer dispatch queue. They do not inspect an application entity's creation/readiness dependency. The special control-channel branch is outside the example. Reading these branches is not a full protocol audit or proof of particular packet timing.

Also directly read Godot 4.6 High-level Multiplayer: modified ENet statement, RPC matching NodePath condition, transfer-mode documentation and Channels (227–234). Godot's separately documented streams support the high-level distinction without authenticating a modified implementation against upstream ENet. The existing dispatcher premise avoids conflating missing target-node routing with the application's missing entity prerequisite.

The two-message possible ordering is legitimate only as a hypothetical delivery allowed by independent streams, not an observed reorder. Same-channel transport delivery does not prove an asynchronously initialized entity ready. An application readiness acknowledgement needs an explicit lifecycle milestone; a transport acknowledgement is not that milestone. Generation matching avoids accidental replacement identity but supplies neither readiness nor authorization.

No packet exchange, fixture, network capture, model or runtime execution occurred. Prior prediction and RPC evidence remains unchanged. No numeric loss, deadline or eventual-delivery guarantee is derived.
