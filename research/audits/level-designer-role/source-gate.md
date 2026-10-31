# Source gate: level designer responsibility and delivery contracts

2026-10-31. Local proposal only; no role article, taxonomy change, engine run or remote publication yet.

## Proposed scope / classification

Candidate title: **关卡策划：从遭遇意图与白盒到可验收的空间交接**.
Proposed path `roles/design/level-designer.md`, proposed ID `ROLE-DESIGN-001` (writer must recheck uniqueness before use). Primary discipline `DESIGN`; related existing IDs `PROG, AI, TA, MODEL, UX, QA, PROD, NARR`. Do not invent a LEVEL discipline.

Read research skill ROLE.md and 01-taxonomy-and-roles.md. Current taxonomy/disciplines.json already lists `关卡策划` under DESIGN as a candidate; it is not an existing completed profile. Current related_roles already uses `level-designer` (e.g. SOL-PROD-001). No established alias registry was found under taxonomy; do not declare level artist, technical level designer, mission designer, encounter designer or all Japanese planner titles synonyms. Here the Japanese source explicitly says レベルデザイナー and describes concrete spatial/event work.

Question: what must a level designer hand off so that “the encounter is intended to work” can be distinguished from “the current geometry, locomotion, navigation and art revision actually support it,” without treating a path query or one assisted completion as proof of experience quality?

## Read primary sources

All URLs below accessed 2026-10-31. Source dates are publication labels where available, not search crawl dates. None is evidence that hiring remains open; no salaries, application contacts or employment availability are used.

### L1 — ORCA, レベルデザイナー (Japanese studio original)

https://www.orca-inc.co.jp/wp/recruit/career/career_level_designer/

Date not displayed. Read heading, 業務内容, necessary/desired skills and 目指す方向・意欲; web text lines17–41. Studio-domain original, not a translation/recruiting aggregator. Supports concrete UE enemy/item placement, map planning/specification writing, and event design/implementation. Useful contrast with a lead-heavy western posting: individual spatial content and event work are explicit. Does not establish a universal planner title, navigation-system implementation ownership, or all studios' responsibility split.

### L2 — Ubisoft Annecy, Lead Level Design (F/M/NB) [AAA Project]

https://jobs.smartrecruiters.com/Ubisoft2/744000140062699

Employer-authored posting on its SmartRecruiters page; date not displayed. Read Job Description, Responsibilities and Qualifications, especially lines19–25,46–85. Supports alignment of gameplay intent, Level Art and Tech Level Design; collaboration with programming, TA, QA and production; spatial cues, progression, pacing, prototypes and technical/performance constraints. This is one **lead/AAA World-team** organization, not a template for every individual level designer or proof all small teams differ. Its reporting line and management duties stay source-specific.

### L3 — Double Fine / Devin Kelly-Sneed, Behind the Code: Designing Raz's Jump

https://www.doublefine.com/news/devin-article-raz-jump

Published **2024-04-23**. First-party shipped-game account by Player Movement and Powers Feature Lead. Read text, especially Metrics (lines70–73), Jump Metrics Tool (90–93), and project/cross-discipline context (8–10). Supports an unusually concrete interface: codified movement measurements enable layout; later changes can invalidate old level assumptions; their editor preview used jump simulation and reflected tuning changes. This is a Psychonauts 2 case, not universal engine behavior. No embedded video watched, runtime executed, or target game's numeric tuning recommended. This source is sufficient to ground a movement-version/layout compatibility contract without claiming designers own movement code.

### L4 — Ubisoft Toronto NEXT 2024–2025 Level Design Brief (historical challenge)

https://static-wordpressv2.ubisoft.com/toronto.ubisoft.com/wp-content/uploads/2024/09/Ubisoft-Toronto-NEXT-2024-2025-Level-Design-Brief.pdf

Six-page primary PDF; read extracted text, particularly **p2** mission document/playable blockout stages and **p4** document evaluation criteria (one-based PDF pages). Identifies historical 2024–2025 program; no separate publication timestamp confirmed. Supports a concrete public example of annotated top-down map, clear design intent, modular/adaptable construction, and meaningful player approaches. Explicitly **challenge criteria**, not disclosed production acceptance procedure; Phase II detailed package was separately supplied and has not been read. Do not copy its score weights into a universal production rubric.

