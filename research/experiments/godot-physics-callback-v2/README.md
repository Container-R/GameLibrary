# Native physics callback mutation: kinematic-body revision

Frozen contract SHA256 `26f80627f6afea5413b664c3a4097118c437655b81fdfaa8ec47866b10aa6dde`. Original self-created circles only; no assets, controller, move_and_slide, game damage, or engine installation. Current hardened-runner author invocation `b3e7b2d4-351b-4342-8b6b-a084fda177f8` passed **two behavior processes plus one version query**, normal Python execution. Earlier v2 invocation `39536c18-7525-4dcc-b264-ca94a2097a2d` also passed the native comparison but used the pre-hardening parser; its runner and receipt are retained without rewriting. No additional stress or optimized-mode tests claimed.

## Why this is v2, not a repaired success for v1

V1 is retained separately at `../godot-physics-callback-v1/`: three failed invocations and exact source snapshots. First startup process returned -6 after data-dir errors; stderr separately printed a signal 11 crash diagnostic; next two never received initial contact. V1 totals three version queries plus three attempted direct processes, zero deferred. No accepted comparison.

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

## Parser hardening history and counts

Review found that the earlier parser checked stderr but could ignore an injected stdout ERROR/SCRIPT ERROR beside a valid result. Actual native logs were clean; this was a consumer acceptance gap, not a newly observed engine error. `historical-runner-before-stdout-guard/` preserves the old runner, and `stdout-guard.diff` shows the additive stream check and exposed pure parser. Current run.py SHA256 `2b00a96795564d2dc067928ceaa2f3c541ecc699873c80d9f9ae2d54a54f4803` rejects such stdout diagnostics before accepting results. Four isolated unittest methods exercise two actual records, stdout error mutations, extra stderr, and duplicate/missing results; these are parser tests, not extra engine cases. Run `python test_parser.py`; it reads the retained earlier raw records.

Main GDScript, project and frozen contract did not change during hardening. Author v2 totals **four behavior processes plus two version queries** across two distinct invocations, not four distinct configurations. V1 separately remains three failed direct attempts plus three version queries. Reviewer UUID `a253567d-2230-43ca-9e02-8a8eb8415367` independently executed two configurations plus one version query with the original v2 runner. Its raw records passed an independent literal oracle. After hardening, the reviewer checked the exact runner diff and pure parser normally and under optimized Python: two clean records accepted and sixteen synthetic mutations rejected in each mode, with zero further engine processes. No synthetic parser test is counted as a native run.

Independent review accepted behavior and hardened parser; see the separately integrated `review/REVIEW.md`. Its original receipt remains attributed to the original runner, not retroactively relabeled as a hardened-runner execution. This fixture is an extension candidate to existing fixed-step/combat material, not a new article or universal combat policy.

## Public archive layout

V1 failed receipts are adjacent at `../godot-physics-callback-v1/`; current and earlier v2 UUIDs remain in `results/`. Independent native and parser evidence is in `review/`. Original read-only reviewer scripts retain historical absolute paths; use `integration/check_archives.py V1_ROOT V2_ROOT REVIEW_ROOT` for relocated static evidence. It does not start Godot. Copy the four current source files into a new external directory and use an external output root for native reproduction; never overwrite these reviewed receipts.

Author `SHA256SUMS` reflects the handoff before public-layout prose edits, not a current documentation manifest. Runtime source digests remain bound by exact receipts. Original source gate predates the v2 revision and is retained as chronology, not the final implemented protocol.

Publication accounting: original v1 has 3 failed behavior attempts and 3 version commands. V2 has 3 accepted invocations (two author, one independent), each 2 behavior processes + 1 version command. Total 9 behavior attempts (3 failed, 6 accepted), 6 version commands, only 2 unique accepted configurations. Independent native repeat used the earlier parser and unchanged GDScript/project/contract; hardened parser was independently checked with pure-record mutations, not relabeled native execution.
