# Physics callback mutation gate: property readback is not physical acceptance

2026-10-31 21:43 UTC. Source gate only, no engine execution, no fixture code or main/remote changes.

## Current evidence, actually inspected

Baseline `gamelibrary-publish-graphics-role/solutions/programming/fixed-step-simulation-boundary.md` SHA256 `6736206936c526f049b724063f2b97645157ab77ea257b6ffa7264a2b89e79b3` (matches preceding native-root stage).

Exact metadata:
`verification_method: 原始文档核对、原创模型与本地Godot实际无头回调夹具；未运行Unity或跨平台确定性测试`

Read `research/experiments/godot-combat-policy/README.md` and `main.gd`. The actual four configurations use independent Node `_physics_process` callbacks, Begin/A/B/End priorities, HP snapshots and intents. There are **no physics bodies, contact detection or hitbox mutations**. The README explicitly excludes physics contacts. This is a genuine new physics-query boundary, not another canonical actor-order test. A guessed actor.gd path was absent; actual implementation is main.gd and was read.

## Specific question

When a combat Area2D receives body_entered and disables its own CollisionShape2D immediately, does the scene property saying `disabled=true` prove the physics server accepted the change? Compare with the documented deferred setter. The useful distinction is **scene-side requested state vs accepted physics participation**, not “deferred always means next tick.”

## Primary docs, read 2026-10-31

1. Godot4.6 CollisionShape2D disabled:
https://docs.godotengine.org/en/4.6/classes/class_collisionshape2d.html
The property should be changed using set_deferred.
2. Godot4.6 Area2D overlap queries:
https://docs.godotengine.org/en/4.6/classes/class_area2d.html
Overlap lists update during physics processing, not immediately upon movement. body_entered/exited require monitoring. Its different method descriptions use slightly different frame wording; do not turn them into an exact universal latency assertion.
3. Godot4.6 Object set_deferred / call_deferred:
https://docs.godotengine.org/en/4.6/classes/class_object.html
Deferred calls run during idle flushing, potentially at the end of process or physics frames; same-thread enqueue order is preserved. Nested deferred work can execute in the same idle cycle. Thus “deferred” is not guaranteed to mean one whole frame later.

## Fixed comparison source, read through GitHub plugin

All at public commit `35e80b3a8822a9df9be390814b62f44c0a9c69e8`:

- https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/2d/physics/collision_shape_2d.cpp#L194-L204 : set_disabled first writes its member, then calls collision_object's owner setter; is_disabled returns that member.
- https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/2d/physics/collision_object_2d.cpp#L319-L336 : owner disabled member is written before server setter calls. Thus node/owner property readback alone is insufficient to prove server acceptance.
- https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/modules/godot_physics_2d/godot_physics_server_2d.cpp#L41-L42 : FLUSH_QUERY_CHECK refuses state changes while flushing queries in a space. area_set_shape_disabled lines351–357 and body_set_shape_disabled650–656 check before changing the server shape.
- https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/2d/physics/area_2d.cpp#L191-L205 : body callback locks before signal emission. Alternative monitoring setter422–437 rejects while locked **before** changing its local property, unlike the shape path. Do not conflate these two setter contracts.

A first guessed server path under servers/physics_2d did not return source; corrected to modules/godot_physics_2d, not inferred from a failed fetch. No copied full implementation.

## Candidate minimal native experiment, not yet executed

Two fresh processes: `direct-shape` and `deferred-shape`. One Area2D sensor with one original CircleShape2D; one StaticBody2D with one original shape, matching explicit layers/masks. No image assets, motion animation, damage rules, extra bodies or installs. Backend explicitly GodotPhysics2D, default main thread; record actual backend/config and installed identity.

Start body separated, then place it at sensor center at a controlled non-query point. Wait for actual first body_entered with bounded failure deadline; no sleep pretending to synchronize.

In that first callback only:
- Direct: set sensor_shape.disabled=true. Freeze expectation of the specific flushing-queries error, scene property true afterward, but no claim physical disable succeeded. Do not treat any arbitrary stderr/nonzero exit as expected success.
- Deferred: enqueue sensor_shape.set_deferred('disabled',true). Immediately after enqueue property remains false. Enqueue a same-thread observation marker after the setter; at marker property must be true and callback must already have returned. No universal frame-number gap asserted.

Physical acceptance witness, independent of property: after the marker move the same body well outside, allow a predeclared finite observation window, then return it to the same center. Direct path is expected to produce a second entry because server-side shape remained active; deferred path is expected not to re-enter within the identical observation window. Record actual coordinates, shape data, masks, all entered/exited identities, callback/marker/movement order and Engine physics/process frame counters. A final overlap-list observation after explicit physics observation boundaries corroborates the event trace, not an immediate post-move query.

Proposed fixed horizon: four physics steps outside, four after return, with a separate bounded initial-entry deadline. This is **an experiment's observation window**, not a source-backed four-step engine guarantee. If events do not settle as expected, preserve the first failure and diagnose phase/backend/setup, rather than widening the pass horizon retrospectively. Could choose exact horizons at pre-code protocol freeze after reviewing SceneTree phase source; current source evidence does not justify “change always observed at N+1.”

Expected trace should distinguish enqueue-time false → marker true from physical overlap removal later. Direct branch may leave node property and server behavior inconsistent; therefore never “repair” the direct branch by toggling state before its witness. Both variants mutate only once in first entry. Collision disabling does not itself define game damage deduplication or cancel already dispatched contacts.

## Value, limits and stop condition

This tests why a hitbox state flag in a collision callback can be a false acknowledgment, and why combat should separately track business eligibility, physics mutation request and later physical observation. It does not solve same-tick damage policy; staged intent logic remains a separate application concern.

Installed build provenance caveat remains mandatory: binary SHA256 previously/currently measured `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`, self-report7d41c59c4 does not match public35e80b3a comparison source. Re-record version/hash if execution approved; no authenticity, unsafe-build or engine-bug inference. Shared note `research/source-notes/godot-runtime-provenance.md` applies.

Stop here pending gate approval. If exact phase timing cannot be frozen, retain only relational callback→deferred-marker ordering and bounded physical re-entry observation; do not claim universal next-tick semantics. No runtime yet and no new article quota. On approval preserve raw expected error plus all unexpected failures, unique run IDs and external deadlines; one control comparison is enough, not a new stress-test matrix.
