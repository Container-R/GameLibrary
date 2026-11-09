# 模块化环境的分件粒度与预制组合设计：独立技术审稿

审查日期：2026-11-09。审查性质：独立模型技术审稿，未参与正文初稿或插图制作。两张原创图为本轮按正文重新制作，不是旧版图的恢复副本。没有执行 DCC、Unity 或其他引擎实验，也没有工时、性能或玩家测试。

## 结论

正文与两张插图的技术内容通过。全文已重新完整阅读，不仅检查新增句；两张 SVG 已由审稿者独立渲染为 PNG 并实际查看，逐项核对坐标、图例、箭头与全文。来源文字记录与 JSON 的 S4/S5 编号也已核对一致。

文章完成了其承诺：帮助有基础建模、局部坐标及编辑器装配知识的读者决定拆件入口、保存常规装配、处理局部改造后的边界及依赖。没有把原创方案说成实际项目资产，没有把对象数当作工时或 draw call，也没有把 Unity 文档规则说成原生运行观察。

## 全文技术复核

从三种修改需求到四件标准组合，再到破墙收口、换地板与更新传播，论证连贯。网格资产、日常摆放单元、局部修改对象的区分可直接用于生产判断。固定原点及局部变换使替换不必重新摆位，但正文仍要求查接合、碰撞和可见表面，没有把相同外部尺寸当作所有内部责任已满足。

破墙不是删掉完整右墙：保留 x=0…1 与 x=3…4，开口为 x=1…3。两侧墙厚端面、较高侧室显露的天花侧边、同高地板接缝及附着物分别处理，覆盖本例关键几何责任。增加 0.04 米铺装使行走面由 z=0.25 升到 0.29，正文正确把它视为空间规格变化，而非单纯换材。

新增结构操作澄清恰当：在保留子对象时换网格引用，仍需核对碰撞与附着内容；删除、增加对象或改变父级另查目标工具规则。它解决“换资产等于可以任意改继承层级”的歧义，又未把通用方法扩展为 Unity 按钮教程。

实例覆盖、复用变体及拆解的维护代价区分清楚。F0 内容修改与把引用字段从 F0 换成 F1 的传播范围不同；已将字段覆盖成 F_break 的变体不应自动改用 F1。普通 Unpack 对变体根与嵌套实例的例外准确；完全解包也不等于复制成私有网格或材料。

## 两图实际检查

### 图 1：modular-granularity-sections.svg

- 上部为 X–Z 投影，下部为 x=2 的 Y–Z 断面，水平轴不同已经明示，未把投影线误画成可见的厚度面。
- 完整墙与破墙的地板顶面 z=0.25、墙顶/天花底面 z=3.25、天花顶面 z=3.45 相互一致，净高为 3 米。
- 两残墙及中央 2 米开口位置正确。红色竖线位于 x=1、3，文字解释端面须覆盖 y=1.5…1.7 的 0.2 米厚度，避免读者把端面当一条无厚度边。
- 下部仅画右半走廊；x=2 位于开口内，虚线只指原墙范围，没有残墙。较高侧室顶部与走廊天花右侧边的显露关系成立。
- 地面在 y=1.7 接合，双方顶面同为 z=0.25；红线及引线分别指向天花侧边和地板接合，没有暗示侧室地面抬高。
- 图例、文字和可见边界互相一致，未见文本遮盖关键尺寸、错误坐标或需修改的技术图示。

### 图 2：modular-granularity-dependencies.svg

- 实线从使用者指向网格资源，虚线从实例/变体指向来源/基础组合，箭头朝向与图例一致。
- 普通实例无地板覆盖，局部换地板实例直接引用 F1，破墙变体覆盖为 F_break；三者没有混成同一种继承路径。
- 图中标准组合明确仍为 F0 的初始状态，底部另分 A 修改 F0 内容、B 标准组合 F0→F1、C 单实例覆盖为 F1，避免静态图和变更后状态混淆。
- A 的影响检查仍指向 F0 使用者；B 指出普通实例继承新字段而 F_break 保持覆盖；C 不改变标准组合字段或资源内容。没有把字段变化画成资源被整体改写。
- 墙和天花资源另有引用，图注明示箭头不表示自动合并网格；拆解与资源私有化区分清楚。

## 原始来源核对

以下为审稿者于 2026-11-09 直接阅读的公开材料，不是根据研究记录推定已经阅读。

1. Joel Burgess、Nate Purkeypile，The Modular Level Design of Fallout 4，GDC 2016。
   https://www.slideshare.net/slideshow/gdc-2016-modular-level-design-of-fallout-4/59770460
   定向查看粒度段文字，并实际查看 86、88、94、96、99 页原始幻灯片预览图。86 页拆分标示、94 页 20/123 对象、96 页 Pack-In 与 Exploded Granular 均支持正文有限陈述。原图为 320×180 预览，足以核对这些标示，不用于精细画面评价。未观看完整演讲，不推断 Pack-In 内部实现。
