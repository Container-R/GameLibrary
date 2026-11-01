# Accepted VFX role — integration checklist

2026-11-01. Main integrator owns staging, indexes, task records and remote writes. This checklist changes none of them.

## Exact accepted inputs

| Local input | Proposed canonical destination | SHA256 |
|---|---|---|
| `article.md` | `roles/vfx/real-time-vfx-artist.md` | `f733913c5763787c9ba7c9f36485be4965434aa47e56a70a2982719be5cfe59a` |
| `source-note.md` | `research/source-notes/real-time-vfx-artist-role.md` | `f1a0010ed3d3dc86a94f22e3ed9b48709f942d53e05ea45ccf983dc0dd558fc5` |

Profile `ROLE-VFX-001`, primary `VFX`, status `source-backed`; updated2026-11-01, review_after2027-02-01. Independently accepted unchanged: `research-drafts/deep-qa/vfx-role/REVIEW.md` and `hashes-and-links.json`. Author checks: `draft-checks.json`. Rechecked hashes unchanged at checklist creation. Recheck collision and canonical links against actual integration base, not just this earlier local snapshot.

## Proposed reading route

Suggested route ID `role-real-time-vfx-artist`, title `从实时特效美术出发：游戏信号与情境接收`, kind `role`, subject_profile_id `ROLE-VFX-001`. Match existing route schema; route ID is a proposal, not already installed.

| Exact existing document ID | Exact repository path | Reader question / scope |
|---|---|---|
| `ROLE-PROG-001` | `roles/programming/gameplay-programmer.md` | 谁提供实际状态、触发和判定契约？效果绘制不是权威规则。 |
| `ROLE-TA-001` | `roles/technical-art/technical-artist.md` | 能否定位同一候选及其资产/导入条件？技术接收不代替信号含义判断。 |
| `ROLE-GFX-001` | `roles/rendering/graphics-programmer.md` | 哪些证据支持把问题升级到系统性渲染？不能只因效果不清楚就认定渲染器有错。 |
| `SOL-VFX-001` | `solutions/vfx/niagara-performance-budget.md` | 如何分开实例、模拟和像素成本？该文是未执行预算协议，不是本角色的性能验证。 |
| `SOL-PROD-001` | `solutions/production/playtest-intervention-evidence.md` | 玩家理解的判断是否被解释/提示改变？专家审查或作者演示不是无提示识别结果。 |

IDs/paths above directly checked in current local `gamelibrary-work`. All five are existing links in the accepted article. The new article and source note link reciprocally. Add catalog/discovery/taxonomy route using repository conventions; do not inflate runtime evidence or call the overall TASK-2026-0008 matrix complete. Existing TA/GFX roles need not have their responsibilities rewritten to integrate this profile.

## Source and version limitations to preserve

- BNS `https://www.bandainamcostudios.com/recruit/career/interview/1034`: dated2021-08-24; Japanese, 小島武史 Tales of Arise passage28–34 and role intro11–23. Historical timing/readability collaboration, no implementation code, player-study outcome or quantitative gain. Frame-level authoring does not imply a universal one-frame tolerance.
- Riot `https://www.leagueoflegends.com/en-au/news/dev/clarity-in-league/`: dated2021-03-12; bananaband1t. Hierarchy and visible textual Shan Hai Scrolls Jhin boundary revision; no independently observed current-game behavior. Other carousel slides and media were not visually inspected; no reconstructed timings or player response measures.
- Riot `https://www.riotgames.com/en/news/valorant-shaders-and-gameplay-clarity`: dated2020-06-30; Brandon “mochi” Wang. Historical VFX/systemic-rendering responsibilities and gameplay smoke boundary versus cosmetic detail. Not universal shader implementation, present-day quality-tier invariance or proof of fairness/network visibility. Source-reported compatibility testing is not this library's test.
- All originals accessed2026-11-01. Metadata versions identify historical source dates, not engine API versions. No fixed engine version is asserted by this role. `engine-agnostic` does not mean experimentally validated across engines; platform field expressly describes responsibility, not validation.
- Ground-warning example and signal-handoff worksheet are original and unexecuted; not Jhin reproduction or any studio's internal template. Actual state, intended cue, rendered observation, context review and player understanding remain separate.
- No engine run, GPU/frame measurement, video/frame analysis, accessibility test, player study or source-asset inspection. Do not change status to `verified` or increment experimental check totals for this unit.
- No universal color/brightness/timing thresholds, cohort outcomes, complete scenario coverage or automatic assignment of damage/collision/rendering authority to VFX artists. Performance and essential information are separate acceptance axes.

## Main-owned final checks

1. Preserve accepted input bytes unless a substantive integration correction is necessary; if changed, record new hash/review scope.
2. Resolve canonical links and profile/route IDs, rebuild generated indexes under current repository rules, and verify route reachability.
3. Keep source-history and unexecuted-workflow limitations in publication/state summary; distinguish source acceptance from runtime evidence.
4. Record actual publication path/SHA only after remote verification. No publication has been performed by this child.