## Discovery leads excluded from accepted evidence

- Gameloft Paris Senior Level Designer, official https://www.gameloft.com/jobs/Senior%20Level%20Designer-744000136734759 : search snippet included rich duties but the opened official page did not expose them. Official Apply link led to https://jobs.smartrecruiters.com/Gameloft/744000136734759-senior-level-designer?oga=true (cache miss); clean URL also failed. **Do not use snippet duties as read evidence.** Two independent employers ORCA/Ubisoft plus Double Fine case suffice without retries or an aggregator fallback.
- The Level Design Book blockout/metrics text was read at https://book.leveldesignbook.com/process/blockout and https://book.leveldesignbook.com/process/blockout/metrics . It led to the first-party Double Fine source. Homepage identifies work-in-progress and CC BY-NC-SA licensing; /about failed. Do not import diagrams, tables or translated prose into this repository. Proposed profile can rely on accepted first-party sources above and original synthesis; numeric dimension tables are not needed. The book's general advice is not a substitute for project-specific locomotion measurements.

## Original reusable deliverable matrix to develop (not source-prescribed process)

1. **Encounter intent → testable brief:** target decisions, prerequisites, intended alternatives, failure/recovery, expected information; separate design hypothesis from verified observation.
2. **Brief → blockout package:** annotated route/encounter map plus playable revision, placement/event dependencies and deliberate omissions. A prettier screenshot is not the acceptance criterion.
3. **Movement/navigation interface:** movement-config/build identity, actor capabilities, geometry/collision revision, navigation availability and intended endpoints; shared LD/programming/AI responsibility. Distinguish player route legibility, collision traversal, NPC path availability and actual path-follow completion.
4. **Playtest → decision evidence:** question, target experience, build, observed actions, assistance/interruption flags, alternative explanations and proposed revision. Keep library playtest article's intervention boundary; do not invent sessions or outcomes.
5. **Art handoff → preserved interaction:** gameplay-critical volumes, sightlines/cues, traversable gaps and clearance, collision/navigation dependencies, allowable art freedom, revision review and regression list. Original suggestions, not claimed studio internal documents.
6. **Change → acceptance packet:** movement/art/layout change triggers targeted recheck, owner and unresolved risks; QA repro/functional evidence and player-experience evidence remain distinct, even if same staff performs both.

Acceptance should be project-scoped and inspectable: exact build/config, concrete intended route/interaction, observed outcome and limits. No universal corridor widths, completion percentages, fun score or claim of proven workflow improvement. An illustrative small route/encounter change could show a widened jump range invalidating a formerly gated path; label it hypothetical, not an executed reproduction. Avoid spawning a new engine fixture for this role profile.

## Existing article links and boundaries

- `solutions/production/playtest-intervention-evidence.md` (SOL-PROD-001): already read original synthesis; includes Valve and GDS sources and separates assisted completion from unassisted discovery. Link rather than duplicate study-method article; its role handoff paragraph is an original recommendation, not employer fact.
- `solutions/ai/navigation-readiness-and-partial-path.md` (SOL-AI-001), linked `research/experiments/godot-navigation-sync/`: dependency/readiness/partial-path states; not proof of good encounter geometry or designer-only ownership. Preserve existing provenance limitations and do not imply a new engine run.
- `roles/programming/gameplay-programmer.md` (ROLE-PROG-001): movement/state/interaction implementation partnership.
- `roles/technical-art/technical-artist.md` (ROLE-TA-001): asset/tool/performance integration partnership, not substitute for level/environment artist.
- `roles/qa/game-quality-assurance.md` (ROLE-QA-001): reproducible functional failures and version risk versus experience observations; not all job-title aliases.

## Gate decision

**Adequate to proceed to one bounded source-backed role profile**, subject to parent acceptance: two independent employers, a useful Japanese original, a specific shipped production account and public annotated-design/blockout criteria. Not adequate to claim universal team structures or real adoption/outcomes. The proposed contract matrix would add actionable cross-disciplinary acceptance work, rather than just copying hiring descriptions. No aliases/taxonomy need change beyond an eventual evidenced DESIGN profile and normal authored links.
