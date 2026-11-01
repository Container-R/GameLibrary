# Controlled NavigationAgent3D path completion — candidate protocol

2026-11-01. Status at freeze: proposed; separate main/independent acceptance required before implementation, and separate native authorization before execution. This document records prospective expectations, not results.

## Question and exact scope

Can an actual NavigationAgent3D finish a consumed partial path without reaching the requested target, while a reachable control emits target_reached before navigation_finished? Controlled Node3D position assignments supply movement; there is no CharacterBody3D, collision shape, move_and_slide, RVO, physics locomotion or AI state machine. The two agents are independent consumers of one immutable map.

Source gate: `research-drafts/navigation-agent-triage/gate.md` SHA256 `8066c7f5c728fd356fd3f7df90c651798064b0a65f08453ed22dd8f1fd186b6e`. Comparison source: Godot commit `35e80b3a8822a9df9be390814b62f44c0a9c69e8`, `scene/3d/navigation/navigation_agent_3d.cpp`, especially 705–765,799–923,984–1000. No per-frame no-op guarantee is assumed for repeated updating getters. Internal physics processing is not substituted for explicit path updates.

## Original geometry and configuration

One explicit NavigationServer3D map, two regions and two separate NavigationMesh resources. No bake or geometry import. Each mesh contains one convex quad at Y=0, with literal vertices/index order:

- Region L: vertices `(0,0,0),(0,0,4),(10,0,4),(10,0,0)`; polygon `[0,1,2,3]`.
- Region R: vertices `(20,0,0),(20,0,4),(30,0,4),(30,0,0)`; polygon `[0,1,2,3]`.

Single writer, one initialization batch. Map active; map/regions asynchronous iterations false; edge connections false; regions enabled and navigation layer1. Map cell_size and cell_height both0.25; explicitly set/read map up `(0,1,0)` (Vector3.UP). No navigation links, obstacles, unrelated regions or topology changes. Record actual vertices/polygons, map/region RIDs and getter values.

Two Node3D parents, each with a NavigationAgent3D child; exact parent/agent instance IDs must be integer/nonzero (not assumed positive), distinct and preserved through all records. Parent hierarchy and assigned map are observed. Both start `(2,0,2)`.

- Reachable target `(8,0,2)`.
- Disconnected target `(22,0,2)`.

Agents: navigation_layers1, avoidance_enabled=false, path_height_offset0, path_desired_distance0.1, target_desired_distance0.1, path_max_distance1.0, simplify_path=false; no limits truncating path (return max length/radius0, search max distance0, search max polygons4096), default A* and funnel explicitly set/read back. Path metadata flags7. Record all requested/read-back settings. No velocity setter or avoidance callback.

## Readiness, initial query and frozen geometry oracle

Before assigning targets, require this map's map_changed signal; initial map iteration0 becomes nonzero and differs from initial; each region iteration nonzero, assigned to this map/enabled/layer1, and exactly the two regions registered. Matching changed ID uses inequality, not universal monotonic greater-than. This is a single initialization batch, not a production concurrency barrier. Getter mismatch or more than240 physics callbacks while waiting is failure; no map_force_update or arbitrary sleep.

Query map closest-point and owner for both starts/targets. Require points unchanged within absolute coordinate tolerance1e-5 and each target owned by its intended L/R region. This excludes a disconnected goal lying outside all navigation surfaces. Actual link count must be0.

Set each target exactly once after readiness. On the next physics callback, perform the update/snapshot sequence below for both agents, but do not move either until BOTH initial path gates pass. Require each path nonempty, finite, starts at `(2,0,2)` and has expected endpoint within1e-5: `(8,0,2)` for reachable, `(10,0,2)` for partial. Every path point must have Y=0/Z=2 within1e-5 and nondecreasing X, within the appropriate start/end interval. Do not require a fixed number of intermediate vertices. This declared geometric oracle is not replaced with observed outputs after a failure.

At initial query both parents are far from target/path end; neither completion signal is expected. Require target-reachable getter true/false respectively, target-reached false for both, navigation-finished false for both. If any readiness/path gate fails, preserve sources/raw data and stop before movement. If BOTH initial path gates pass, that same initial-query callback performs the first0.5-bounded assignment for each agent under the movement phase below; it is driver callback1, not an extra uncounted setup movement.

## Every following physics callback: queries first, movement second

Bound at most48 driver callbacks, counting the initial query callback, after readiness. A separate wall timeout bounds the process. These bounds are watchdogs, not a frame-rate or arrival-time promise.

