# Coverage audit: choose a missing handoff, not another empty directory

2026-10-31. Read-only inspection of `gamelibrary-publish-texture/taxonomy/disciplines.json`, CATALOG and article frontmatter. No article drafted, implementation executed or main/remote state changed. Counts describe this local release snapshot, not an independent remote-publication verification.

## Actual authored coverage

CATALOG contains **19 source-backed articles: 5 roles + 14 solutions**. All remain source-backed; attached real experiments do not upgrade entire articles to universal validation.

| Primary discipline | Articles |
|---|---:|
| PROG | 2 (gameplay role, fixed-step solution) |
| SFX | 2 (interactive-audio role, music-state solution) |
| DESIGN | 2 (level role, economy solution) |
| TA, QA | 1 role each |
| A11Y, AI, ANIM, ENGINE, LOC, PLATFORM, PROD, NET, GFX, UX, VFX | 1 solution each |

Thus 16 primary disciplines are represented. Taxonomy has 24 entries, of which ACCESS is explicitly a legacy umbrella: use 23 nonlegacy entries as the denominator if one is needed, not a misleading 24-target checklist. **ART2D, MODEL, MUSIC, NARR, DATA, LIVE, BIZ** have no primary article. This is not equivalent to no research: the Steam capsule source note is BIZ-related but outside the roles/solutions CATALOG; pinned ink source audit already exists; music appears within SFX and multiple cross-disciplinary tags.

Five authored role profiles are gameplay programmer, technical artist, interactive audio designer, game QA and level designer. Other taxonomy specializations remain candidate scaffolding, not completed occupational research. Lack of a separate composer or environment artist profile is not by itself the highest-value next task.

Related-discipline tag occurrences (not coverage quality scores): PROG12, NET1, ENGINE6, TA5, ART2D0, MODEL3, ANIM3, VFX0, GFX2, SFX2, MUSIC2, DESIGN5, NARR2, UX7, QA15, DATA2, LIVE0, PROD4, PLATFORM3, BIZ0, AI1, A11Y2, LOC1. Tags can locate interfaces but do not prove that their associated responsibilities have been explained or tested.

## Three concrete undercovered handoffs

### 1. MODEL → TA/ENGINE: does mesh data remain the intended geometry after attribute extraction?

**Unmet question:** an exported/interleaved mesh buffer can be large enough and parseable while an importer reads the wrong vertex positions by ignoring accessor-relative offsets or treating stride as element size. What minimal acceptance distinguishes valid bytes, attribute identity and intended topology?

Current asset-import article covers preserving import intent/configuration; texture article covers block layout and CPU decode. Neither provides mesh vertex/attribute handoff evidence. This candidate must target **recovered vertex values and index topology**, not repeat another generic byte-budget calculator.

Primary source read: Khronos glTF2 specification source, https://github.com/KhronosGroup/glTF/blob/main/specification/2.0/Specification.adoc , accessed2026-10-31; sections3.6.2 Buffer Views and3.6.3 Accessors. It defines buffer-view spans, vertex stride and accessor offset/count/type; multiple attributes sharing a view require stride. The official registry HTML timed out; reading Khronos's own GitHub source was a normal public alternative. Current main is mutable: pin commit and relevant file hashes before implementation/publication. No vendor-importer behavior or render result follows from this source alone.

**Feasible new evidence:** create an original two-triangle indexed mesh with interleaved POSITION and NORMAL float32 fields, nonzero buffer-view offset and accessor offset; standard-library struct packing/unpacking and JSON only. Use distinct, non-symmetric vertex values so a plausible wrong extraction is visible; compare to an independent literal vertex/index oracle. A naive tight-packed read should give wrong values while staying within the byte buffer. A corrected limited reader should recover intended positions and topology and reject selected declared-view overrun/stride mistakes. Preserve immutable synthetic binary as base64 and exact digest.

