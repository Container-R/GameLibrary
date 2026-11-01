# Independent character transit protocol review

2026-11-01 01:32 UTC. Accepted candidate protocol SHA256 `193a8a05c6034ed59152b5c6c948139a1bc4c44068a27232ce38b1b971cfca41` for implementation review only. No engine/version/API query, motion, model or fixture execution.

## Source and identity check

In addition to the earlier SOURCE-REVIEW, independently fetched public commit35e80b3a8822a9df9be390814b62f44c0a9c69e8 scene/3d/physics/kinematic_collision_3d.cpp lines67–112 and collision_shape_3d.cpp82–90. The local/collider shape getters resolve a shape-owner object; a CollisionShape3D child creates an owner using itself. Therefore this scene's expected shape objects are the respective CollisionShape3D nodes, not their Shape3D resources. The protocol correctly freezes both roles and validates owner/resource/index mappings without asserting all owner objects have that type.

## Bounded design accepted

One wall and two independent sphere actors, identity transforms, separated lanes and explicit masks provide the intended counterexample: clear initial/requested endpoint occupancy need not imply an unobstructed intervening displacement. The actual motion calls, not the stationary controls, must establish transit obstruction.

The positive wall query is bounded to one per readiness callback, at most120, with exact expected collider/index; unexpected hits fail rather than silently retry. Four fixed empty occupancy controls run on the first successful callback before either move. Query count is readiness attempts+4, derived from records, not falsely fixed at five. Shape parameters, exclusions, mask, query margin/motion, maximum results and callback/frame are specified.

Exactly two actual inherited move calls use explicit displacement4/test_only=false/method margin0.001/recovery_as_collision=false/max_collisions1. Blocked oracle is checked before the open call. Actual pre/post transforms and returned travel/remainder supply movement evidence; CharacterBody slide properties/getters do not substitute. No direct correction, second move, remainder slide or post-call probe is allowed.

The frozen blocked center/contact intervals, normal bounds and finite1e-5/1e-4 consistency tolerances are original acceptance criteria, not a derived global physics bound. They reject zero progress and passing through the wall without requiring exact1-minus-margin. A mismatch is a preserved failed hypothesis, not permission to tune after execution. The open control requires actual full displacement and null collision, not a fabricated zero-contact object.

Backend is explicitly a selected configuration readback; PhysicsServer class is diagnostic, and source/build provenance remains unauthenticated. Actual _physics_process observation is distinguished from a completed whole solver step. Input/result/resource/body identities are process-local and not assumed positive.

Fresh source/receipt binding, prelaunch guards, bounded process attempts and fail-closed errors remain required in implementation. Pure ownership/type/contact/occupancy/receipt mutations must not be counted as physics cases. No native failure cleanup, universal CCD, slide controller, navigation agreement, game arrival or performance claim is authorized by this protocol.

No material protocol correction requested. Exact implementation/pure-test review and separate coordinator native authorization remain necessary.
