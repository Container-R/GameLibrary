# Gate: actual Godot physics callback order versus same-tick combat policy

2026-10-31 19:35 UTC. **Gate only: no engine launched, no new fixture or callback result.** Recommend a bounded actual-engine integration, provided coordinator approves four fresh processes. It adds scheduling evidence missing from the reviewed Python policy; do not merely call a Python/GDScript sorted loop and label it engine scheduling.

## Existing coverage inspected

Read simultaneous-combat-policy README and existing godot-fixed-step main.gd/run.py/README. Chosen original combat policy: actors/targets alive at tick start qualify; qualifying attacks survive same-tick death; damage batch committed after eligibility. A/B eachHP1 with mutual damage1 should both die. Deliberate sequential-first-strike alternative is not an engine bug or intrinsically unfair rule.

Existing real Godot fixed-step fixture uses one physics callback to update integer state, varying main-frame scheduling. It does not compare independent actor callbacks that mutate shared HP. Existing Python supplement shows stable sorting can still implement a different policy, but never exercises Godot callback dispatch. Proposed experiment therefore has a genuine integration gap.

## Official API and pinned source read

Godot4.6 Node docs, accessed2026-10-31:
https://docs.godotengine.org/en/4.6/classes/class_node.html#class-node-property-process-physics-priority
and #class-node-private-method-physics-process . Exact property `process_physics_priority`; setter `set_physics_process_priority`, getter `get_physics_process_priority`. Do not mistakenly set `process_priority` for physics. Lower physics priority runs first; equal priorities use tree order. `_physics_process(delta)` requires enabled physics processing and tree membership; override auto-enables. `set_physics_process(false)` disables future callback dispatch. `_ready` runs children before parent; initialize deliberately rather than relying on parent-ready already having configured a child's first behavior.

Thread groups matter: restrict all nodes to same inherited default main-thread process group, no subthreads/group-order changes. This is not a universal cross-group ordering guarantee.

Official Godot4.6.3-stable comparison pin `35e80b3a8822a9df9be390814b62f44c0a9c69e8`, fetched via GitHub plugin:
- https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/main/node.h#L186-L192 : physics comparator orders priorities, then tree position.
- https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/main/scene_tree.cpp#L1151-L1209 : physics node list sorted when dirty, copied for dispatch, eligibility/tree checks, physics notification; deferred queues flush around group processing. This is callback traversal, not simultaneous HP semantics.
- https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/main/node.cpp#L91-L97 : physics notification invokes virtual callback.
- same Node.cpp1168–1185,4058: property setter stores priority/re-registers as needed; exposed property maps to physics setter.

These are inspected source semantics, not proven exact installed binary implementation. No source excerpts/code copied into proposed fixture.

## Proposed four-case actual schedule

Each fresh process creates A and B with fixed tree insertion orderA thenB. Swap only declared physics priorities: A0/B10 versus A10/B0. Same main-thread group. Do not sort actors manually to impersonate scheduler; each actor's actual `_physics_process` records its own entry and does the chosen work.

Cases:
1. immediate, A priority0 B10: first actor checks currentHPs and immediately applies damage; predicted finalA1/B0, one damage/death.
2. immediate, A10 B0: predicted A0/B1, actor-entry order reversed. First callback advantage follows real priority, not stable actor identity.
3. staged, A0 B10: beginning snapshotHP1/1; both callbacks emit qualified intents from same snapshot; end commit gives0/0 and two damage/death records.
4. staged, A10 B0: actor-entry order reverses but normalized intents/events/finalstate matchcase3. Do not require emitted event ordering identical when contract only defines normalized content.

Use explicit phase nodes: snapshot at priority-100, actor callbacks0/10, commit/reporter at100. One coordinator owns HP/snapshot/pending intents and central commit; phase nodes call its begin/commit methods. These are *project phase boundaries expressed through actual callbacks*, not engine-provided atomic transaction. Prefer this over coordinator doing all actor work in one for-loop: real independent actor callback order remains observable in both policies. In immediate mode begin still records tick/initial state and commit only finalizes, so phase scaffold is comparable.

Separate snapshot eligibility from commit ordering. Each actor onlyqueues once, targetID/attackerID/actionID/tick explicit; no extraHP mutation after commit. Fully independent expected trace should contain phasebegin, the two actor entries (in actualpriority order), phasecommit, and normalized finalstate/events. Record Engine.get_physics_frames for each entry; all combatphase records must share one enginephysics frame. Record delta and actual configured priorities/group mode; don't use an invented Python tick as sole same-tick evidence.

Initial-dead boundaries already exist in Python supplement; four fresh processes above isolate actual scheduling increment. Do not claim new engine coverage of unexecuted boundary cases or bigger combat systems.

## Minimal stop / failure / evidence protocol

Parent creates/configures nodes before enabling their processing. During initialization keep physics disabled explicitly; set fixed priorities before enable. Commit callback sets completed and disables every phase/actor physics callback after both actor entries were observed. No node free/reparent, no midtick priority change, no queue_free ordering test. A later idle `_process` publishes exactly one complete RESULT_JSON and exits0; publishing must require completion, not rely on first idle frame containing physics. Extra callbacks after completion are error, no silent repeated attacks.

Add finite in-engine logical guard (unexpectedsecondcombatframe is failure) and external Python timeout with preserved partial stdout/stderr. Runner creates isolated HOME/XDG, uses existing `--headless --single-threaded-scene` flags; no timing/sleep ordering and no need multiple rendering rates. Fresh processes percase and controlled source/contract hashes. Reject nonzero exit, SCRIPT ERROR, unexpected stderr, missing/multiple result records, or trace mismatch. Clear summary before -O and any optional imports/spawn; preserve original failure even if later corrected. One independent repeat checks raw callback logs with literal expected membership, not only summary PASS.

Do not copy old fixed-step runner freshness weakness: its early-O rejection precedes cleanup; current evidence note explicitly warns about historical summary reuse. New runner should use strengthened cleanup order and capture startup/timeout failures without calling stale files current success.

## Installed identity caveat and stop rule

Read existing research/source-notes/godot-runtime-provenance.md. Prior installed binary selfreports4.6.3.stable.official.7d41c59c4/full7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3; public tag resolves35e80b3a… and prior selfreport commit lookup returned422. The previously measured installation fingerprint is omitted here; the original measurement was historical byte evidence, not a new measurement in this gate. New execution must hash actual binary and record selfreport again, never backfill old runs or authenticate official origin from string.

No collision solver, physical contacts, animation, device input, rollback/networking, concurrency, cross-platform determinism, fairness or performance proof. Deterministic callback order does not choose the game's simultaneous policy. Stop after four cases plus independent repeat and bounded runner checks; failure of assumed order is evidence to inspect, not reason to rewrite oracle silently. If actor callbacks are not actually dispatched independently, reject as redundant wrapper rather than publishing new engine evidence.

> 公开衍生说明：本次仅省略安装位置、安装指纹或执行记录标识，并调整现址/固定历史链接；技术观察、失败、计数与原有证据范围保留。正文中的“本次”及身份相等陈述均属于原记录时点，本轮未重新检验，未运行旧实验，原始摘要声明不改写为新字节。文中描述性记录别名不是可执行目录名。
