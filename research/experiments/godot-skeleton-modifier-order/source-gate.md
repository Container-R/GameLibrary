# Skeleton modifier ordering: native observation gate, not executed

2026-10-31 22:22 UTC. No fixture code or engine invocation. Target: depth addition to existing animation article, not a new generic Rig/IK claim.

## Actual current baseline, not inherited summary

Read `gamelibrary-work/solutions/animation/turn-in-place-foot-sliding.md`, SHA256 `a2737fba414f04ebfe7040c996da33a6a077104c0ec5e250f184699ebb258465`.

Exact verification metadata:
> verification_method: 官方版本文档与日本项目材料核对；4项Python二维模型测试；新增Godot原生两配置及独立两配置复跑（双方各另一次版本查询）；Rig六行表及真实角色/Unity/UE验证未执行

The four Python tests are 2D contact geometry. Actual Godot native evidence is a single-bone position/rotation animation with root extraction, repeated delta getter reads, and explicit zero/one/two applications to ordinary Node3D recipients. It does not execute the later Rig dependency worksheet, real IK, foot contacts or Unity/Unreal. That worksheet already requires order-only controls for member IDs, settings, target/bone references and world poses. The proposed experiment tests a **different built-in Godot modifier boundary**, not those unexecuted Unity cases.

## Primary documentation actually read

All Godot **4.6**, accessed2026-10-31:

1. https://docs.godotengine.org/en/4.6/classes/class_lookatmodifier3d.html — Description explicitly requires parent-bone LookAtModifier3D above child-bone modifier for correct child result. Properties `relative`, `duration`, `forward_axis`, `primary_rotation_axis`, `origin_from` and angle limitations clarify the proposed controlled input. This is a built-in look-at orientation mechanism, not a general hand/foot IK solution.
2. https://docs.godotengine.org/en/4.6/classes/class_skeletonmodifier3d.html — Description says target Skeleton3D is the parent; modifiers follow AnimationMixer playback if present. `modification_processed` is the documented moment to read that modifier's pose. Influence blending can occur around processing; proposed influence1 avoids conflating stage output with partial blending.
3. https://docs.godotengine.org/en/4.6/classes/class_skeleton3d.html — `skeleton_updated` means final pose/all modifiers complete; `pose_updated` does not report modifier processing. MANUAL mode uses `advance`, which accumulates delta for deferred processing. Bone “global” pose is skeleton-space, not world-space.

## Exact pinned comparison branches read

Public comparison commit `35e80b3a8822a9df9be390814b62f44c0a9c69e8`:

- https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/skeleton_3d.cpp#L1152-L1203 : collects direct-child SkeletonModifier3D IDs in child order, processes sequentially, refreshes dirty bone transforms after each. This is **not Unity's depth-first collection rule**.
- Same file lines1206–1222: move_child/add/remove notify invalidate modifier collection; `move_child` can alter order without reparenting or replacing members.
- Same file lines311–416: pre-modifier pose backup, modifier processing, skeleton_updated, skin update, then pose restore. Lines427–432: advance schedules deferred modifier update. Reading after advance returns or after an arbitrary frame can miss the actual modified pose.
- https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/skeleton_modifier_3d.cpp#L119-L124 : processing then modification_processed signal. Its signal can fire after a modifier returns early internally, so signal count alone is not evidence of successful aiming.
- https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/look_at_modifier_3d.cpp#L515-L606 : reads parent global pose for bone rest space, derives target direction, writes local bone rotation. `relative=false` uses rest for the local starting basis, but still reads current parent global pose. Duration0 disables the transition interpolation path; limits disabled/influence1 narrow history sensitivity.

No full implementation copied; these are source traces, not proof of installed exact source identity.

## Proposed geometry and falsifiable oracle — freeze before any code

Original identity-world Skeleton3D with two bones:
- Parent P: rest/pose identity at(0,0,0).
- Child C: parent index P, local rest/pose origin(0,1,0), identity rotation/scale.
- Independent target nodes outside the skeleton: P target(10,0,0), C target(0,1,10). Their world transforms remain fixed.
- Exactly two direct-child LookAtModifier3D nodes, assigned to P and C; forward axis+Z, primary rotation axisY, `relative=false`, origin_from SELF, offset0, duration0, influence1, active true, angle limitation false, `use_secondary_rotation=true`, `origin_safe_margin=0.1`. Skeleton callback MANUAL, physics interpolation disabled; no AnimationMixer, skin/mesh, custom modifier, solver or downloaded asset.

