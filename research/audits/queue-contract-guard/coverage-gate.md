# 分类与研究深度门槛（2026-10-31 20:09 UTC快照）

只读基线：`gamelibrary-publish-broker/`。读取研究Skill的 `references/01-taxonomy-and-roles.md` 与 `05-repository-contract.md`。未修改主树/远程，未运行引擎或新夹具。本轮不是追求新增分类数量。

## 实际结构核对

- 25份被索引文章：5岗位、18方案、2案例；均有唯一稳定文档ID。
- 22个不同primary discipline；非遗留学科中只有BIZ尚无主类文章。**这不等于BIZ没有知识**：`research/source-notes/steam-capsule-handoff.md`已有NOTE-BIZ-STEAM-ART-001，作为源说明未进入CATALOG是当前索引范围，不应改称缺失文档。
- taxonomy有24个ID，ACCESS明确为legacy-umbrella并split_into A11Y/LOC；不能重复算成24个独立完成领域。此次25篇primary/inline related_disciplines全部引用存在的ID。
- CATALOG的25个本地链接均存在，路径集合与实际25篇文章一致；没有重号或漏项。
- 6条人工阅读路线、26个entry，引用的document_id均存在；5条role路线的subject_profile_id均指向实际role档案。
- 只读实际运行：`python -B gamelibrary-publish-broker/scripts/navigation/build_routes.py gamelibrary-publish-broker --registry gamelibrary-publish-broker/taxonomy/reading-routes.json --output gamelibrary-publish-broker/DISCOVERY.md --check`，返回0，输出 `navigation matches`。没有重生成文件。
- queue共48条、ID无重复：46 published、1 needs-research、1 researching。任务published不等于每条增加一篇文章；多条是来源/审查/既有文章加深，25篇与46条不是矛盾。

## 具体问题与优先级

### 1. 已知分类错误：TASK-2026-0048的RENDER不是有效ID

全量检查queue各discipline，**只找到这一条未知ID**；应使用现有GFX，不新增同义空类。协调者已知道并安排修正，本报告不冒称新发现。

更重要的守门缺口：`scripts/test_taxonomy.py`当前检查taxonomy兼容性与文档frontmatter，但不遍历queue discipline；因此既有taxonomy测试通过不能证明队列分类合法。建议下一次维护时加一条只读queue ID引用校验，避免同类问题再进入恢复状态；不是增加新研究文章。

### 2. 新近任务的expected_artifact从路径变成自由描述，降低断点恢复定位能力

- TASK-0045：`solutions/programming/fixed-step-simulation-boundary.md and finite policy/actual callback evidence`
- TASK-0046：`Existing asset-import/ownership solution plus actual ResourceLoader evidence`
- TASK-0047：`Existing asset-loading article plus bounded request ownership evidence`
- TASK-0048：`Source-backed matrix layout handoff with original compiler and host-byte evidence`

Skill要求expected_artifact字段但未强制其值只能是路径，因此这**不是已证明的schema违例**。然而前面多数已发表任务可以直接定位文件，新值不能作为路径解析；自动恢复不应把英文描述当缺失文件。

建议保留字段向后兼容，同时为已发表任务增加明确 `artifact_paths` 数组或同等明确字段。0045至少定位固定步文章与对应实验；0046/0047定位同一资产文章及各自实验。不要为了字段命名把这些真实已发表成果标成missing。TASK-0008的预期 `taxonomy/roles-and-work-areas.md`尚不存在，但它本来仍为needs-research，不算丢失的已发表产物。

### 3. 角色tag不是已批准别名；现有五个岗位不能代表所有责任覆盖

现有标签包含qa-engineer(10篇)、qa-tester(5)、performance-qa(2)、game-quality-assurance(2)，以及sound-designer/technical-audio-designer/interactive-audio-designer等。没有受控别名表证明它们同义，**不应自动全替换成现有岗位ID**。QA档案和显式subject_profile路线已经避免了这个误归并；这是应保持的边界，不是要求再建几十个岗位空页。

没有找到当前路线将不存在岗位冒充已完成档案的情况。职业轴缺少部分专门岗位不必立刻补文章；先看现有交接是否缺明确负责人与验收物。

### 4. 低优先级的路线说明重复，而非断链

SOL-ENGINE-001在TA、QA、关卡策划三条路线的rationale都追加了同一句候选根/外部依赖隔离说明。内容真实，链接有效，但“从关卡白盒交接出发”为何需要读加载对象图的理由较间接。可由编辑按路线问题分别精简，而不是自动把每个新增技术段都复制到所有入口。无需新增分类、路线或用户导航效果声明。

## 只推荐一个后续来源发现问题

### AI/关卡/角色控制：调整NavigationAgent半径是否会改变可通行路径，还是只改变避让？

**具体问题**：关卡为一种体型交付通道，角色碰撞体后来变大；项目仅调NavigationAgent2D.radius，仍获得到原目标的路径。负责导航的人和负责角色碰撞的人应交付哪些不同参数/证据，才能避免“查询可达”被当成“实体能通过”？

这一问不是重新宣告已有文章漏测：`SOL-AI-001`已经明确未测角色移动、碰撞/半径侵蚀。它现有真实证据是图同步与断开区域部分路径；`ROLE-DESIGN-001`已有版本化运动/布局交接，但没有实际检验避让半径、烘焙半径和物理碰撞体三者的API差别。25篇中的Root Motion、固定tick、资产所有权和网格字节内容也没有回答此配置误用。

本轮只做一次定向官方来源检查，实际读到：
[Godot4.6 NavigationAgent2D.radius](https://docs.godotengine.org/en/4.6/classes/class_navigationagent2d.html#class-navigationagent2d-property-radius)，访问2026-10-31，属性段明确radius用于avoidance，不改变普通pathfinding；更改路径查询所适用体型要处理NavigationPolygon.agent_radius与相应地图。该类仍标Experimental。**不据此宣称已经运行烘焙或碰撞实验。**

下一次来源门槛应进一步锁定官方NavigationPolygon.agent_radius与CharacterBody2D运动/碰撞语义，确认何处实际改变导航几何，何处只是元数据/避让。只有来源支持明确可控差异后，再提出实际引擎对照；本轮不批准运行。

**希望交付的工程成果**：一个针对“体型改变”的责任/配置验收小节：关卡几何、导航适用体型、避让radius、物理形状、目标容差分别由谁确认；若做有限真实夹具，必须同时记录查询路径与实际碰撞/位移，不能只把两组相同路径打印成“实体不能通过”的证明。可以先限制在无RVO、固定静态几何的窄对照，不马上实现完整NPC控制器。

**停止条件**：若只能重述已知API句子，或无法独立控制路径几何与实体运动条件，则保存源码说明而不制造新夹具。若有可证伪、无安装/素材依赖的具体对照，提交单独门槛等待验收。沿用现有二进制身份未认证的限制，不把真实加载/导航回调升级成官方构建认证。

不推荐因为BIZ零主类就强行发表商业概览，也不插队打断正在进行的GFX矩阵证据。先修queue引用检查与产物定位，再选择上述唯一深度问题，比继续扩大空类别或重跑同类模型更有价值。
