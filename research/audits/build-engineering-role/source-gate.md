# Next occupation source gate: build engineering and release-candidate handoff

2026-10-31 22:12 UTC. Discovery only; no role article, runtime, installation, repository-state or remote edits. Read actual canonical `gamelibrary-publish-physics-callback` taxonomy, CATALOG and roles; research Skill `references/01-taxonomy-and-roles.md` requires responsibility/deliverable/acceptance interfaces and a real public case, not merely job titles.

## Current coverage and classification

Six actual profiles, not a completed occupational matrix:
- ROLE-PROG-001 — roles/programming/gameplay-programmer.md
- ROLE-TA-001 — roles/technical-art/technical-artist.md
- ROLE-SFX-001 — roles/audio/interactive-audio-designer.md
- ROLE-QA-001 — roles/qa/game-quality-assurance.md
- ROLE-DESIGN-001 — roles/design/level-designer.md
- ROLE-GFX-001 — roles/rendering/graphics-programmer.md

Taxonomy revision `2026-10-31.2` explicitly includes ENGINE specialization **构建与部署工程**, work areas 编译流水线/自动构建. PLATFORM includes 发布自动化/包体与补丁/认证; LIVE includes 配置管理/稳定部署/事故响应; PROD concerns scheduling/dependencies/milestones. Recommend primary ENGINE for a build-engineering responsibility profile, with related PLATFORM/LIVE/QA where justified. Do not invent a discipline or equate Build Engineer, CI/CD Engineer, Release Manager, QA Engineer and Technical Producer. A principal cross-company release architect is a broader senior sample, not a universal build-engineer definition.

## Three primary employer samples actually opened and read

All access dates 2026-10-31. The pages expose no confirmed publication/update date for the role text; mark dates unknown, not search crawl timestamps. Readable content does not prove hiring availability, historical implementation quality or achieved performance. No salary/contact/application information retained.

### 1. Cygames — ビルドエンジニア／ゲームエンジン／東京 (Japanese original)

https://hrmos.co/pages/cygames/jobs/1793262169510682626

Official chain: https://recruit.cygames.co.jp/career/?search=base_002 lists this exact role (link120). Sections 仕事内容 / 実際の業務 / 開発環境 actually read.

Scoped responsibility sample: Cyllista engine and its game teams' CI/CD, Jenkins automatic tests and game-binary distribution, static-analysis automation, developer support and repository administration. Tools are that employer's named environment, not required global standards. This page distinguishes building support tools from introducing/maintaining existing services. It does not specify artifact approval signatures, reproducibility guarantees or who authorizes public release.

### 2. Bandai Namco Studios — 【ゲームエンジン】CI/CDエンジニア (Japanese original)

https://hrmos.co/pages/bandainamcostudios/jobs/050_0050_sa010_0500_0082

Sections 仕事内容 / 担当業務 / ゲームエンジン開発の固有の特色 actually read. Employer page names SOL-AVES and build, automated testing and package distribution in an on-premises/cloud environment, with pipeline data analysis and developer collaboration. Its platform wording covers Windows and commercial consoles without exposing private SDK requirements. This is shared-engine CI/CD scope, not proof that this team owns storefront approval or every game's deployment. Official careers page https://www.bandainamcostudios.com/recruit/career was also opened; it exposes engine and build categories, but its link17 is a broader engine group and must not be represented as a verified direct link to this exact individual posting.

### 3. Riot — Principal Software Engineer, Developer Connections, Game Release (English original)

https://www.riotgames.com/en/work-with-us/job/8049807/principal-software-engineer-developer-connections-los-angeles-usa

Job ID REQ-0010111; Los Angeles. Introduction and Responsibilities actually read. Senior central-release architecture explicitly spans client, server, backend services, content, configuration and publishing workflows, partnering with game teams and release leadership. It supports a broader cross-surface compatibility/decision interface, not a claim every build engineer has this seniority, release authority, console knowledge or global responsibility. No internal schemas, metrics or operating procedures are public here.

## One bounded real-case lead already read (not an extra employer)

