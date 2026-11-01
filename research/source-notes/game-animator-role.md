# 游戏动画师岗位：来源记录

访问日期 2026-10-31；对应 [ROLE-ANIM-001](../../管理档案/历史正文/roles/animation/game-animator.md)。正文是有限岗位接口研究，不是特定引擎或完整角色管线的验证。

| 来源 | 作者、日期与语言 | 阅读定位与用途 |
|---|---|---|
| [BNS 仕事紹介：３Dアニメーター](https://www.bandainamcostudios.com/recruit/career/interview/1229) | 企业编辑的多人项目介绍；2021-12-03；日语；采用段落署名吉武敬一朗 | `私たちは、ここにこだわっています！` 的 Theater Days 段落，文本79–91行。提供具体历史制作经历；正文聚焦该段，不展开同页其他项目。 |
| [Ubisoft Montréal Senior Technical Animator – March of Giants](https://montreal.ubisoft.com/en/jobs/senior-technical-animator-march-of-giants/) | 雇主说明，REF31771Z；日期未知；英语 | Job description及职责17–27行、Qualifications29–37行。说明可能的技术动画协作范围；不证明项目内部实际执行效果。 |
| [BNS 2027年新卒採用 アニメーター](https://bandainamcostudios.snar.jp/jobboard/detail.aspx?id=WnBP0-KhtUu_o64YK6Et3A) | 雇主招聘页面；日期未知；日语 | 業務内容81–122行，末尾333行显示受付終了。区分职责名称；招聘届次不作发布日期，页面可读不代表仍接受申请。 |

行号属于当次文本视图，优先按章节回查。Ubisoft页脚版权年份没有用作职位日期。各页链接的视频均未观看，不据此评价画面或推断技术；没有复制图片、视频、完整访谈或规模数据。

## 来源范围与原创部分

S1 没有公开引擎版本、具体 rig/skin 实现、服装算法、检查矩阵或缺陷统计；不能从历史经历推出当前工作室实践或全面质量保证。S2/S3 是雇主职责样本，不是统一职业标准或组织权限表。

正文的源端与运行端配对观察、角色组合记录、假设抬臂/袖口场景和接收步骤均为原创未执行建议，不归因于任何工作室。没有制作资产、运行引擎、测量角色表现或证明故障根因。资料支持 `source-backed` 岗位分析，不支持 `verified` 动画修复方案。

发现使用日语 `アニメーター リグ モーション` 及英语 `animator interview animation gameplay technical animator`。Ubisoft 的 Rainbow Six Siege gameplay animator 职位原链接实际返回404，搜索摘要未作事实依据；改用可读的 S2。未深读的 GDC 幻灯片、挑战PDF及其他访谈不计入来源。

现有 TA 档案已覆盖通用资产身份与导入检查，原地转身文章已覆盖根运动和有限运行观察。初始档案只补动画表演与角色组合接收的职责，不宣称完成全学科岗位矩阵。

## 2026-11-01 补读：S4，平移样条重定时的规范与代数

Khronos glTF 2.0，固定提交 `59ecbdba704206bb656965ab4e202881806066f1`：

- [Appendix C：Animation Sampler Interpolation Modes](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#L3979-L4077)：段时长、归一化进度、逐分量求值及 Cubic Spline Interpolation 公式。
- [Animation sampler](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#L3257-L3293) 与 [animation.sampler.schema.json](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/schema/animation.sampler.schema.json)：秒单位、平移输出类型及时间／输出约束。schema 与正文属于同一规范体系，不计为独立实现验证。

新增小节依据规范求值式，原创推导正统一时间缩放下的切线反向缩放，并手算同进度的 0.75／1／0.75 对照。它只证明理想数学中的平移曲线关系，不证明编码资产合法、逐位一致、引擎播放或艺术质量。没有执行程序、生成资产、观看动画或继承其他动画／glTF 实验的结果；不是规范直接规定的重定时生产流程，也不主张全部 DCC 切线具有相同约定。