2. Joel Burgess、Nate Purkeypile，Skyrim's Modular Approach to Level Design，2013-05-01 作者署名转载。
   https://www.gamedeveloper.com/design/skyrim-s-modular-approach-to-level-design
   实读 Graybox、Build-Out、Polish 周边有关结构特征、常用件优先及 helper markers 的文字。支持正文的制作交接建议；没有据此评价全部插图的视觉表现。
3. Unity 6.0，Override prefab instances，Behavior of overrides。
   https://docs.unity.com/en-us/engine/6000.0/manual/working-with-gameobjects/prefabs/override/prefab-instance-overrides
   同字段覆盖优先的文档规则支持正文更新传播分析；它不等于资源内容修改规则。
4. Unity 6.0，Create variations of prefabs，基础继承及 Edit a prefab variant。
   https://docs.unity.com/en-us/engine/6000.0/manual/working-with-gameobjects/prefabs/prefab-variants
   支持变体通过覆盖表达差异，不证明任意重设父级可行。
5. Unity 6.0，Revert a prefab instance to a GameObject，Unpack / Unpack Completely。
   https://docs.unity.com/en-us/engine/6000.0/manual/working-with-gameobjects/prefabs/unpacking-prefab-instances
   直接确认普通解包保留嵌套实例、变体解包后的根仍是 base instance、完全解包进一步解除关系。

来源 JSON 的五项核心主张、定位及限制与以上实际读取一致。正文原研究访问日期与本次独立复核日期分别保留，二者不混同。

## 新反例与版本风险

额外分析了“右墙节点下有灯具，换破墙网格后想把灯移到侧室父对象”的场景。换网格引用本身不会自动重新布置灯或同步独立碰撞；删除节点和改变父级则是不同的结构操作。最终稿已用一处最小澄清处理此风险，无须扩展为工具教程。

另直接阅读了官方旧页：
https://docs.unity.cn/6000.0/Documentation/Manual/PrefabInstanceOverrides.html
它自标 Unity 6 Beta，覆盖类型附近说明不能重设继承对象父级或删除继承对象，可以停用替代。现 docs.unity.com 的 6000.0 Overrides/Variants 页则将 child GameObject 删除列入允许类型；新页未说明所有 reparent 情形。这是版本材料描述差异，不能用旧 Beta 限制替代现版本结论，亦不能从允许删除推出任意层级变更都允许。正文并未作这种承诺，修订后不存在此项事实错误。

补充直接核对 Unity 6.0 MeshFilter.sharedMesh 的 Remarks：
https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/meshfilter/sharedmesh
该文档警告底层共享网格改写可能影响所有使用者，支持区分装配继承与资源共享；本次没有执行其中示例代码。

## 实际读者任务与验证边界

仅凭全文，具备所述基础的读者可以针对侧室破口决定右墙的独立修改入口，制作保留两端的替换件，列出天花侧边、地板接缝与附着物的新增检查；可以识别 0.04 米铺装的高差；可以对 F0 内容更新与 F0→F1 字段更新给出不同的检查对象。核心做法没有藏在研究记录里。

本次通过针对说明性方案、图文一致性及已核对来源。未验证游戏内碰撞、导航、材质表现、导入刷新时机或生产效率；正文已将这些保留为实际交付验收工作。导航入口由独立导航审查负责，本报告不替代其结论。

## 审查版本

仅批准以下正文及图的实际字节，后续技术改动需重新审查受影响部分。

- GameLibrary/美术设计/环境设计/模块化环境/模块化环境的分件粒度与预制组合设计.md
  SHA-256：304c4cc60c240df0c14de8b6d9c379b7828897fa3ee84d982ad4c5d47c62e752
- GameLibrary/美术设计/环境设计/模块化环境/examples/modular-granularity-sections.svg
  SHA-256：57d7ac22b1d2dcd1688ea2329954167854b81e7cf7130df2f82678a3ea6ff822
- GameLibrary/美术设计/环境设计/模块化环境/examples/modular-granularity-dependencies.svg
  SHA-256：d6721eb1d653d7fd1c7475b3a1798213c0ff9335c7cd8ed1c1fc939706316512
- 管理档案/研究/TASK-2026-0310/sources.json
  SHA-256：c12bc874d2d62d3525f912b6f421f70c0f6f6ad7067fa88cfdd84389513cf740

- 管理档案/研究/TASK-2026-0310/sources.md
  SHA-256：c54c056139e40769f47f950d799403f9a448e566ad02299a50985e581fef8200

来源记录的 S4/S5 顺序及编号修正已实际复核，原段落内容不变，与 JSON 及正文参考编号一致。所有本轮实质审稿意见已解决。

## 图 1 排版调整的有限复核

2026-11-09，在完整审查之后，图 1 移除了下部横穿侧室的灰色水平注释引线。本审稿者对修改后的 SVG 重新渲染并实际看图，确认竖向虚线、文字、坐标、墙厚端面、侧室较高顶部及两侧同高地面均保留，断面含义未改变。此次仅复核这一排版改动及其视觉上下文，没有重复外部来源研究；正文、图 2 和两份来源记录未变。图 1 的最终 SHA-256 已更新于上表，技术通过结论保持。