https://tech.cygames.co.jp/archives/3442/

Cygames Engineers' Blog, **2020-10-08**, CEDEC2020 follow-up “Python による大規模ゲーム開発環境 ～Cyllista Game Engine 開発事例～”. Read accessible Q&A text, especially job logging and thumbnail generation; **did not watch the video or read embedded slides**. It reports CI periodically launching a C++ thumbnail runtime and Python submitting resulting thumbnails through the asset system to Perforce. This is a concrete generated-output feedback path into source control, useful for discussing build-input closure and who owns generated artifacts. It does not establish their artifact hashes, approval protocol, loop prevention, immutable promotion or measurable speedup. Retain a compact paraphrase only; no sample code copied.

## Original narrow engineering question

**When a candidate is rebuilt or its content/configuration changes after QA checks, what exactly is being promoted, and whose prior acceptance still applies?**

Proposed role deliverable, not an asserted vendor implementation: a candidate handoff sheet binding code/content revisions, dependency/toolchain/configuration identities, produced package identity, invocation outcome, test evidence target, and the separately authorized promotion decision. Include explicit ownership for generated outputs that later become new build inputs. Treat “same branch/commit,” “pipeline green,” “QA passed,” and “published to environment” as distinct claims.

Finite unexecuted counterfactual for later authoring: QA accepts package A; a second build from the same source revision produces package B after a tool/config/generated-input change. If the handoff records only source revision and a green status, reviewers cannot determine whether evidence for A applies to B. Proposed acceptance rejects automatic carry-forward, or requires an explicit equivalence claim with its scope and owner. This is an original responsibility/acceptance worksheet, **not** proof that the three employers use these fields or have experienced this exact failure. No new synthetic runner is needed at this gate.

Potential interfaces:
- Game/engine teams supply intended revisions, dependency constraints and compatibility assumptions.
- Build engineer supplies attributable executable/package outputs plus failure classification and reproducible invocation context; owns pipeline mechanics, not game-quality verdict by default.
- QA supplies evidence tied to the candidate/configuration and untested scope, not generic timeless approval.
- Release/platform/operations owners specify intended destination, rollout constraints and permission to promote; exact allocation remains organization-specific.

## Why current content does not finish this handoff

- ROLE-QA-001 already says build engineering supplies identifiable artifacts and QA scopes evidence; it deliberately does not profile the upstream production/distribution responsibility or grant QA final release authority.
- SOL-ENGINE-001 (`solutions/engine/asset-import-intent-contract.md`) studies clean-checkout/import/runtime-resource identity, not candidate publication across build, QA and release owners.
- CASE-LIVE-001 (`case-studies/liveops/destiny-config-admission-rollback.md`) explains runtime configuration admission/rollback; it is not a build-engineer role profile or candidate approval chain.
- `research/source-notes/runner-invocation-freshness.md` and the additive fresh harness verify invocation freshness for selected research fixtures. They do not establish game packaging, approval transfer across rebuilds, storefront authorization or a production release workflow. Do not republish that same harness as a new profession-specific result.
- Existing TA profile overlaps generated assets; the proposed boundary is the engine/game build artifact and its evidence transfer, not a claim that build engineering owns all DCC tools.

## Honest access outcomes and stopping rule

Ubisoft release-build job search returned a detailed cached excerpt, but direct French and English pages returned 404; Toronto job endpoint returned “Job not found.” Rockstar position7711020003 direct open returned404. These are excluded as verified role content, not silently sourced from search snippets. Cygames Magazine28424 returned only an iframe, so its interview is not treated as read. The accessible technical blog Q&A is separate evidence. No access bypass or account action attempted.

Gate supports a **narrow ENGINE build-engineering role proposal** with distinct Japanese shared-engine and US senior central-release scopes, not a complete profession survey. Before full authoring, independently re-open chosen role pages and review the actual-case excerpt; keep every original handoff recommendation labeled unexecuted. No need to search indefinitely for more titles. TASK0008 remains incomplete; no new canonical role ID or aliases assigned at discovery stage.
