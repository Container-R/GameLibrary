# CharacterBody3D transit obstruction — candidate protocol

2026-11-01. Source-only protocol, pending independent/main acceptance. No fixture or native invocation is part of drafting. Geometry/tolerances/counts below are prospective acceptance criteria, not measured results.

## Purpose and fixed scope

Two actual inherited `move_and_collide` calls on two CharacterBody3D actors compare a blocked lane with a clear parallel lane. Both initial and requested endpoint shapes are non-overlapping with the wall; only the intervening transit is blocked. This closes a finite actual-motion gap, not a complete navigation/controller integration. No NavigationAgent, move_and_slide, test_move, test_only movement, direct post-call teleport, gravity integration, stairs, rotation, moving platforms or RVO.

Source gate SHA256 `03eaf1c25cecde4d404c573804601a8d5e4635be41cc5b689bbb31bf2d212fc6`, independent SOURCE-REVIEW `c9fd7aee` (full digest in separate review). Existing SOL-AI-001 and its fixtures remain untouched.

## Original geometry and identities

Root Node3D, identity transform. StaticBody3D Wall at `(2,0,0)` with one enabled CollisionShape3D child, local identity transform, BoxShape3D size `(1,4,2)`. Its bounds are X[1.5,2.5], Y[-2,2], Z[-1,1]. Wall collision_layer2, collision_mask1; zero constant linear/angular velocity. No other static body or Area3D.

Two CharacterBody3D actors, Blocked at `(0,0,0)` and Open at `(0,0,4)`. Each has exactly one enabled identity-local CollisionShape3D holding its own SphereShape3D radius0.5. All global/local basis matrices remain identity, scale1; no rotations/nonuniform scale. Both collision_layer1, collision_mask2, empty exceptions and all six axis locks false. Their shapes cannot collide with each other under these masks. CharacterBody velocity explicitly zero and safe_margin property explicitly0.001, recorded but not used as a substitute for the method argument. No slide-specific state is treated as movement evidence.

Record all node instance IDs (integer/nonzero, not assumed positive), body RIDs, shape resource IDs/RIDs, shape-owner IDs and body-local shape indices. Bodies and nodes must be distinct; resources for the two actor shapes and separate query shape also distinct. Query shape is another SphereShape3D radius0.5, not attached to a body. Shape indices are0 for each single-shape body. Server body mode must match STATIC for Wall and KINEMATIC for actors, using explicit enum comparisons rather than guessed numeric values.

### Shape ownership oracle from inspected source

Pinned commit `35e80b3a8822a9df9be390814b62f44c0a9c69e8`:

