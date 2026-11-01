# Unreal Notify eligibility — independent source review

2026-11-01 UTC. **ACCEPT for a narrow source-only supplement**, retaining the scenario qualification below. Gate SHA256 `a65a80af55e5e5a4c12f056be9762a5fef59fb25e2ed136e767f11c2db878725`.

## Exact originals reopened

All three originals returned Unreal Engine / Unreal Python **5.6** titles with the selected version parameter. No publication date, patch identity or immutable implementation commit is established.

- [Animation Notifies manual](https://dev.epicgames.com/documentation/en-us/unreal-engine/animation-notifies-in-unreal-engine?application_version=5.6): Montage Notify/Window (169–174), weight (194), and Common Notify Properties (203–217). These support configurable eligibility and the Queued/Branching Point timing distinction. The manual explicitly describes gameplay-altering uses; a blanket prohibition on Notify-driven gameplay would contradict its scope. The named Montage Blueprint callback route has a specific playback-node requirement, not a rule for every custom Notify.
- [AnimNotifyEvent generated API](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/AnimNotifyEvent?application_version=5.6): dedicated-server property (33,115–118), filtering/chance/follower properties (22–35). Disabled server triggering is explicitly documented as skipping that Notify on dedicated servers. The page is Experimental generated API documentation with an AnimTypes.h locator, not implementation source inspected. Constructor defaults are not evidence of editor/project defaults.
- [Networking Overview](https://dev.epicgames.com/documentation/en-us/unreal-engine/networking-overview-for-unreal-engine?application_version=5.6): client/server architecture and separate-world example (17–59). This supports separating an authoritative decision from client presentation and explicitly implemented replication. It does not supply a Notify-specific authority bridge or exactly-once guarantee.

## Scenario precision and useful scope

The proposed mismatch is defensible **if the required hook must execute locally on the dedicated server and no other request path supplies that decision**. Make that condition explicit in the eventual example. Merely deciding hits on the server does not imply that every initiating callback must run there: a project could intentionally submit a validated client-origin request through a separate network path. The disabled flag alone cannot establish a lost hit in that different architecture.

Given the stated sole server-local hook, client preview execution cannot demonstrate eligibility of that hook on the server. Enabling the flag only removes this documented exclusion; it does not establish animation evaluation, remaining filters, collision validity, authority ownership, replication or duplicate handling.

Queued versus Branching Point concerns timing/order in the documented context. It supplies neither evidence of filter bypass nor automatic authority, and the prose should not reinterpret “asynchronous” as a proven worker-thread contract. Filter precedence, dispatch internals and interruption behavior remain uninspected.

The contribution is a concrete authored-eligibility/required-execution-location check, not another seek/advance example. Existing Godot method-track, root-motion and policy evidence cannot validate these UE mechanisms. No UE invocation, model, source implementation inspection, images, video or experiments performed. Keep the supplement compact and do not turn the documented scenario into a measured engine defect.
