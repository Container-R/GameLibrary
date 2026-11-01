# Independent controlled navigation-completion protocol review

2026-11-01 01:11 UTC. Accepted revised protocol SHA256 `7e5197e2368bb8be30c446b3a8ac1cc2274b781e77e2db8238a1788963d53dad` for implementation review only. Initial500f3a9f candidate preserved by author. No engine/version, native API, fixture code or test execution in this review.

Source review d8733bc5 establishes the comparison-source expectations, not installed runtime behavior. Two disjoint original XZ quads and distinct reachable/disconnected targets form a narrow useful contrast. Revised protocol explicitly sets/reads map UP(0,1,0). Initial driver callback1 performs first displacement only after both agents' initial geometry/state gates pass; this removes reconstruction ambiguity without adding a case.

Four declared updating getters execute in fixed order for each active agent before either parent moves. Their calls are not assumed cached or frame-guarded. Signal handlers only record and latch; they do not update navigation or move nodes. Target transition may precede finish state within a call, so callback records are not confused with the post-query snapshot. Passive path/index/reached/distance inspection is separated from updating getters.

Expected route endpoints, monotonic straight-segment path, target ownership, registered map/regions, no links and explicit configuration are pre-movement gates. Actual returned next positions drive bounded0.5 assignments, never invented waypoints or a teleport to the disconnected target. The fixed48-callback budget comfortably permits these finite distances, but is a watchdog rather than a timing/throughput claim. No equality-at-distance threshold is needed.

Final oracle distinguishes exact target/finish signal counts in the finite window, target-before-finish order for reachable control, no target signal for partial route, final reached/finished/reachable states and actual positive movement. Finish latches prevent subsequent parent assignments; no post-assignment updating query occurs in that frame. Final snapshots do not become eternal nonduplication guarantees.

One version query plus one behavior process, exact binary/helper pins, minimal isolated environment, fresh evidence, fail-closed diagnostics/source/raw checks and first-failure preservation remain separate from native authorization. No CharacterBody3D, collider, move_and_slide, physical arrival, mission effect, avoidance, dynamic topology or cross-build determinism is established by the prospective fixture. Installed binary/public comparison-source correspondence remains unauthenticated.

No material protocol blocker remains. Exact code and pure consumer tests must be reviewed before any separately authorized native attempt; a failed geometry or runtime gate does not authorize a parameter sweep.
