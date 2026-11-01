# Independent recursive focus protocol review

2026-10-31 23:41 UTC. Accepted protocol SHA256 `7e365c4fe586fb7487cc913842b256faed13ecd122f4ecb5177439e97a19564f` for implementation review, not execution. This separate review preserves the earlier SOURCE-REVIEW unchanged. Read the complete candidate and compared it with the independently read official docs/pinned source findings in that review. No code, engine/version invocation or capability command was executed.

## Acceptance

- Five live Control instances and direct ancestry isolate recursive inheritance from replacement identity. Actual local/effective modes, recursive settings, visibility/tree state, nonzero exact IDs and viewport owner are required; application modal ownership remains an explicit product label, not a native Window claim.
- The post-disable oracle belongs after setter return. Passive exit callbacks may observe intermediate cached eligibility and are explicitly diagnostic-only for that field. Owner loss and the Control exit are separate from Viewport's acquisition-only signal.
- The override setter-only row requires owner Default to remain unchanged, separating eligibility from acquisition. Only the subsequent deliberate grab produces the out-of-scope owner. The same Opener ID remains throughout.
- The finite memberships are coherent: Opener enter twice/exit once, Default enter once/exit once, three viewport gains Opener/Default/Opener. Parent disable and override enable alone produce no viewport gains. Transition markers constrain association without asserting unnecessary cross-signal order.
- Deferred final observation is not equated with a completed/rendered frame; the synchronous null owner is not a perceptual outcome. No navigation, device, native modal, accessibility or Unity result is implied.
- Exactly one version process and one behavior process are planned, with separately bounded deadlines and process-callback watchdog. First unexpected outcome stops; no timing/scene/oracle relaxation. Provenance, source/identity pins, minimal environment and bounded cleanup language remain scoped, not authentication or containment guarantees.

## Implementation acceptance points (not protocol amendments)

The implementation must supply actual parent IDs/paths or equivalent engine-derived ancestry and subtree-membership observations, not infer membership merely from role labels. Validate the final owner against the live LogicalModal ancestry as well as the Opener ID. Record actual signal argument identities and passive callback snapshots; emitted request names alone are not observations. Ensure each acquisition has clear before/after call markers so the stated callback transition boundaries can be checked. Preserve the distinction between configured single-threaded fixture behavior and a claim that the engine has no internal threads.

No material protocol correction requested. Native execution still requires review of the exact implementation and explicit coordinator authorization.
