# 图形程序岗位：三份雇主材料的证据边界

读取2026-10-31；支持ROLE-GFX-001职责研究，不是招聘有效性报告或技术性能验证。

| 来源/精确地址 | 已读定位 | 能支持 | 不能支持 |
|---|---|---|---|
| Ubisoft Montreal，Senior 3D Programmer，744000138127992；https://www.ubisoft.com/en-us/company/careers/search/744000138127992-senior-3d-programmer | JOB DESCRIPTION / What you'll do / Qualifications | Unreal多人项目的小团队高级跨域职责：引擎、帧性能、预算/回归及跨部门协作 | 所有图形程序都领导预算；Unreal具体版本；本库方法已经被使用 |
| Capcom，レンダリングエンジニア，01_06_020；https://hrmos.co/pages/capcom/jobs/01_06_020 | 仕事内容 / 歓迎条件 | RE ENGINE团队回应功能需求、支持发布，开展GPU/CPU优化和资产技术工作 | 当前RE ENGINE技术版本或全平台支持矩阵；职称全球等同 |
| Techland，Rendering Programmer；https://techland.net/job-offers/rendering-programmer | Job Description / Qualifications | 自研引擎渲染系统设计、实现、维护及相关技术能力 | 与Ubisoft高级岗位相同的审批权限；所有产品/主机效果已被独立验证 |

Capcom来源链为雇主公开职位总表 https://hrmos.co/pages/capcom/jobs → レンダリングエンジニア独立页；已直接读原始日文，不依赖招聘聚合器翻译。Ubisoft和Techland为各自官方站点英文全文。三页未确认首次发布日期/修订日期，抓取时间不是发布日期；访问成功不是雇佣承诺。只使用职责与技术能力段，不保存职位全文、人事联系方式或薪酬。

引擎/工具名只标识雇主环境与能力示例，没有推断软件版本。岗位文档中的六阶段交接、五行阴影功能工作表均是原创建议；假设反例没有实际截图、帧时间或团队试用数据。它们不构成标准、认证、真实项目复盘或跨平台性能结论。

原始岗位建档时27篇/5岗位基线来自gamelibrary-publish-native-root。GFX已有图形程序候选方向，但此前无对应岗位档案。TA、矩阵接口、纹理预算和Niagara文章提供相邻知识，不覆盖完整功能的职责接收包；不将新增局部研究宣称为TASK0008完整职业矩阵。

## S4：公开生产案例补证，而不是把职位广告当生产结果

Wube Software，Friday Facts #227 - Rendering, Trees & Scenario talk，2018-01-26，https://www.factorio.com/blog/post/fff-227 。署名Posila、Ernestas、Klonan；实际选读Rendering/VRAM optimizations（Posila）与Trees refresh（Ernestas）正文。前者解释不同机器优化结果可能相反以及设置开关，后者说明树/阴影拆分的空白像素与视觉变化、当时正在进行的树素材重做。不保存图片，不声称观看视频或执行游戏；2018进展不能变成当前性能保证、最终发布验收或已完成重做。

这里只以简短事实支持“渲染改变需与内容视觉接收共同处理”的原创责任推导，不重述整个帖子、数值表或其他场景章节。该案例与库中Factorio派生缓存失同步是不同原始帖子/问题，不将缓存案例冒充渲染经验。

## 2026-11-01 补读：深度效果的比较量与重建空间

- **S5：** Clay John，*Introducing Reverse Z (AKA I'm sorry for breaking your shader)*，**2024-04-29**。[Godot 官方原文](https://godotengine.org/article/introducing-reverse-z/)。读取引言及 Writes to POSITION、Writes to DEPTH、Reads from depth_texture、Operations in clip space（本次文本约 32–116 行）。用途是历史 4.3 迁移路径的区别，不是当前所有 renderer 的完整规范。未照搬其中向量与标量比较的示例，也未采纳性能或精度收益为本库测量。
- **S6：** Godot **4.6**，*Advanced post-processing*，[版本化官方教程](https://docs.godotengine.org/en/4.6/tutorials/shaders/advanced_postprocessing.html)，Full screen quad、Depth texture（本次文本约 16–88 行）。用途是 renderer 对应的 NDC 区间及逆投影／齐次除法步骤。页面可变，未将它标成固定实现源码；未采用末尾优化讨论作为结论。

新增水面提示表是原创未执行决策例，不是已发现的项目事故。视轴量与欧氏长度的区分及 `(3,0,−4)` 示例为数学解释，不来自渲染输出；教程的距离措辞没有被扩展成径向距离或物理水厚保证。未执行 shader 编译、GPU 捕获、图像或精度／性能比较；未检查原文图片，不转载代码块或图表。复用两页内容的正文与本记录合并保持简短。
