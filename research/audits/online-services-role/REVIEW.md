# Independent review — ROLE-NET-001 online services engineer

Date: 2026-10-31. Read-only review of the draft, source note and discovery gate; exact local input SHA256 values recorded in `input-hashes.json`. Original two primary sources independently opened and read. No workload, service calls, account access, simulated HTTP server, repository staging or remote writes performed.

## Verdict

**Accept as source-backed role profile. No material issue requiring revision found.** This acceptance concerns source fidelity and scoped original synthesis, not production service validation or completion of the global roles matrix.

## Source fidelity

### BNS Japanese interview19539

Independently read the official Japanese page's role, work-interest and professional-priority sections. Named-speaker attribution in the draft matches the source:

- 青木 describes a broad team scope rather than a universal individual job definition.
- 松島 describes cross-company client/server coordination and explicitly identifies his original background as client engineering. The draft does not relabel him as proof of one standard backend profession.
- 何 describes shared foundations and post-matchmaking start support across projects.
- 天野 describes technical-director coordination, with members doing design/implementation.

The unknown publication date is appropriately retained: the inspected article body exposes no clear date, and crawler recency is not publication evidence. The draft's umbrella job title and responsibility matrix are an editorial classification, not asserted to be BNS's official standardized position. The source is employment/team testimony, not protocol documentation or capacity evidence.

### Riot2020 historical platform testing

Independently verified article date2020-12-15 and Keith Gunning's introduction. Infrastructure sections separate frame-to-frame game-server execution from platform services. Harness sections describe simulated requests and background polling, while *Simulating Game Servers* explicitly replaces actual gameplay execution with mock provisioning/results behavior. *Extensive Monitoring* supports whole-test-duration metric acceptance rather than one successful response.

The draft correctly treats this as historical first-party self-report. It does not promote mock-client/mock-server traffic into actual game tick performance, render quality, full real-client handshake proof, independent reproduction or present-day VALORANT architecture. It also avoids importing headline scale figures as transferable benchmarks. The source's separate game-server testing reference is not falsely presented as a source this profile independently reproduced.

## Original worksheet and role scope

The service-chain table, implementation-identity fields, omitted-boundary recipient and acceptance decision are repeatedly marked original and unexecuted. They are not attributed to private BNS/Riot runbooks. The hypothetical report example preserves useful platform observations while refusing a broader real-session claim; it does not declare all mocks invalid.

Responsibilities are split among client/gameplay/backend/infrastructure/QA/release owners without giving this role automatic authority over all of them. Pre-/post-match service scope remains distinct from the existing client prediction article. NET is reused; LIVE/PLATFORM/QA/PROD are cross-relations, not invented discipline replacements. Neither the article nor source note completes TASK-2026-0008.

The recommendation to obtain an authorized actual-project service chain before future integration/load work is appropriate. There is no fabricated execution, numeric threshold, distributed exactly-once guarantee, security certification or toy-workload-as-production-evidence claim.

## Evidence limits retained

Two organizational samples do not establish a global occupation standard. The worksheet is a proposal, not an exercised acceptance gate. Cross-platform is a responsibility scope marker, not platform test coverage. First-party interview and engineering post provide different evidence types; neither substitutes for local traces, service versions or a workload provenance record.

No cosmetic edits requested; avoid expanding this focused role profile with the optional2025 capacity article or inaccessible job listings merely to increase source count.

## Independently checked primary pages

Accessed2026-10-31:

- [Bandai Namco Studios Japanese interview19539](https://www.bandainamcostudios.com/creator-interviews/19539): sections サーバー開発にとどまらない、多岐にわたる役割; ゲーム体験を支える、サーバーエンジニアの面白さ; 単純な技術力だけではない、仕事へのこだわり. Current text view lines24–86.
- [Keith Gunning, Scalability and Load Testing for VALORANT](https://www.riotgames.com/en/news/scalability-and-load-testing-valorant): introduction; Infrastructure; Microservice Testing; Load Test Harness; Harness Components; Simulating Game Servers; Extensive Monitoring. Current text view lines7–104.

Section names are the durable locator; text-view line numbers are access-time aids. No source images, code or complete text copied into this review.
