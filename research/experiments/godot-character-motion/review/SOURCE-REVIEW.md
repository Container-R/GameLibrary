# Independent CharacterBody motion source gate

2026-11-01 01:29 UTC. Accepted for a bounded protocol only; no fixture implementation, engine/version invocation, collision query, motion or model execution.

## Direct primary-source read

Opened official Godot4.6 [PhysicsBody3D](https://docs.godotengine.org/en/4.6/classes/class_physicsbody3d.html), [CharacterBody3D](https://docs.godotengine.org/en/4.6/classes/class_characterbody3d.html) and [KinematicCollision3D](https://docs.godotengine.org/en/4.6/classes/class_kinematiccollision3d.html). Independently fetched public comparison commit35e80b3a8822a9df9be390814b62f44c0a9c69e8 files scene/3d/physics/physics_body_3d.cpp and character_body_3d.cpp; read cited87–162 and40–134/399–454/684–693 ranges.

The inherited method consumes displacement and explicit margin/test/recovery/count arguments. Its wrapper starts from the actual transform; the non-test path applies returned travel after recovery/axis-lock handling. Slide instead integrates velocity with delta and maintains separate movement/platform state. Thus CharacterBody's slide margin property and slide-related getters must not substitute for the inherited method's arguments and actual before/after transforms. Returned collision travel/remainder and collider identity are suitable evidence; source does not promise an exact ideal contact coordinate for arbitrary setup.

## Existing evidence gap checked

Current article2272a85f explicitly excludes character collision movement. The old radius fixture's stationary overlap tests and the newly accepted completion fixture's uncollidable Node3D assignments remain insufficient to establish transit obstruction. A real CharacterBody3D inherited move call therefore adds a distinct useful witness without requiring a full controller or nav-to-controller integration.

## Protocol constraints

- Freeze two independent identity-scale sphere actors and one wall with exact local/global transforms, dimensions, shape enabled state, body class/mode, collision layers/masks and all axis locks. Prevent actor-actor influence explicitly; clear endpoints alone do not show a clear intervening route.
- Freeze configured backend/thread settings and distinguish a ProjectSettings configuration readback from independently authenticated implementation identity. Retain the shared installed-binary/public-source caveat.
- Define a bounded readiness phase with actual wall identity from a positive query, plus each actor's start and requested endpoint clear. Freeze query geometry, margin, mask, exclusions, maximum results, call order and maximum/count recording. These controls establish particular occupancy/visibility observations, not a universal synchronization barrier. No unrecorded repeated probes or arbitrary sleep.
- Only after all controls pass, perform exactly one move_and_collide per actor with explicit test_only=false, method safe_margin0.001, recovery_as_collision=false and max_collisions1. Record actual call arguments and pre/post transforms; do not perform post-call direct position correction or feed velocity without integration.
- For the blocked result bind collider ID/RID and documented shape ownership/index to the actual wall. Keep nonzero integer identities without positivity assumptions. Predeclare finite tolerances for travel versus transform displacement, travel+remainder versus requested motion, negligible lateral movement, normal/contact interval and partial positive forward travel. Do not assert exact1-minus-margin contact. The open control must return null and actually move4 units.
- Preserve first unsupported readiness/body/shape/backend/error/oracle result and stop. A failed result cannot authorize a backend/body/margin/threshold sweep. Query counts, two move calls and version/behavior processes must remain separate.

This narrow case can demonstrate endpoint occupancy versus intervening obstruction for its chosen geometry. It cannot establish arbitrary continuous collision safety, CharacterBody move_and_slide behavior, stairs/platforms/pushing, gravity, performance, physical safety of older navigation paths or completed gameplay arrival. Protocol/code review and separate runtime authorization remain required. No material source blocker identified.
