# Reliable-channel note — final editorial review

2026-11-01 UTC. **ACCEPT with two wording-only refinements.** Entire standalone note read against the independently reviewed upstream source and Godot documentation.

- Original note SHA256: `55a4ef12cfaf8b41de4250332c01dd45062f6e2a08f48297ce162895949b016f`.
- Accepted note SHA256: `3307c0123ddba6fa0e23a6b5e7ae96f3d1700177938b346ffb800a08f1b00ce3`.

Changed “退休规则” to “失效清理规则” and “已退休” to “已失效” for clearer Chinese lifecycle terminology. No technical premise, source claim or proposed behavior changed.

## Acceptance scope

The two hypothetical messages target an existing dispatcher, not an unavailable entity RPC node. The delayed-A/no-gap-B ordering is explicitly assumed and permitted by independent sequencing, not an observed reorder or mandatory network outcome. The possibility of identifier reuse is separated from initial readiness failure.

Same-channel delivery is not equated with completion of asynchronous creation. Transport acknowledgements and application milestones remain distinct; a prior Ready does not guarantee continuing readiness. The proposed admission choices preserve capacity, expiry and lifecycle checks without promising eventual completion. Generation identity does not establish sender authorization.

Channel independence is expressly not independent bandwidth, congestion resources or a latency guarantee. Upstream ENet source identity is not transferred to Godot's modified implementation. Source locators and the selected documentation scope agree with the prior review.

The note adds a precise ordering/readiness distinction, rather than another generic networking caveat. Its record fields and intervention table are original unimplemented suggestions, not upstream protocol fields. Existing prediction and RPC evidence remains unchanged and does not become cross-channel evidence.

No further correction required. No engine, packets, model, native execution, existing-article edit or remote write performed.
