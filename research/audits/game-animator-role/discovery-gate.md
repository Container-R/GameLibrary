# Source gate — game animator: authored performance versus integrated character combinations

2026-10-31 UTC; bounded TASK-2026-0008 triage only. Recommendation: **game/3D character animator**, primary ANIM, related TA/MODEL/PROG/DESIGN/QA. Technical animator is a collaborating specialization, not an automatic alias. No full role draft, runtime, main-tree or remote changes.

## Verified local gap and non-duplication

Read current `gamelibrary-work/CATALOG.md`, role-directory listing, `roles/technical-art/technical-artist.md`, gameplay-programmer metadata/boundary and `solutions/animation/turn-in-place-foot-sliding.md` metadata. No dedicated animator role in this local snapshot; not a fresh remote-state claim.

ROLE-TA-001 already covers repeatable asset pipelines, rig/technical-animation support, source/import identity and generic FBX acceptance. ROLE-PROG-001 covers playable rules and system interfaces. SOL-ANIM-001 already covers root-motion ownership, foot contact and finite Godot LookAt/evaluation observations. Do not rewrite those as a new role.

New boundary: **a motion can be approved as an authored performance yet remain unsuitable on the actual character proportions, clothing/hair combinations and runtime presentation.** The animator contributes intent and pose correction; technical animation/rigging and runtime integration provide different diagnosis and changes. Successful import or a generic bone-transform test cannot certify the resulting performance. This is not another root-motion or turn-in-place algorithm.

## Primary sources read

Accessed 2026-10-31. Discovery used Japanese `site.bandainamcostudios.com creator-interviews アニメーター リグ モーション` and English `site.ubisoft.com animator interview animation gameplay technical animator`. The following actual page bodies, not search snippets, support the recommendation.

### S1 — concrete named project experience (strongest case)

[Bandai Namco Studios — 仕事紹介：３Dアニメーター](https://www.bandainamcostudios.com/recruit/career/interview/1229), **2021-12-03**, Japanese; studio-authored multi-person account. Specific passage: `私たちは、ここにこだわっています！` → `「アイドルマスター ミリオンライブ！シアターデイズ」の場合`, signed **吉武 敬一朗**, text lines79–91.

Yoshitake describes mocap-based work requiring manual pose adjustment for stylized proportions and further adjustments after engine integration to reduce clothing/hair breakdown. This supports continued animator involvement beyond source-clip authoring, not proof that every combination was exhaustively checked. The account exposes no test matrix, rig implementation, defect counts or engine version. Avoid repeating its historical scale figures as current production requirements.

Also read the page's role introduction13–28 and named Tales of Arise/Gundam examples31–75 to establish context, but a future article should focus on the single above case instead of summarizing all three. Embedded YouTube videos were **not viewed**; no visual quality, timing or technique claims from their content.

### S2 — complementary technical-animation responsibility sample

[Ubisoft Montréal — Senior Technical Animator – March of Giants](https://montreal.ubisoft.com/en/jobs/senior-technical-animator-march-of-giants/), English employer description, **REF31771Z**. Publication date **unknown**; footer2021 is not the job's publication year; current hiring availability unverified.

Exact sections: `Job description`17–27, `Qualifications`29–37. Responsibilities include collaborating with animators/riggers, asset technical validation, integration and engine-side animation/physics prototypes. Supports a possible receiving/supporting role, not evidence this project's real workflow or quality meets those intentions. It does not prove that technical animators own every rig, every export or animation direction globally.

### S3 — same-studio role distinctions, narrowly used

[Bandai Namco Studios recruitment — 2027年新卒採用 アニメーター](https://bandainamcostudios.snar.jp/jobboard/detail.aspx?id=WnBP0-KhtUu_o64YK6Et3A), Japanese employer-hosted recruiting page. Publication date **unknown**;2027 is recruitment cohort, not publication date. Body ends `受付終了` (line333): do not advertise it as an open role.

`業務内容`81–122 distinguishes animator performance work, cinematic work and technical-animation rig/environment support. Useful to avoid conflating titles; it is a responsibility sample, not measured career outcomes. Interview video links78–80 uninspected. No application or login attempted.

### Exact failed source and safe alternative

Ubisoft gameplay-animator search hit at https://www.ubisoft.com/en-us/company/careers/search/744000139618029-gameplay-animator-rainbow-six-siege- returned an actual404 page on open. Its search snippet mentions export/integration but is **not accepted as full-body evidence**. Replaced with readable S2; no bypass or repeated request needed. Other search leads (GDC2016 slides, Toronto challenge PDF, Sonia Pronovost interview) not deeply read, not evidence for this gate.

## Candidate original handoff: character-combination acceptance

One actionable question: **When a source performance works on the authoring character but breaks on a runtime outfit or body variant, what evidence lets the animator and technical owner choose a pose revision, rig/skin correction or runtime-integration fix without silently changing the intended performance?**

Proposed original, unexecuted worksheet—not a studio template:

1. Name intended action/character quality and the review camera/context; animation author provides approved source revision and relevant pose moments, not merely a video marked done.
2. Identify the actual target body, rig/skin revision, outfit/hair and clip/import/runtime setup; reuse existing TA identity guidance rather than duplicate its whole checklist.
3. Review a deliberately bounded set of character combinations in the actual target context. Record which combinations and time ranges were checked, and which were not; a representative sample cannot claim exhaustive coverage.
4. Preserve paired source-versus-runtime observations. Distinguish intentional stylization from unexpected deformation/collision/pose change; diagnosis remains pending until evidence locates the boundary.
5. Record a proposed correction and receiver: animator for intended pose/performance; rig/skin owner for deformation support; integration/runtime owner for altered playback/procedural behavior. These are negotiated interfaces, not universal title-based permissions.
6. Recheck the affected combinations and source intent after a change; shared-rig or shared-clip changes require an explicit impact set. Do not conceal a global regression by approving only the originally failing costume.

Potential hypothetical example for later drafting: a raised-arm gesture works on the authoring body, but one runtime sleeve cuts through the torso. Do **not** preassign the cause to bad animation, retargeting or physics. First pair the exact clip/rig/outfit and observations; decide which change preserves intended silhouette and scope. No real reproduction performed.

## Decision, evidence limits and stopping condition

**Gate passes for one bounded animator role if parent selects it.** S1 supplies a named historical production account; S2/S3 supply complementary role interfaces. Enough evidence for a source-backed responsibility article plus original unexecuted acceptance worksheet; not enough for a verified deformation fix, current studio organization chart or general mocap pipeline recipe.

Unknown: exact DCC/export settings, rig architecture, clothing simulation, acceptance thresholds, combinatorial coverage, frame budget, staffing, current practice and internal approvals. No invented timing values, performance gains, universal engine guarantees or deterministic animation claims. Do not claim headless bone tests establish artistic/visual acceptance.

Stop triage here. A future article should reuse existing TA/animation solution links, keep primary-source paraphrase brief, and label its matrix unexecuted. Runtime work would need a separately defined original/authorized character fixture with an actual visual oracle; it is not justified merely to make a role draft look tested. TASK-2026-0008 remains incomplete.
