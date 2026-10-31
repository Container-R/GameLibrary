# Pre-runtime gate review

2026-10-31 21:45 UTC. No engine execution. Independently fetched public comparison commit 35e80b3a8822a9df9be390814b62f44c0a9c69e8: CollisionShape2D setter writes its member before owner call; CollisionObject2D owner setter also writes local member before server call; GodotPhysics2D area_set_shape_disabled invokes FLUSH_QUERY_CHECK before changing shape state. Area2D monitoring setter instead rejects locked changes before its local write. Therefore the two local-readback contracts must not be conflated.

Independently read CollisionShape2D disabled documentation and Object deferred semantics. Source supports a prospective scene-property/server-acceptance split and deferred ordering, not an authenticated installed-build guarantee or exact next-frame timing.

No material gate blocker, provided implementation freezes these controls: same marker/movement sequence for both configs; direct actual exit between first/second entries with same body identity; explicit phase for the finite outside/return horizon (physics_frame is pre-step); exactly one expected primary flush-query diagnostic plus restricted source/backtrace envelope, rejecting extra errors. Deferred negative re-entry observation is finite, not a proof of indefinite absence. Neither property true nor expected error alone suffices for acceptance.

The independent physical re-entry witness makes this distinct from previously observed business-state callback ordering. No automatic damage deduplication, physics safety, generic backend or universal latency guarantee follows. Parent and author notified before execution.

## Author pre-collision failures — source-only diagnosis, 21:49 UTC

Parent reported and reviewer read retained raw outputs: first startup failed with data-directory errors and signal 11; next attempt reached frozen initial-entry deadline without observing contact. Neither supplies a collision-mutation conclusion. Reviewer has not run any engine process. Current code geometry/layers appear consistent but no supported cause established.

Failure stdout lacks accumulated events/world/space diagnostics because current implementation emits result only after successful marker protocol. Recommended bounded readback before failure: scene/world/server space identities and active state, server shape counts/disabled status where exposed, actual global positions, inside-tree and monitoring/masks; preserve 20-boundary deadline. Exit handler currently ignores actual callback argument and logs intended body identity, so eventual acceptance requires logging/validating actual event body, as main also identified.

Independently fetched comparison source `scene/resources/world_2d.cpp`: get_space lazily creates and activates its space. `scene/2d/physics/collision_object_2d.cpp` ENTER_TREE assigns server transform and world space. This does not justify an unobserved activation fix. Initial guessed resources/2d path provided no usable content; corrected resources/world_2d.cpp was read. No fixture edits or new runtime were performed.

## Pairing-source check — 21:50 UTC

After parent supplied diagnostic same active space and coincident server transforms with no entry, independently read pinned modules/godot_physics_2d/godot_area_pair_2d.cpp and godot_area_2d.cpp plus Area2D constructor. Pair setup uses area collision mask and shape solver without a static-body exclusion. Backend monitor callbacks trigger shape registration updates; monitorable changes broadphase static classification. Scene constructor calls both monitoring and monitorable setters. These do not establish why this installed run has no event, nor justify changing body type as a fix.

Suggested remaining concrete readback gaps are server shape enabled/data/local transforms and server layer/mask versus scene metadata, plus monitorable. No new reviewer run, no supported engine-defect or universal static-body incompatibility conclusion. Parent retains authority over any further diagnostic execution; original finite failure must remain preserved.

## Separate kinematic configuration gate — 21:51 UTC

Independently inspected additional pinned source: godot_step_2d.cpp schedules constraints from moved-area and active-body lists; GodotBody2D::set_state TRANSFORM explicitly activates kinematic mode, while static mode updates transform/wakes neighbours; set_active refuses static activation. AreaPair constructor activates kinematic participants, and CharacterBody2D constructor specifies BODY_MODE_KINEMATIC.

This is a concrete source-grounded reason to propose a **new frozen CharacterBody2D configuration**, not proof that scheduling caused the installed static-body failure. Earlier note correctly rejected a blanket static-body exclusion at pair setup; scheduling paths supply additional context without overturning that limitation. Recommended preserve all three failed receipts, freeze changed body class/mode, retain geometry/horizons/relational checks, and avoid introducing move_and_slide or claiming controller-motion correctness. No reviewer runtime or implementation edits.
