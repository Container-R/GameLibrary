# TASK131 independent source-contract review

2026-11-01. Status: gate accepted for drafting; final note not yet available. This is an independent, source-only adversarial review, not an implementation test or release approval.

## Exact inputs

Local published-content baseline supplied as commit `0e6419f27550bb177b759f19b3f5db5e69905576`. The directory is not a Git checkout; this review independently hashed file bytes, not the directory's commit ancestry.

| Input | SHA-256 | Reviewed scope |
|---|---|---|
| `research-drafts/existing-depth-selection-19/gate.md` | `ff3c8534edf7f883490c6511565954c9b405056c4ce434669ab3aae3dd18efb9` | Complete gate |
| `research/source-notes/nativearray-copy-and-disposal-ownership.md` | `fc070bebc24debcb35551ef3936ae2d26914e03b11d959292f7a2de971fea856` | Source-only note |
| `solutions/engine/addressables-content-update-baseline.md` | `971f27e4c38c6da3f3e3b83440349ed161debbd635f508f21ff208119acc6092` | §4.1 |
| `research/source-notes/fmod-event-bank-teardown.md` | `42cbdf6cb4a30cf312db01f0937195ec8969370b6451da6cb0d44424464f0080` | Source-only note |
| `solutions/audio/music-state-transition-contract.md` | `0fb9f95ae8070e74c803275dec6b54ca46ab4f0efd297cf680439f54ce4294cb` | Source-only scene-exit passage; no model result used |
| `solutions/rendering/presentation-queue-latency-boundary.md` | `00e190d5737b3533a7996775f78b14439319f42aaed112f748ac189e30eb5023` | §1.1 |

## Independent checks and adversarial findings

1. **NativeArray — reject reference-count substitution.** Independently inspected official [fixed Unity source, lines 194–270 and 924–947](https://github.com/Unity-Technologies/UnityCsReference/blob/0d0e6a11923ed73f1e8481eb5a6b2e67fe5ddc09/Runtime/Export/NativeArray/NativeArray.cs#L194-L270) via GitHub fetch after web fetch failed. The owning allocation branch schedules the disposal job, clears this receiver and returns the new job handle. An adapter that forwards only the input dependency loses the release completion dependency. Equally, one that interprets a copied struct as an acquired owning reference invents an operation not present here. Restrict conclusions to the original Persistent-allocation scope; null/non-owning branches do not justify generalized disposal behavior.
2. **Addressables — reject object substitution.** Independently read [1.21.21 catalog documentation](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/LoadContentCatalogAsync.html), Load additional catalogs / Update catalogs. Operation-cache retention is distinct from catalog-cache/hash behavior. A router is useful only if it directs the reviewer to the application's owned load-operation reference, not a mythical catalog-unload action. Completion alone neither releases that ownership nor establishes new remote content. Copies of handle values must not silently become additional owned references.
3. **FMOD — reject sufficient-barrier substitution.** Independently read [EventInstance release and callback definitions](https://www.fmod.com/docs/2.04/api/studio-api-eventinstance.html#studio_eventinstance_release) and [Bank unload / unloadSampleData](https://www.fmod.com/docs/2.04/api/studio-api-bank.html#studio_bank_unload). Release requests instance disposal; DESTROYED is about-to-destroy, not an acoustic receipt. Bank unload can override sample retention and invalidates associated objects. Thus a project end-record must remain input to bank policy, not sufficient permission to unload every dependency. A route offering a universal shutdown barrier would fail this test even if its footnotes disclaim listening tests.
4. **Vulkan — reject context substitution.** Independently read [fixed Khronos guide](https://github.com/KhronosGroup/Vulkan-Guide/blob/82887e8444045655cc4578827e4183be9de593ff/chapters/swapchain_semaphore_reuse.adoc), solution discussion and pseudocode. The relevant proof is reacquisition of the same image plus acquire synchronization, not a frame-slot fence or index alone. Keep this an ordinary successful-cycle semaphore-reuse route. It supplies neither shutdown/recreation coverage nor proof of visible presentation. Do not require CPU waiting when the source permits the appropriate GPU wait.

These checks use primary sources directly, not prior author sign-offs. No SDK, driver, audio or engine was run. No linked run archive or historical model result was used. The Vulkan specification itself and native Unity scheduler implementation were not independently inspected in this review; no new stage-mask or scheduler claim is certified.

## Usefulness decision

Conditional accept: the gate changes an adapter review from “wait for done” into four distinct corrective actions. This is more useful than four summaries only if the final note preserves responsibility identity, evidence scope, explicit non-entailment, and a direct route to each exact source section. A shared vocabulary for review questions is acceptable; a shared completion Boolean or destruction algorithm is not.

Final-note review remains pending. In particular, inspect the final table and worked scenario for hidden conflation of allocation disposal, relinquishing one operation reference, application resource policy, and next semaphore reuse. Publication must not rely on this gate-only verdict.

## Final-note binding and verdict

Independently read the complete `research-drafts/resource-release-routing/note.md` after it became available. Exact SHA-256: `d70c0b4c26d9b4a5876a358a008fd15872c9016e6ebf57969cc885d1dcce8be5`.

**ACCEPT for source-only publication at this exact hash. No blocking technical finding.** This supersedes the pending final-note verdict above, not its scope limits.

Adversarial checks against the actual table and scenario:

- The NativeArray row preserves the returned disposal dependency rather than claiming that input lastUse or local receiver clearing proves deallocation. The closing paragraph explicitly preserves correctly registered existing jobs, avoiding an incorrect “all copied jobs immediately invalid” rule.
- The Addressables row asks about the application's operation reference and rejects completion-as-release, catalog unloading, cache clearing and remote freshness. The paragraph rejecting automatic ownership increments for every struct/handle prevents an easy cross-row reference-count misreading.
- The FMOD row's output is a bank-holding policy decision, not SDK destruction completion. It requires other users and policy in addition to the project record and expressly rejects callback-alone authorization. The reception-record section preserves instance/policy correlation and does not license later access through a stale SDK handle.
- The Vulkan row names normal continuous presentation, same-image acquire synchronization and actual image indexing. Shutdown/recreation and visible-display inferences are rejected in the row itself, not only in a trailing disclaimer. The shared scenario remains four independent integration examples rather than a cross-SDK shutdown session.
- The introductory allowance for a shared scheduling/message facade is appropriately conditional on typed responsibilities, evidence and actions. The note therefore rejects information loss, not abstractions in general. Its four review fields and four distinct remediation routes supply concrete additional utility beyond a fact summary.

Non-blocking navigation improvement: labels naming Addressables §4.1, Vulkan §1.1 and the FMOD exit passage currently link to full files. Exact stable section anchors would shorten the route, provided the publisher verifies generated anchor behavior. Full-file targets do exist in the inspected content baseline; this is not a broken-link finding.

This review does not approve any uninspected AUTHOR-NOTES contents, index edits, commit ancestry, remote publication or subsequent draft changes. The final-note evidence claim stays source-only and inherits the linked notes' version/allocation/path limits. It does not establish behavior under exceptions, cancellation, concurrency, driver execution, acoustic output or a new general destruction protocol.
