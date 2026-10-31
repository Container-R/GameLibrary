# Physics query callback mutation — implementation investigation, not accepted evidence

2026-10-31. Contract `68b53b919dbbc200f62b2a28932e8047eabcb03434ce64ff41dbb7812233dd6f` was frozen before code. Exactly two intended configurations; **neither comparison is established yet**. No new article or engine-bug claim. All three actual invocations stopped in the first configuration; deferred configuration has not run.

## Actual attempts preserved

1. `results/fb43cbe6-ccbd-4507-9e2f-a3d61e2da016`: one successful version query, one direct-config startup process returned -6; stderr printed a signal 11 crash diagnostic after data-directory creation errors. Runner set HOME/config/cache but omitted XDG_DATA_HOME. Exact source in `initial-startup-failure/`. No collision conclusion.
2. `results/a51adba6-2f98-4911-849f-a4a4b3831aac`: one version query plus direct process, initial entry deadline exceeded. XDG_DATA_HOME isolated; no horizon/oracle changes. Exact source in `initial-no-entry/`.
3. `results/1c95ee67-42da-438e-b857-becfdbc2aa10`: one version query plus direct process, same initial-entry failure. Exact source in `diagnostic-no-entry/`, also current. Added failure-only diagnostic trace, actual callback identity recording (not merely intended body's ID), and TMPDIR isolation. No state repair or extra waiting.

Total attempted so far: **three version processes + three direct behavior processes; zero deferred behavior processes**. No successful behavior configurations. Timeouts are external subprocess limits, not evidence all possible engine descendants are cancelled. Unique output directories retain raw stdout/stderr and source/binary hashes. No core dump or outside user file collected.

## Diagnostic observation

Third invocation reaches physics frame 25 with paused=false, one server shape on each object, same area/body/world space and space_active=true. Body and sensor server transforms both have origin (0,0), node shape disabled=false. No body_entered was observed. Therefore guessing a missing world-space activation is not supported by this trace. Shape presence, shared space and transforms do not alone prove collision-pair registration or callback delivery.

No four-boundary window was widened. SceneTree.physics_frame names a pre-node-physics boundary, not a completed solver step. No engine defect or changed API semantics inferred from this incomplete fixture.

## Additional comparison-source inspection

Public comparison commit `35e80b3a8822a9df9be390814b62f44c0a9c69e8`:
- scene/resources/world_2d.cpp get_space creates and activates a space.
- scene/2d/physics/collision_object_2d.cpp ENTER_TREE assigns that space.
- scene/main/scene_tree.cpp physics_process emits physics_frame before node processing; transform notifications flushed afterward too.
- main/main.cpp flushes physics queries before SceneTree physics_process, then steps physics after it.
- modules/godot_physics_2d/godot_physics_server_2d.h defaults active=true.
- scene/2d/physics/area_2d.cpp constructor enables monitoring/monitorable; monitoring installs callback.
These source branches are diagnostic leads, not authenticated exact installed binary source or a diagnosis of absent entry.

Public getter documentation inspected: https://docs.godotengine.org/en/4.6/classes/class_physicsserver2d.html . Gate docs and original expected setter boundary remain in `../physics-callback-native-gate/gate.md`.

Installed binary identity caveat: shared `research/source-notes/godot-runtime-provenance.md` applies; public comparison commit and self-reported installed hash differ. Raw binary digest/version preserved per invocation. No safety, authenticity, or engine-bug inference.

## Narrow source-supported hypothesis, not executed diagnosis

After stopping runtime, inspected comparison source at the same public commit:
- `modules/godot_physics_2d/godot_step_2d.cpp` lines 139–205: constraint island construction from moved areas and active bodies.
- `modules/godot_physics_2d/godot_area_pair_2d.cpp` constructor (around lines 94–103): explicitly activates a kinematic body to process the pair; no equivalent static activation there.
- `modules/godot_physics_2d/godot_body_2d.cpp` lines 303–328: kinematic transform branch calls set_active(true), static branch updates transform and wakes neighbours.
- `modules/godot_physics_2d/godot_area_2d.cpp` lines 48–62: area shape/transform changes place it on moved-area list.

Our area stays stationary after initial setup; only a StaticBody2D moves. Therefore lack of active-body/moved-area constraint processing is a concrete hypothesis consistent with the observed no-entry trace. It is **not** proven against the installed binary, and not a claim that Area2D can never detect StaticBody2D. A kinematic body or moving sensor would be a **newly frozen revised experiment**, not silent repair or successful evidence for the original protocol. No such change or execution has been made. Native acceptance remains blocked for this original fixture.

Public layout note: original gate is archived in the adjacent v2 directory as `../godot-physics-callback-v2/source-gate.md`; the relative draft locator above records the original workspace. These v1 receipts remain FAIL even after the separately frozen v2 succeeds.
