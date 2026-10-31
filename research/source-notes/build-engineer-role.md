# Build-engineering role: source and method boundaries

Accessed 2026-10-31. Intended role: `roles/engine/build-engineer.md`, ROLE-ENGINE-001. Primary ENGINE; PLATFORM/LIVE/QA are related interfaces, not synonymous occupations. Baseline inspected: `gamelibrary-publish-isolation`, six existing role profiles. No runtime, CI service, package publication or organization trial performed for this role.

## Sources actually read

1. Cygames employer page, Japanese: https://hrmos.co/pages/cygames/jobs/1793262169510682626 . Sections 仕事内容 / 実際の業務 / 開発環境. Verified direct official-directory link120 from https://recruit.cygames.co.jp/career/?search=base_002 . Shared-engine and game-development support, not a published release-approval protocol.
2. Bandai Namco Studios employer page, Japanese: https://hrmos.co/pages/bandainamcostudios/jobs/050_0050_sa010_0500_0082 . Sections 仕事内容 / 担当業務 / ゲームエンジン開発の固有の特色. SOL-AVES shared-engine pipeline sample. Official https://www.bandainamcostudios.com/recruit/career exposes engine/build categories; its broad engine link is not asserted to resolve directly to this exact posting.
3. Riot employer page, English: https://www.riotgames.com/en/work-with-us/job/8049807/principal-software-engineer-developer-connections-los-angeles-usa . REQ-0010111; introduction and Responsibilities. Senior central-release architectural scope, not a universal build-engineer responsibility or authority model.
4. Cygames engineering blog: https://tech.cygames.co.jp/archives/3442/ , dated2020-10-08. Read accessible Q&A text, including thumbnail-generation answer. The article documents CI-generated thumbnails submitted through its asset system to Perforce. No slides/video inspected, no third-party implementation copied. It does not establish that thumbnails ship, any rebuild incident, or tested-package promotion guarantees.

Role pages have no confirmed original publication/update dates. Do not substitute search crawl dates, assert hiring availability, or retain salary/application/contact material. Named tools/platforms describe employer scope, not independently verified support, recommended purchases, SDK access or performance.

## Original contribution and exclusions

The six-stage handoff and five-row candidateA/rebuildB worksheet are original, explicitly unexecuted proposals. Code revision, package identity, external configuration, test evidence and promotion authorization are distinct objects. An equal package hash does not establish identical external runtime dependencies; a differing hash does not alone identify a gameplay difference. Explicit evidence scope and decision ownership are required rather than mandatory full retesting or automatic approval.

The published invocation-freshness harness is adjacent executed evidence for limited research runners. It does not test this new role's release workflow. The Destiny case concerns runtime configuration admission/recovery, not package promotion. No claim of complete occupation coverage or new aliases.

## Discovery exclusions retained

Direct Ubisoft release-build pages returned404 and Toronto's job-download endpoint returned “Job not found,” despite rich search excerpts. Rockstar7711020003 returned404. Those excerpts are not role evidence here. Cygames Magazine28424 exposed only an iframe; its interview is not claimed read. No access bypass, account write or job application was attempted. The accepted employer/case evidence is the four accessible pages above.

## Optional technical reference, not employer practice

SLSA v1.2 official pages, accessed2026-10-31: https://slsa.dev/spec/v1.2/build-provenance (Model, BuildDefinition, RunDetails, BuildMetadata) and https://slsa.dev/spec/v1.2/verifying-artifacts (How to verify, Step1/2). Artifact identity and invocation identity are different; dependencies are best-effort even through Build L3. Verification includes matching the artifact subject digest and checking the envelope signature against configured signer/builder trust and expectations. These support only the short terminology/trust distinction. No copied schema, signing implementation, SLSA level claim, employer adoption inference or QA/promotion certification.