**Limits:** this is a deliberately restricted glTF attribute/mesh contract, not a general safe parser or official validator; no GPU rendering, DCC export, real engine import, skinning, animation, sparse accessors, matrices, normalization, external URIs or compressed extensions. An in-bounds wrong field is not automatically malformed glTF—distinguish a valid asset interpreted incorrectly from an invalid fixture. Current Python standard library is sufficient; no packages/credentials/downloaded code required.

### 2. NARR → gameplay/save: which story checkpoint and world-side effect belong together?

**Unmet question:** saving a narrative engine's internal state and recording a host-world reward are separate operations. Can a resumed story advance with a missing reward, or repeat an external action after restoring a different checkpoint?

Existing pinned ink audit supplies source depth but no authored role/solution for this integration. Economy ledger and cloud save already cover adjacent idempotency and publication boundaries, so a new unit must add binding/evaluation and content identity rather than restate those articles.

Primary text reopened: https://github.com/inkle/ink/blob/35c63e52f1d36060930dc7ed3cfba38ea224b528/Documentation/RunningYourInk.md , Saving and loading; Actions v.s. Pure functions. It exposes story-state JSON and explains action/pure callback distinction. Existing pinned runtime audit records the General binding default exception; do not copy the guide's convenience-binding default onto every API. No host+story atomicity guarantee was found in these sections. That absence is a bounded inspected-source observation, not a universal claim about every integration.

**Possible evidence:** an original host-state/receipt checkpoint model can show split commits, but would not validate actual ink callback behavior. No installed C# runtime was available at prior gate, and it has not been rechecked here. Without actual runtime or a richer source-only unresolved question, another synthetic ledger risks duplicate value. Defer behind the mesh handoff, preserving these leads.

### 3. DATA → design/production: what does a level-completion event actually establish?

**Unmet question:** a gameplay completion event, a recorded assistance flag, a session attempt and a human participant are different units. Can the report denominator and intervention context be reconstructed rather than inferred from raw event row count?

Current playtest article explains observation contamination, but no DATA solution explains schema-level handoff from gameplay instrumentation to an interpretable report. This is not a request to collect user telemetry or infer retention/monetization success.

Primary overview read: Microsoft PlayStream Overview, https://learn.microsoft.com/en-us/xbox/playfab/data-analytics/ingest-data/playstream-overview , updated2023-11-01, accessed2026-10-31. It supports that developers define custom events to track game/player behavior. It **does not establish delivery ordering, retries, unique-event semantics or correct denominators**. The visible public body was readable despite a generic authorization banner; no login was attempted.

**Possible evidence:** local synthetic event histories with multiple attempts, declared assistance, missing end event and repeated rows, comparing event-count and explicitly scoped attempt-count reports. No actual player outcomes. Further primary schema/transport documentation is required before claiming any specific provider duplicates or reorders events. This candidate's source gate is weaker than the mesh question; do not manufacture provider guarantees from a marketing overview.

## Recommendation: ONE next problem

Choose **MODEL-primary mesh attribute handoff: “有效二进制不等于正确顶点：glTF交错属性的偏移、步长与几何验收”**, related TA/ENGINE/GFX/QA. It adds a missing content-production interface, uses authoritative accessible specification sections, and admits a small falsifiable artifact experiment with no new install or credentials.

Before coding: pin Khronos source; read accessor alignment/bounds and mesh-index requirements as well as JSON schema; freeze a supported subset. Proposed invariant: extracted POSITION and index sequence equal independently declared geometry under that subset, and each referenced element lies within its declared buffer view—not merely the overall buffer. Proposed adversarial contrast: wrong tight-packed read remains in bounds but returns other interleaved data; strict reader rejects a shortened view even when backing buffer still has bytes. These are different failures and should not be merged into one “corrupt file” label.

Bounded stopping condition: one original indexed interleaved artifact, one correct extraction, one observable naive semantic misread, and a small declared set of negative layout cases with independent literal expected values/hashes. No rendering claim, general parser project, role dossier or extra format breadth. If sources reveal that this specific artifact setup is invalid, revise the proposal before execution and preserve the reason; do not adjust the oracle after seeing desired output. Source review and independent acceptance precede any new article decision.

