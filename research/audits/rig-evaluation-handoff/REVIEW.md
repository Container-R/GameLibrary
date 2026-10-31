# Rig evaluation handoff independent source review

2026-10-31 21:17 UTC. Reviewed draft section SHA256 `5f3dc3c0a1464d3182ad81286475986ac2c7836c1d7967fbf97dcf6acf4e6fb8` and source note `6a6137cb5af50ba35d2abb10ec9a0f99891614fa8097986cf1a6385cac78a937`. No runtime execution.

Independently opened all three originals:
- Square Enix CEDEC2015 PDF, https://www.jp.square-enix.com/tech/library/pdf/CEDEC2015_Luminous_FFXV_Animation.pdf . Text layer confirms title/authors/date on physical page 1 and cited physical pages 23, 27–29, 32, 40–43, 45. These support animator-facing tools, ordering burden, TA presets and project-specific role/workflow discussion. No inference from unread diagram colors or video.
- Unity Animation Rigging 1.2.1, https://docs.unity3d.com/Packages/com.unity.animation.rigging@1.2/manual/RiggingWorkflow.html . Metadata identifies 1.2.1; generator date is not release date. Rig Component paragraphs explicitly connect hierarchy traversal to ordered animation jobs after normal Animator evaluation. This is bounded package documentation, not a whole-engine lifecycle or evidence that FFXV used Unity.
- Capcom employer page https://hrmos.co/pages/capcom/jobs/01_03_040 . Job duties support the limited rig/IK/script role example, not global title aliases, current hiring guarantees or universal organization.

The dependency table and six-row worksheet are explicitly original/unexecuted. The torso-aim/hand-IK counterfactual is physically plausible under its stated parent-chain assumptions and correctly refuses to guarantee either order. Target spaces, moving grip points, reachability and artistic priorities prevent a universal order conclusion. Existing Godot root-motion evidence is not repurposed as Unity evidence.

One narrow correction requested before final acceptance: in the hierarchy-change worksheet row, record/preserve world-space control/target poses and bone/target references. Reparenting can change spatial inputs even without editing numeric parameters; otherwise an observed change could be misattributed to job order. This is an isolation-of-variables requirement, not a demand for new runtime work.

## Correction closure

At 21:17 UTC re-read corrected hierarchy row: it now preserves/checks world poses and bone/target references and records spatial inputs alongside collection order, explicitly forbidding attribution of reparent-induced spatial change solely to evaluation order. Accepted final section SHA256 `67161c4148640da2eaf055c16f2f88ed64f9d59f5bf036243e875198afd42cf1`; source note unchanged. No new runtime evidence implied.

## Material review correction — 21:18 UTC

Main integration review found a scope error missed above: the existing turn-in-place article does **not** archive a Godot root-motion experiment. Independently read `gamelibrary-publish-gltf/solutions/animation/turn-in-place-foot-sliding.md` and `research/experiments/root-motion/README.md` now: evidence is four Python 2D rigid-transform model tests, explicitly excluding skeletons, solvers, engine callbacks and real character assets. Its engine verification matrix remains unexecuted. Unrelated Godot animation-event evidence must not be substituted.

The earlier review's acceptance of the draft's Godot characterization was incorrect; primary-source checking did not establish repository baseline scope. Prior acceptance is superseded pending corrected article/source-note/gate wording. This correction does not invalidate the independently checked Japanese/Unity source claims or require runtime execution.

## Corrected draft acceptance — 21:19 UTC

Re-read corrected section SHA256 `34f0b88ca9691ced655eee1693df6aaaac28f4b8a2b81e5f006672d7966ecdb5` and source note `7223dde52e6a4a207f45910d5d36337a3661497b809943b79e53f0232795be72` against the actual existing article/fixture README. Both now accurately name four Python 2D tests and exclude bones, IK solvers and engine callbacks. Unrelated Godot animation events are explicitly not root-motion evidence. Accepted these corrected files; earlier hashes/acceptance are historical and superseded.

Also accepted added original A/B controls for collected constraint IDs/membership, Rig-layer assignment, enable states, weights, references and actual ordered list. Membership/settings differences prevent order-only attribution, complementing the spatial-input control. These are proposals, not executed Unity behavior. No new runtime occurred. Corrected discovery gate path awaited separately; not yet reviewed.

At 21:19 UTC read corrected discovery gate `research-drafts/role-handoff-depth-gate/gate.md`, SHA256 `583600a88c2f716d396aaf06b8e50524ad2f21e502cb83fd5af547ebbd1f72d6`. Root-motion scope is corrected there too, with explicit 21:18 correction history. Gate remains prospective source-depth work, not an executed rig experiment. This closes the previously pending gate scope check.