- [kinematic_collision_3d.cpp67–74](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/physics/kinematic_collision_3d.cpp#L67-L74) resolves local shape index to shape owner object.
- [kinematic_collision_3d.cpp96–112](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/physics/kinematic_collision_3d.cpp#L96-L112) resolves collider shape owner and exposes collider shape index.
- [collision_shape_3d.cpp82–90](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/physics/collision_shape_3d.cpp#L82-L90) creates an owner with the CollisionShape3D node (`this`) and adds its Shape3D resource.

Therefore in THIS scene `get_local_shape(0)` must identify the Blocked CollisionShape3D NODE, and `get_collider_shape(0)` the Wall CollisionShape3D NODE, not their SphereShape3D/BoxShape3D resources. Validate through actual `shape_find_owner(0)`, `shape_owner_get_owner`, `shape_owner_get_shape_count` and `shape_owner_get_shape` mappings. Do not generalize the owner-object type to shapes created through other APIs.

## Physics configuration and readiness queries

Project explicitly selects `physics/3d/physics_engine="GodotPhysics3D"`; record and require its ProjectSettings readback. This is selected backend configuration, not independent native provider instrumentation. Record PhysicsServer3D class name diagnostically without inventing an engine-provider identity from it. Headless rendering choice is not a physics proof.

All operations run in an actual Node `_physics_process(delta)` callback after setup. Record callback count, Engine physics frame and finite positive delta; do not infer a completed whole physics step or measure performance. Setup geometry/configuration and body shape ownership must validate BEFORE any query or motion.

Readiness: per callback, at most one `direct_space_state.intersect_shape` query at the Wall center `(2,0,0)` using the separate radius0.5 sphere. Query transform basis identity, margin0, motionZERO, collision_mask2, collide_with_bodies=true, collide_with_areas=false, exclude BOTH actor RIDs, max_results4. Record each attempted query with parameters and full returned collider ID/RID/shape-index fields. Empty result means pending; an unexpected object/index is failure, not a retry. Exactly one Wall hit with shape index0 establishes positive geometry visibility. Maximum120 such callbacks/queries; no arbitrary sleep/force update or universal readiness claim.

On the FIRST successful positive-query callback, perform exactly four more intersect_shape queries, using identical parameters except origin, in order:

1. Blocked start `(0,0,0)`.
2. Blocked requested endpoint `(4,0,0)`.
3. Open start `(0,0,4)`.
4. Open requested endpoint `(4,0,4)`.

Require all four results empty. These are stationary occupancy gates, not transit proof. No native `cast_motion`, test_move or test_only call. Total stationary query count on an accepted invocation is `readiness_attempts + 4`, with readiness_attempts between1 and120. Counts are derived from raw query records, not a hard-coded claim. No actor position changes before all five successful-callback gates pass.

## Exactly two actual moves

On that same successful callback, after the four empty controls, call Blocked then Open once each:

`move_and_collide(Vector3(4,0,0), false, 0.001, false, 1)`

The vector is a fixed displacement of4 units, not velocity. This finite experiment has no speed/frame-independence claim. Record exact call arguments, entry/return markers, same callback/frame, pre/post global Transform3D, and actual position difference. No motion is applied before or between these calls through another API.

After Blocked returns, validate its finite motion/collision oracle before calling Open. Any failure preserves partial output and stops; do not continue to obtain a convenient control after a failed gate. After both calls record final transforms/settings and finish observation. No second movement, manual remainder slide, post-call overlap or native retry. Teardown occurs outside the observation window and does not suppress diagnostics.

## Frozen numerical and identity oracle

All numbers must be finite before abs/comparison; booleans cannot stand in for integer IDs/counts. Input transforms, dimensions and settings use absolute component tolerance1e-5 (float representation permitted). Bases remain identity1e-5. Nonzero IDs are opaque process-local values, matched by role, not hard-coded across runs.

Blocked:

- Returned collision non-null, exactly1 reported contact, actual collider object/ID/RID equals Wall, collider shape index0.
- Returned local/collider shape owner objects equal the declared CollisionShape3D nodes; owner/resource maps remain unchanged.
- Actual final center X in `[0.95,1.05]`, Y/Z within1e-5 of0. This broad near-contact interval rejects immediate no-progress or wall traversal; it does NOT assert the center equals1−margin or a universal contact precision.
- `travel` agrees componentwise with actual post−pre displacement within1e-5; X positive and less4. `travel + remainder` agrees with requested `(4,0,0)` within1e-4; remainder X positive. These equalities apply only to this non-overlapping, axis-aligned setup and no locked axes, not all depenetration cases.
- Contact normal X<=−0.99, absolute Y/Z<=0.01 and length within0.01 of1. Contact position X in `[1.45,1.55]`, absolute Y/Z<=0.1. Collider velocity equals zero1e-5. Depth is recorded and finite, with no exact depth-value oracle.
- No exact motion fraction, ideal surface intersection or byte-equal floating result required.

Open:

- Returned collision null; do not call collision getters on null or fabricate zero-contact KinematicCollision3D.
- Actual final `(4,0,4)` and displacement `(4,0,0)` within1e-5; identity basis unchanged.

Both actors' initial/endpoints were clear under recorded stationary controls, yet only Open realizes the full displacement. No getters `get_position_delta`, `get_real_velocity`, `get_last_motion` or slide collision getters are used; they belong to the slide path, not this result. No scene velocity is interpreted as actual displacement.

## Runtime/archive boundary

One author attempt, if separately approved after code review: one isolated --version process then one isolated behavior process; source/runtime identity and raw error gates apply to both. Fixed binary SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`, path `/usr/local/bin/godot`, previously recorded self-report4.6.3.stable.official.7d41c59c4. Exact self-report dictionary is pinned in implementation review, not authenticated official source provenance.

Version timeout10seconds; behavior20seconds. Exact isolation helper `bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970`; minimal base PATH=/usr/bin:/bin, LANG=C, LC_ALL=C plus its five fresh paths. Fresh UUID, stale-summary removal before optimization/import guards, all fixture/runner/oracle/consumer/test/helper/protocol source manifests before/after, binary before/after, raw stdout/stderr and process receipt retained. No PASS until process exit0, empty diagnostic streams, exact raw/parsed association and portable numerical/identity consumer pass. Timeout cleanup is attempted/bounded and honestly records unresolved state, not a blanket containment promise.

Pure tests before native must include finite movement/contact/owner-node-versus-resource/occupancy mutations, typed IDs, malformed raw JSON and complete synthetic archive guards; they do not constitute physics results. Any initial source/capability/runtime/oracle failure is retained with exact bytes; no tolerance/backend/geometry sweep. Independent native repeat requires separate authorization after author success.

This finite witness does not prove general CCD, corridor clearance, collision-free future motion, navigation/physics agreement, slide behavior, controller responsiveness, game mission arrival, dynamic interaction or performance. It closes only the recorded static-wall transit obstruction boundary.
