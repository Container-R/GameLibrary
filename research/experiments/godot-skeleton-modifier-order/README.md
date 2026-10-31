# Native Godot look-at modifier order and pose observation

This original headless fixture tests two built-in LookAtModifier3D nodes on a two-bone Skeleton3D. It does not test a rendered character, skin deformation, foot contacts, general IK, AnimationMixer execution or Unity/Unreal ordering.

## Frozen input and scope

`contract.json` SHA256 `46d4965fb6b945e9acc0f5d41118747525a2545180af9181874933e6eb95ea65` was accepted before fixture code or native execution. Its status remains the historical pending-at-freeze value; approval was separate. Parent P is at the origin; child C has local rest/pose origin (0,1,0). Targets are fixed at (10,0,0) and (0,1,10). Forward axis is +Z, primary axis Y, relative false, duration zero, influence one, angle limits disabled. Base poses are reset to local rests, not treated as zero-position deltas added to rest.

The same skeleton, targets and modifier instances are used for both evaluations. The only intended input change is direct-child order via `move_child`. The fixture reads actual child IDs/order, bindings and settings; IDs are exact signed nonzero process-local integers. It uses MANUAL `advance(1/60)`, with no deprecated force-update API.

| Order | First stage global +Z directions (P, C) | Final directions (P, C) | Child forward/target dot |
|---|---|---|---|
| P then C | +X, +X | +X, +Z | 1 |
| C then P | +Z, +Z | +X, +X | 0 |

The runner checks all basis columns, positions, finite orthonormality and bindings with absolute component tolerance 1e-5, not only the forward vector. Child origin stays (0,1,0) because its offset is along the parent's yaw axis. This separates inherited orientation from changed origin/target distance.

## Actual observations and timing

Current accepted author receipt: `results/94105a77-e9f7-4367-ba9e-dfd4802f1224/receipt.json`. One native behavior process contains two evaluations; another process reports version. Both exited 0 with empty stderr. The observed stage and final bases match the frozen literals. Each separately deferred continuation sees both global bases restored to identity, with unchanged origins.

Setup modifier/final signals are retained and phase-tagged before the first drain marker. They are not counted as requested manual evaluations. Each armed evaluation records advance-call/return, two actual modifier signal emitters, `skeleton_updated`, then the deferred restored snapshot. Reading in a signal callback and reading afterward are intentionally different observations. An `await skeleton_updated` continuation would run within signal emission; it is not the post-restore read used here.

The initial complete oracle failed solely on an added `is_interpolating == false` assumption, despite native exit 0; details and pinned getter comparison are in [initial-failure.md](initial-failure.md). `historical-false-interpolation-oracle/` preserves the full initial sources and runner logs; initial raw evidence remains `results/d950544e-f0af-4068-aa0f-780ede638355/`. Current acceptance records the Boolean as a diagnostic, not a false/true success condition. Numeric duration and remaining time stay zero; all predeclared geometric expectations remain unchanged.

Author totals are **two behavior processes and two version queries**, one failed full oracle and one accepted full oracle; the two evaluations are repeated, not four distinct configurations. Independent review is now archived in the sibling draft `deep-qa/skeleton-modifier-order/` (intended publication under this experiment’s `review/`). UUID `6703fd88-731a-4879-8a5d-6f2ac968b3e2` repeats the exact final five sources with one behavior and one version process. Its separate literal raw oracle passes; six distinct synthetic mutations are rejected under normal and optimized Python, and one optimized-startup rejection clears a seeded summary before native execution. These negatives execute zero native processes. Combined author/reviewer history is three behavior processes and three version queries, with two accepted full oracles and the preserved initial failure; still only two distinct evaluation orders. Same-binary review is not independent engine implementation or build authentication.

## Reproduce without overwriting evidence

Create a fresh external disposable directory. Copy only `run.py`, `main.gd`, `project.godot`, `contract.json` and `isolation.py` into it. Run `python run.py` in that copy, or supply a fresh output directory as its first argument. Do not run inside this archive or its historical snapshot. Output folders use unique UUIDs; the success summary is removed before optimized-mode rejection or helper import. `-O` is intentionally rejected, not used to execute native tests.

The exact five-location helper is copied byte-for-byte from the new production helper, SHA256 `bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970`. This is additive use by a new runner, not migration of old fixtures or registration in the shared fresh harness. The helper prepares HOME, XDG_CACHE_HOME, XDG_CONFIG_HOME, XDG_DATA_HOME and TMPDIR in a fresh owned temporary root. It is not a sandbox, full-environment sanitizer or ownership authentication. Only selected paths, not the complete inherited environment, are logged.

Each native process has a 30-second external timeout; the behavior has a 10-second engine watchdog. Raw stdout/stderr/status are retained on failure and timeout. Unexpected diagnostics in either stream reject acceptance. The manifest records source hashes before execution and compares them after successful execution. Hashes bind this archive, not publisher identity or external authenticity.

## Runtime and source identity

Installed binary SHA256: `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`; runtime self-report `4.6.3.stable.official.7d41c59c4`. Its self-reported full hash is retained in the raw payload. Comparison source commit `35e80b3a8822a9df9be390814b62f44c0a9c69e8` does not match that self-report. Exact official build/source provenance remains unconfirmed; neither the word “official” nor repeated same-binary behavior authenticates it.

Sources read (2026-10-31):
- [LookAtModifier3D 4.6](https://docs.godotengine.org/en/4.6/classes/class_lookatmodifier3d.html): parent-before-child requirement and settings.
- [SkeletonModifier3D 4.6](https://docs.godotengine.org/en/4.6/classes/class_skeletonmodifier3d.html): per-modifier observation signal.
- [Skeleton3D 4.6](https://docs.godotengine.org/en/4.6/classes/class_skeleton3d.html): manual advance, skeleton-space poses, final signal and reset-to-rest.
- [Pinned sequential collection/processing](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/skeleton_3d.cpp#L1152-L1222).
- [Pinned backup, final signal, restoration and deferred advance](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/skeleton_3d.cpp#L311-L432).
- [Pinned parent-space look-at calculation](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/look_at_modifier_3d.cpp#L515-L606).

This finite evidence does not show arbitrary history independence, an optimal order for every rig, callback completion after an arbitrary frame, visible animation quality or device performance.