Original hand-derived expected orientation table, **not executed**:

| Modifier order | After first stage | Final parent +Z axis | Final child +Z axis |
|---|---|---|---|
| P then C | P rotates to+X; child inherits parent orientation | +X | +Z, aimed at its target |
| C then P | C initially remains aimed+Z under identity parent | +X | +X after parent rotation, no longer aimed at its target |

Child offset is onY, so parent yaw does not move the child's origin. Thus target error difference isolates inherited orientation rather than changed target distance or position. Use literal vector/basis geometric oracle, not equality between two summaries or quaternion-sign assumptions. Proposed tolerance1e-5 per normalized axis/position; child-target direction dot approximately1 versus0. Confirm orthonormal finite bases and unchanged origins. Exact Euler decomposition is unnecessary. If first actual run differs, preserve failure and inspect source/setup; do not fit expected vectors to observed output.

## Smallest useful A/B design and observation sequencing

Preferred **one fresh process with two explicit evaluations**, same skeleton, target nodes and modifier instance IDs. Evaluate P→C; after capture and completion, restore the identical known local inputs, reorder the same children using move_child, then evaluate C→P. No reparenting, reconstruction, target movement or member replacement. A second fresh independent reviewer repeat is separate evidence. If main requires explicit sequence-history control, a separately frozen second author process C→P then P→C is possible, but not silently added as more “cases.” With relative=false, duration0, limitsfalse and influence1, source indicates output is not interpolated from prior state; nonetheless record interpolation state and reject unexpected history dependence rather than claiming general statelessness.

Important asynchronous boundary:
1. Configure outside tree where possible; identify and tag any setup-only skeleton signals, not count them as manual evaluations. Drain setup work at a defined deferred marker before arming evaluation.
2. Capture both bones' local/global poses, target world transforms, skeleton world transform, bone parent/rest data, modifier IDs/settings/target/bone bindings and ordered direct-child IDs before each evaluation. IDs are process-local signed exact integers, nonzero; same members across A/B required.
3. Call advance with one fixed positive delta, 1/60. Do **not** read a final pose immediately afterward.
4. In each modification_processed callback, snapshot actual stage pose and emitting modifier ID; require exactly the intended two-stage order for the armed evaluation.
5. In skeleton_updated, snapshot final pose and stage sequence. Only accept the armed evaluation that has those two modifier signals; reject extra/missing evaluations rather than swallowing them.
6. Schedule the continuation with call_deferred from that signal. An `await skeleton_updated` continuation itself resumes *inside* the signal, before the source's restore loop: it is not an after-restore observation. The separately deferred continuation can record restored base poses and then prepare the next evaluation.

Do not invoke deprecated force_update methods to simulate completion. No need AnimationMixer: explicitly setting identical base poses removes animation timing as a variable, but therefore does **not** validate mixer/modifier ordering under actual animation. No skin means final pose signal is observed, not visible rendered deformation or character quality.

## Failure boundaries and feasibility decision

**Feasible and valuable**, conditional on freezing above geometry/settings/counts before execution. It can demonstrate that a modifier which individually aimed correctly may be invalidated by a later ancestor mutation, and that the correct observation signal matters because poses are restored. It does not establish universal correct order for all rigs or validate the article's Unity torso/hand-IK worksheet.

Risks to stop on: unsupported class/API in installed build; invalid bone/path binding; setup update accidentally counted; extra deferred evaluation; interpolated world transforms; duration/history not actually disabled; changed membership or targets; unexpected restored-pose behavior. One failed initial trace is diagnostic evidence, not permission to add warm-up loops or widen acceptance. Future runner must isolate HOME/XDG/TMPDIR, retain all raw output/failures, check both output streams, use unique receipt, external timeout and source/binary hashes. No native code has been created or executed at this gate.

Installed binary previously measured SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`, self-report `4.6.3.stable.official.7d41c59c4`, fullhash `7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3`; public comparison is35e80b3a. Re-record if execution approved. Shared `research/source-notes/godot-runtime-provenance.md` caveat applies: no exact official-build/source authentication, no unsafe/fake/engine-defect inference.
