# Source gate — production manager: declared progress versus dependency-ready delivery

2026-10-31. Bounded triage within existing TASK-2026-0008; no new main task, article, publication, native test or repository edit. Parent supplied head6aa9a5b; coverage below was read from current local `gamelibrary-work`, not independently asserted as a newly fetched remote snapshot.

## Recommendation: select one production role

**制作管理 / Production Manager**, primary PROD, related QA/ENGINE/DESIGN/ART2D. Focus on cross-discipline dependency, scope and milestone handoff, not player-research moderation or universal executive producer authority. Producer, Production Director, Development Manager and Production Manager must remain organization-specific titles, not automatic aliases or one uniform hierarchy.

Read existing8 role profiles' catalog entries and role paths; no production-management profile exists. Read SOL-PROD-001(playtest intervention) and ROLE-QA-001: the former constrains what helped player completion proves, the latter distinguishes defects, risk evidence and release authority. The proposed role instead owns **making commitments, dependencies, scope changes and escalation intelligible across teams**. It should consume QA/UX findings rather than duplicate their methods or certify technical success.

TASK-2026-0008 still needs-research and explicitly remains incomplete. This is a candidate bounded contribution, not a completed global responsibility matrix.

## Original sources actually read

All accessed2026-10-31; English and Japanese discovery. Search phrases included `producer development director dependencies production interview game` and `プロジェクトマネージャー インタビュー 開発`. No aggregation summaries used as evidence.

### S1 — studio interview: production hierarchy and dependencies

[Ubisoft Toronto — People of Ubisoft Toronto: Meet Frank Roy, Production Director](https://toronto.ubisoft.com/people-of-ubisoft-toronto-meet-frank-roy-production-director/), **2023-08-31**, English, first-party studio interview.

Exact reading: introductory role question(lines31–35); *Career Development*(47–58); *Upcoming Projects*(63–66). Roy describes planning with a Lead Producer and decomposition with Associate Producers/Production Managers, multidisciplinary dependencies and expert support. The project passage discusses plans and approvals as work underway, not demonstrated delivery improvements.

Use: a concrete organizational sample separating planning/coordination from discipline expertise. Do not infer that the reporting structure is universal, that named tools are required, or that the stated intentions caused measurable success. No internal schedule or dependency artifact exposed.

### S2 — actual production experience, Japanese first-person account

[Bandai Namco Studios — 「テイルズ オブ アライズ – Beyond the Dawn」プロジェクトマネージャー/プロデューサー 押山 萌香](https://www.bandainamcostudios.com/creator-interviews/14742), Japanese, first-party interview. **Publication date not confirmed in inspected body**; search recency is not a substitute.

Exact reading: *所属と業務内容*(18–39); *印象的なエピソード*(42–67). Oshiyama recounts staged remote transition late in Tales of Arise versus building the Beyond the Dawn team remotely from inception, shared progress visibility and decisions tied to goals. The earlier training-project account explicitly says the initial year did not ship on Steam; do not rewrite the ambition as achieved release. A page notice says the exceptional remote-work measure has ended; historical practice is not current company policy.

Use: a concrete production-context case showing why transition readiness and common understanding cannot be assumed from identical process labels. Weekly screenshots and group discussion were described as communication practices, **not independent proof of integrated build readiness or measured productivity**. No comparative efficacy or internal QA results available.

### S3 — narrower current-readable employer responsibility sample

[Riot Games — Game Producer II, League of Legends (Contract), Singapore](https://www.riotgames.com/en/work-with-us/job/8163433/game-producer-ii-league-of-legends-contract-singapore), English. Body identifies Job Id6151 despite numeric URL8163433; retain both rather than invent a requisition mapping. **Publication date unconfirmed**; readability does not establish that recruitment remains open.

Exact reading: role description(lines14–18), *Responsibilities*(19–25), relevant qualifications(27–36). This role covers cosmetics delivery across Singapore/Los Angeles/external partners, scope and milestone alignment with discipline leads/Product/QA, and dependency/risk visibility.

Use: supports a bounded deliverable-intake and cross-team handoff responsibility. Not evidence that the employer's actual releases meet all stated goals or that the producer alone grants release acceptance. Specific tools/experience requirements are this sample, not general prerequisites.

## One actionable engineering question

**When a discipline or external partner reports “done,” what allows the receiving team to commit to the next integration step or milestone—and who decides scope/date changes when that dependency is not actually ready?**

Proposed future role contribution: an original, explicitly unexecuted **dependency handoff record**, not another playtest form:

- The promised outcome and intended receiver, attached to a concrete milestone/scope version.
- The producer's status assertion versus the receiver's needed artifact, interface/configuration assumptions and evidence location.
- Known missing inputs or integration work, each with an owner; no completion percentage invented to hide them.
- Date confidence/constraints and change impact on other disciplines; ambiguity escalated to the actual decision owner rather than silently absorbed.
- Explicit choice after a failed dependency: rework, sequence change, scope reduction or revised date, with acceptance responsibility retained by the relevant technical/product/release roles.

This is proposed synthesis, not a schema attributed to Ubisoft/BNS/Riot. “Done” labels, screenshots and schedule updates can communicate progress without demonstrating integration or final quality. Conversely, incomplete integration does not erase completed upstream work; it changes what downstream commitment is justified.

## Decision enabled, and why this is not duplicate QA

The artifact would help a production manager decide whether to preserve a downstream commitment, expose a dependency risk or seek a scoped change decision. Engineers provide technical readiness evidence; QA characterizes defects/coverage; user researchers characterize experience evidence; production coordinates their consequences for commitments. The production role cannot turn a meeting decision into passed tests or resolve expert disagreement by rewriting evidence.

Failure boundary: **reported local completion ≠ receiving team's usable input ≠ milestone acceptance**. Existing playtest article concerns inference under moderator intervention; this new boundary concerns work transfer and authority across disciplines even when no player test occurs. Existing build role identifies artifacts; production still needs to know which dependency and commitment those artifacts satisfy.

## Gaps and stopping condition

Gate **passes for one source-backed role draft if selected by parent**. Three firsthand samples support role variation; BNS provides a named project experience rather than only recruitment language. No further generic source roundup is needed for this triage.

Unresolved: actual internal schedules, acceptance templates, delivery metrics, resource/capacity allocation data, change-control policy, escalation authority, outcomes caused by remote-work practices, or comparison of management methods. Do not infer universal Scrum/RACI/Jira requirements, claim a quantitative efficiency gain, or treat management pressure as authority to bypass technical quality or worker wellbeing. No invented toy scheduling benchmark is warranted. A future role should keep one concrete handoff worksheet and clearly label it unexecuted, not expand into general management doctrine.

User-researcher was not selected: current strongest retrieved original samples support production management, and this choice avoids rephrasing existing QA/moderator material. This is prioritization judgment, not a claim that user research is fully covered or lower value globally.

## Local coverage fingerprints

- CATALOG.md: `837e48cfe251674325d3d69321bf9af4360e727c4665620add1257e9e1f6f7f1`
- SOL-PROD-001: `fd1e1b424fb2bdd6c42721855ab33f8f8e32f7b523bb1000367bf19eb7f65e3f`
- ROLE-QA-001: `22cf310097fc68886d2336e9089b8cd712c2c25b593434e0ef15ed8e5a7795e2`

No main-worktree, queue, taxonomy or remote changes made.
