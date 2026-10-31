# Discovery gate: online services engineer, not another client prediction role

2026-10-31. Read-only source discovery; no article, queue, main-tree or remote edits; no runtime, traffic generation, credentials or installation.

## Actual coverage and priority judgment

Read current `gamelibrary-work/CATALOG.md`, `taxonomy/disciplines.json`, role paths and TASK-2026-0008. Catalog contains **30 indexed items and 7 role profiles** at this inspection: gameplay, technical art, level design, QA, interactive audio, graphics and build engineering. There is no online/backend services role profile. NET already exists in the candidate taxonomy with authoritative servers, synchronization, backend services, distributed/database work and multiplayer security. Therefore **do not add a new discipline**, and do not describe NET as completely empty.

Highest-value next missing role, as a research prioritization judgment: **在线服务工程师 / Online Services Engineer**, primary NET, related LIVE/PLATFORM/QA/PROD. Narrow scope is pre-/post-match service orchestration and operational acceptance, not frame-to-frame game simulation, all database engineering or universal security ownership.

Existing exact evidence does not close this gap:
- `solutions/programming/client-prediction-authority-boundary.md` verification_method: `原始来源核对与既有原创离散协议模型16项测试；跨实体依赖补充为未执行手算与验收提案；未进行引擎、真实网络或跨平台物理验证`. This covers prediction/replay, not a login/party/match/provisioning service flow.
- `case-studies/liveops/destiny-config-admission-rollback.md` verification_method: `第一方事故说明与当前基础设施概念文档核对；事实、当时措施状态与原创验收建议分层；无生产日志、事故复现或部署试验`. Valuable admission/recovery case, but no role profile or end-to-end capacity proof.
- Existing local SQLite transaction tests prove their local storage boundaries, not distributed service correctness or production load. Do not transfer their PASS to this role.

TASK-2026-0008 remains `needs-research`, intended full roles/work-area matrix, with an explicit note that a partial audit is not completion. Its next_action still says 28 articles / six roles; that is stale descriptive context, not a reason to alter the task in this discovery pass.

## Three original sources actually read

All accessed 2026-10-31. Short fact summaries below; no copied diagrams, source tables or performance graphs. Published claims remain attributed, not independently reproduced.

### S1 — Japanese employer team interview: responsibility evidence

[Bandai Namco Studios, ゲームの“面白さ”に踏み込むサーバーエンジニアとは？【後編】](https://www.bandainamcostudios.com/creator-interviews/19539)

Language Japanese; first-party studio interview. **Publication date unknown in the inspected page body**; do not substitute the search engine's “five months ago.” Sections actually read: サーバー開発にとどまらない、多岐にわたる役割 (text-view lines 24–46), ゲーム体験を支える… (47–61), 単純な技術力だけではない… (68–86).

Named interviewees 青木, 松島, 何 and 天野 describe different scopes: one team combines infrastructure, server applications, CI/CD and management tools; another engineer bridges client and server development companies; shared server foundations support starting play after matching; a technical director emphasizes coordination. This is evidence of **variation in real responsibilities**, not proof that every online engineer owns every listed task. The interview supports cross-team interface work and launch-to-operation thinking but exposes no production protocol, benchmark or fault log.

### S2 — US studio engineering project: service test applicability boundary

[Keith Gunning, Riot Games, Scalability and Load Testing for VALORANT](https://www.riotgames.com/en/news/scalability-and-load-testing-valorant), **2020-12-15**, English.

Read introduction; VALORANT’S Infrastructure / Microservice Testing; Load Test Harness / Harness Components; Simulating Game Servers; Extensive Monitoring (text-view lines 11–104).

The author separates moment-to-moment game-server execution from platform services. Their load harness reproduced service requests and background polling; scenarios included queueing, Agent selection and connecting after provisioning. Mock game servers reproduced provisioning and results recording without gameplay logic. Per-service tests were insufficient for cross-service request chains, and acceptance required monitored metrics to stay within bounds for the test duration. This is a **historical project report**, not a current architecture specification or our executed test. Its mock-server boundary is especially useful: platform load evidence is not gameplay server/tick capacity evidence. We do not need to reproduce headline concurrency numbers to explain that distinction.

### S3 — US studio engineering project: optional capacity-depth evidence

[Tomasz Mozolewski, Riot Games, Improving Performance by Streamlining League’s Server Selection](https://www.riotgames.com/en/news/tech-blog-cpu-usage), **2025-01-16**, English.

Read The Old and the New, The Goals, Building a Simulation, Game Cost, Auto Scaling, Solution Criteria, Results, Scoring, Live Results and Learnings (text-view lines 23–277). No unread graph values are extracted.

Their investigation considers delayed CPU observations and changing per-match demand; a lowest-current-CPU strategy can bunch young games whose resource use later rises. The team chose a simple allocation strategy using project-specific scenarios and later compared live shards. This supports a distinct handoff between gameplay demand profile and allocation policy, not a universal recommendation for Round Robin, a transferable CPU threshold, or independent reproduction. **Keep as an optional follow-on source, not a second large case recap in a role profile.**

## Original concrete engineering handoff question

**When QA reports “the online platform supported the target load,” exactly which client-to-service-to-game-session chain ran, which endpoints were mocked, and which party owns the first omitted boundary before calling the product launch-ready?**

This is not merely “add monitoring.” An original proposed acceptance handoff would name:
1. The supported user action sequence (e.g. party → queue → selection → allocated session → connect → result acknowledgement), with actual product-specific success/failure semantics chosen by the team.
2. Which steps used the released client, a service-request harness, actual services, actual game-server executable or a mock. Each omitted behavior remains explicit.
3. The input workload's arrival pattern/background polling/session durations and versioned configuration, with provenance rather than invented player data.
4. The owner of each transition, its timeout/failure observation and functional outcome, not only aggregate request throughput. No exactly-once/retry guarantee is inferred from these sources.
5. A separate acceptance item for real game-server simulation and client integration when the platform test deliberately mocked them.

These five items are **our proposed synthesis**, not the studios' private runbook or exact published protocol. Role responsibilities are supported by S1 and S2; the particular field choices and release gate remain an original unexecuted design. A small toy HTTP simulator would only demonstrate our invented system and is not proposed as production evidence.

## Discovery exclusions and decision

Two Ubisoft leads did not yield usable responsibility evidence: the original SmartRecruiters Online Programmer page `744000155910588` returned an expired-job page; `744000154357833-online-programmer-snowdrop-` was inaccessible through the reader. No aggregator snippet is promoted to an employer claim. The Montréal identity-services page was opened as reconnaissance but is not needed for this focused role. No region-count claim is made from inaccessible listings.

**Gate passes for a source-backed role draft**, if selected by parent: combine Japanese direct team testimony with Riot's explicitly scoped platform test case; retain source dates and role variation. Prefer a bounded profile and one original evidence-boundary worksheet, not a universal cloud architecture tutorial. No runtime follow-up is justified without an authorized actual service/project and a specific load-test question. This advances TASK-2026-0008 partially and does not complete the global matrix.

## Inspected local identity

- CATALOG.md SHA256 `dd3ee71923898173a96c491869ce6fd13ee65fbceaabb7f296068d966de0d60b`
- taxonomy/disciplines.json `c28cc442ed8851804e5d96bc6a38b27bc8ad367e8218441178e37905d4e79025`
- SOL-NET-001 `833d6d37ee69bc6f6665fb7516f54fd3f81deb71c1f36c296528bd158cdcc3ae`
- CASE-LIVE-001 `a94ace53738b20613f4e11ad89540c03d6efed9920ef0bd1df8b60afdac05924`