For each agent not terminal at callback entry, in fixed order Reachable then Partial:

1. Record phase `before_update`, actual parent position and frame/callback index.
2. Call exactly once each in this order: `get_next_path_position()`, `is_navigation_finished()`, `is_target_reachable()`, `get_final_position()`. **All four may update navigation.** No assumption that the last three are passive or cached no-ops.
3. Record the returned values and the non-updating `get_current_navigation_path`, `get_current_navigation_path_index`, `is_target_reached`, `distance_to_target`, plus parent position. Mark `after_queries`. Any signals produced by any of the four calls belong to the current query subphase.

Complete this query phase for BOTH active agents before assigning either parent position. Thus every updating call in that callback sees its parent's pre-assignment position; no updating getter is called after either parent moves.

For each agent whose finish latch is still false, compute `next_parent = old_parent.move_toward(actual_next_point, 0.5)` and assign it once. Log actual pre/returned-next/computed/actual post positions and `position_assigned`. Check exact intended displacement within1e-5, no overshoot or displacement above0.5+1e-5. Subsequent queries occur only in the next physics callback. This step length is a controlled positional driver, not velocity×measured time or physical motion.

If finish is latched during any query, do not assign that parent's position in this or later callbacks. Stop all driver activity after both finish latches and complete their post-query snapshot, emit the final record and exit. No speculative extra movement, target reset, repath or repeated completion probing. Final inspection includes no additional updating getters. Recorded absence of further signals is only within this finite observation window.

## Passive signals and literal semantic oracle

Connect path_changed, waypoint_reached, target_reached and navigation_finished before target assignment. Handlers append identity, signal name, current phase, actual parent position and physics frame; waypoint details may be recorded with exact supported types. Handlers never query updating methods, modify nodes or target, await, or perform movement. A navigation_finished handler only sets its own terminal latch after recording. Guard recording outside the declared observation window to avoid teardown reads; all unexpected engine diagnostics still fail.

Signals may arise during any of the four updating calls; do not require a particular getter as the sole emitter. Record call markers so order is attributable. Expected end states:

| Agent | target_reached signal | navigation_finished signal | Terminal position | Final reached/finished/reachable |
|---|---|---|---|---|
| Reachable | exactly1, preceding its finish | exactly1 | within0.1 of `(8,0,2)` | true / true / true |
| Partial | zero in window | exactly1 | within0.1 of `(10,0,2)`, farther than0.1 from `(22,0,2)` | false / true / false |

Every signal must belong to the exact registered agent and current parent; no callback claims from a different node. Both agents must have at least one observed position assignment and positive progress in X; initial positions cannot be relabeled as completed travel. Source geometry/path endpoints remain invariant within1e-5; parent positions remain on the declared straight segment. Navigation-finished latch agrees with actual getter result. Target arrival is not inferred solely from the finish signal.

The hypothetical application error is interpreting both finishes as requested-goal success. The guarded interpretation treats the partial result separately. No actual mission success, user outcome or universal requirement to reject partial paths is tested.

## Process, identity and failure contract

One author attempt consists of exactly one isolated `--version` query and one isolated headless behavior process; no scans, installs, renderer or network activity. Installed path `/usr/local/bin/godot` resolves to `/opt/godot/4.6.3/Godot_v4.6.3-stable_linux.x86_64`; required file SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`. Previously observed self-report is4.6.3.stable.official.7d41c59c4; exact version/schema will be bound in code review, not treated as authenticated official provenance.

Use exact isolation helper SHA256 `bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970`, minimal base PATH=/usr/bin:/bin, LANG=C, LC_ALL=C and five fresh invocation-root locations. Fresh UUID evidence directory; remove old summary before optimization/import guards. Per-process timeouts: version10seconds, behavior20seconds; own process group and bounded cleanup attempts. Preserve partial raw output/status even on failure; no automatic retry or geometry/tolerance adjustment.

Freeze all source/consumer/test/helper/protocol hashes before authorized native launch, retain before-after checks and binary hash. Reject duplicate/nonfinite JSON, unexpected stdout/stderr diagnostics, missing/multiple final payload, bool-as-int identities, unrelated source/output receipts and incomplete cleanup. Final acceptance only after process success, exact raw/parsed association and portable independent numerical/state oracle, not a child PASS string alone. No native failure-path result is promised by code inspection.

Independent source/code review and pure tests precede native authorization. A separate independent native repetition, if authorized after author success, uses identical frozen sources and counts separately. No code or native invocation is part of this protocol drafting step.
