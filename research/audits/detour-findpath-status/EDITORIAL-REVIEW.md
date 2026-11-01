# Editorial review: Detour path status and output capacity

2026-11-01. Accepted unchanged.

Reviewed the complete proposed `research/source-notes/detour-findpath-status-and-capacity.md`, SHA-256 `45879f3e02bb725307e2698240707a7a583ca655944394ea9badc369b5431f14`, together with SOURCE-REVIEW and MAIN-SOURCE-READ. Independently reopened the fixed [result assembly and extraction code](https://github.com/recastnavigation/recastnavigation/blob/6dc1667f580357e8a2154c28b7867bea7e8ad3a7/Detour/Source/DetourNavMeshQuery.cpp#L1147-L1204); remaining interface/status premises were checked against the separately recorded direct-source reviews.

The three-node counterexample is sound under its explicit assumptions. A length-three parent chain is backed up once before a capacity-two write, so the retained prefix is A,B rather than B,C. Given that search found C and did not exhaust nodes, the assembled status carries output truncation without the partial-search flag. This is a symbolic control-flow trace, not a query result from a real mesh.

The proposed acceptance expression uses the detail mask as an any-bit test and checks both success/failure state and the actual last returned reference. Its refusal of all three degradation indicators is clearly a conservative caller policy, not an API obligation or claim that every flagged result is unusable. Search resources and output storage have different recovery decisions; the written count is not promoted into the complete required size.

Initialization requires the documented positive bounded node capacity as well as success. The supplied positions must belong to their respective valid polygons, and output allocation must match the stated capacity. Those premises are not claimed to be proven by the proposed status check. Query/data lifetime and concurrent mutation limits are explicit. Acceptance does not certify physical arrival, straight-path output, arbitrary costs or optimality.

The existing-article link `../../solutions/ai/navigation-readiness-and-partial-path.md` resolves correctly from the intended public source-note directory, and that destination exists. Its runtime records were not opened or inherited. The complete new note contains neutral technical prose, public source identities and hypothetical labels, not private execution identifiers or host-specific runtime metadata.

No compilation, Detour call, mesh creation, model execution, private archive read or staged/remote edit occurred. Source derivation is compact and the policy is explicitly original. No correction requested; acceptance is limited to this exact note and the selected synchronous-query mechanism.
