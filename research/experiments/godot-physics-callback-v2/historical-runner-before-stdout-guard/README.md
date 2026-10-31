# Native physics callback mutation: kinematic-body revision

Frozen contract SHA256 `26f80627f6afea5413b664c3a4097118c437655b81fdfaa8ec47866b10aa6dde`. Original self-created circles only; no assets, controller, move_and_slide, game damage, or engine installation. Author invocation `39536c18-7525-4dcc-b264-ca94a2097a2d` passed **two behavior processes plus one version query**, normal Python execution. No additional stress or optimized-mode tests claimed.

## Why this is v2, not a repaired success for v1

V1 is retained separately at `../physics-callback-native/`: three failed invocations and exact source snapshots. First startup process returned -6 after data-dir errors; stderr separately printed a signal 11 crash diagnostic; next two never received initial contact. V1 totals three version queries plus three attempted direct processes, zero deferred. No accepted comparison.

V2 changes StaticBody2D to CharacterBody2D, and records/validates actual class and PhysicsServer2D body mode KINEMATIC=1. No movement solver call is introduced: the same coordinate assignments drive the same finite overlap sequence. Same radii 10/5, layers/masks1, positions(0,0)/(100,0), initial20-boundary deadline, four outside and four return boundaries, identical deferred marker in both configurations, same callback mutation and error oracle. Full isolated HOME/XDG_DATA_HOME/XDG_CONFIG_HOME/XDG_CACHE_HOME/TMPDIR retained. `v1-to-v2.diff` documents exact changes; v1 files were not rewritten.

Comparison-source hypothesis motivating revision: GodotStep2D processes moved-area and active-body constraint islands; GodotAreaPair2D activates kinematic bodies; static transform changes do not use that same activation branch. This justifies a separate kinematic control, **not proof of the exact reason v1 failed** or a claim Area2D cannot detect StaticBody2D.

## Actual bounded observations

| Observation | Direct setter inside first body_entered | Deferred setter inside first body_entered |
|---|---|---|
| Immediate CollisionShape2D.disabled | true | false |
| Same-thread deferred marker after callback | true | true |
| Diagnostics | Exactly one expected flushing-queries primary error, restricted source/backtrace envelope | Empty stderr |
| Actual callbacks | enter → exit → enter, same exact callback argument body ID | enter → exit; no second entry within fixed return window |
| Final overlapping-body list | same body | empty |

Both processes returned 0. Direct setter mutates scene state before server refusal: true property readback did not demonstrate physical disable. The return entry is a physical participation witness, not just duplicate notification; actual exit was observed between entries. Deferred path never toggles state back, and the same marker/movement protocol is used in both variants. Direct is deliberately not “repaired” before its witness.

The author recorded first entry/marker at physics frame 7, direct exit 9 and second entry 13; deferred exit 8. These are **observations of this invocation, not frozen exact tick expectations or universal latency**. Four SceneTree.physics_frame signals are pre-node-physics boundaries, not four independently confirmed completed solver steps. Deferred calls can run in the same engine frame. Event marker `callback_return` is the final recorded callback action, not native stack-return instrumentation; the later deferred marker and public deferred semantics establish the relational observation.

The backend and separate-thread fields are ProjectSettings configuration readback, not independent backend implementation authentication. Actual body class and body mode use object/server getters.

Actual body IDs are nonzero integers and compared exactly, including actual `who` arguments for enter/exit. They are process-local, may be signed, are not persistent identifiers, and should not be routed through lossy JavaScript Number parsing. Python JSON preserves integer tokens here. Cross-process equality or difference has no meaning.

## Reproduction and receipt limits

`python run.py --output-root /absolute/external/output-root` creates a new UUID directory and fresh temporary project. No existing result is read to decide success. Current source and binary hashes, argv, returncodes, timeout status, raw stdout/stderr, parsed results and output hashes are retained. Default output root is local `results/`; reviewers should use independent output paths. Each subprocess has a 20-second external deadline; this is not a universal OS cancellation/descendant-cleanup guarantee. Temporary project/home directories are cleaned. The legacy v1 archives are not touched.

No engine/runtime authenticity claim follows from self-consistent receipts. No crash durability, solver completeness, multi-contact scheduling, damage deduplication, collision threading, controller response, or all-backend/platform guarantee. Error acceptance is restricted to the expected direct setter diagnostic and its source/backtrace lines; nonzero process exit fails.

## Sources and provenance

Read Godot4.6 documentation: [CollisionShape2D disabled](https://docs.godotengine.org/en/4.6/classes/class_collisionshape2d.html), [Area2D](https://docs.godotengine.org/en/4.6/classes/class_area2d.html), [Object deferred calls](https://docs.godotengine.org/en/4.6/classes/class_object.html), [SceneTree physics_frame](https://docs.godotengine.org/en/4.6/classes/class_scenetree.html), [PhysicsServer2D getters](https://docs.godotengine.org/en/4.6/classes/class_physicsserver2d.html).

Fixed public comparison commit `35e80b3a8822a9df9be390814b62f44c0a9c69e8`:
- scene/2d/physics/collision_shape_2d.cpp194–204 writes local disabled member before owner/server call.
- scene/2d/physics/collision_object_2d.cpp319–336 writes owner state before server call.
- modules/godot_physics_2d/godot_physics_server_2d.cpp41–42,351–357 refuses shape mutation during query flushing.
- scene/2d/physics/area_2d.cpp191–205 signals inside locked callback processing.
- modules/godot_physics_2d/godot_step_2d.cpp139–205, godot_area_pair_2d.cpp constructor, godot_body_2d.cpp303–328 support the separately scoped kinematic revision hypothesis.

Installed binary digest `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`; self-report `4.6.3.stable.official.7d41c59c4`, fullhash `7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3`. This differs from public comparison source identity. Shared `research/source-notes/godot-runtime-provenance.md` caveat applies: not authenticated exact official source/build, no unsafe/fake/engine-bug inference.

Independent repeat pending. This fixture is an extension candidate to existing fixed-step/combat material, not a new article or universal combat policy.