## Evidence update — final recommendation supersedes earlier ranking

At18:41 UTC the integrator supplied stronger DATA primary leads. Independently opened them before revising this decision:

- Unity, https://docs.unity.com/en-us/analytics/rest-api/record-event-rest-api , Important fields: eventUUID is optional and documented to prevent accidental duplicate insertion; omitted eventTimestamp is inferred from receipt time. Session identity and ghost events are distinguished. These are that provider's documented interface statements, not measured service delivery, global exactly-once semantics or stable cross-provider promises. No request submitted; legal/privacy sections are not the topic and no compliance advice is inferred.
- GameAnalytics, https://docs.gameanalytics.com/events-metrics-and-filtering/metrics/ : distinguishes started sessions, ended sessions, per-session and per-user playtime populations. This supports denominator specificity, not a generic completion formula.
- GameAnalytics, https://docs.gameanalytics.com/event-tracking-and-integrations/sdks-and-collection-api/api/event-types/ : session-end section explicitly discusses closure before end processing and later recovery. Missing end can reflect instrumentation/lifecycle, not necessarily player failure. This does not establish that every missing attempt-completion event has that cause.

All read2026-10-31, rolling docs; no authoritative publication date confirmed here. The new sources close the earlier DATA source-depth weakness. **Final recommendation: prioritize DATA attempt-completion evidence over MODEL for the immediate next unit.** This is a source-driven revision, not a claim that the original PlayStream overview was sufficient. Mesh remains a ready second candidate, but another binary-layout unit immediately after texture is less diverse than a new reporting-evidence boundary.

Narrow question: **“关卡完成率：重试事件、重复尝试与未知结果不能共用一个分母”**. Original local synthetic records only; stable event identity separate from attempt identity and fictional actor identity, declared analysis cutoff, no missing completion silently labeled failure. Preserve orphan outcomes, conflicting repeated IDs, unfinished attempts and assisted completions as distinct report categories. Compare (a) raw completion rows/start rows, (b) deduplicated completed attempts/eligible started attempts, (c) fictional actors with a completed attempt/actors with eligible starts; show why these answer different questions. If completion context is missing, leave context unknown rather than infer unassisted success. A synthetic explicitly defined same-ID/same-payload retry can collapse; same-ID/different-payload must surface a conflict, not arbitrary first/last-wins.

Use a finite CSV/JSON fixture and standard-library Python or SQLite query, plus an independent hand-enumerated oracle. Verify event-order permutation invariance only for the declared complete batch and conflict policy; do not claim live streaming order independence. Late arrivals require a new as-of report, not rewriting the prior observation as if it had been known. Avoid retention/UTC DayN scope creep: those are separate metric definitions, not needed to solve this question.

Stop after one fixed synthetic cohort, explicitly named report denominators, bounded retry/conflict/orphan/unresolved/assistance cases and an independent result comparison. No SDK, account, real player collection, backend performance, vendor transport execution, privacy/legal conclusion or behavioral outcome. This extends existing playtest evidence and economy cohort reasoning without pretending it is another real-user study.

## Integrator sequencing decision — 18:42 UTC

The MODEL source/fixture unit had already begun from the initial recommendation when the stronger DATA recommendation arrived. Complete that bounded active handoff rather than duplicate or abandon its source work; retain DATA as the next candidate with its newly strengthened source gate. This is a sequencing decision, not a factual claim that MODEL objectively outranks DATA. Integrator separately pinned and read the Khronos source at59ecbdba704206bb656965ab4e202881806066f1 before continuing. No new article was published merely to improve coverage counts.

## Coordinator execution decision

At18:45 UTC the coordinator confirmed MODEL source/fixture work had already begun from the initial recommendation and its source was independently pinned. Complete that active coherent unit rather than discard it mid-validation. DATA remains the next candidate supported by the updated gate. This sequencing is a coordination decision, not an evidence claim that MODEL objectively outranks DATA.
