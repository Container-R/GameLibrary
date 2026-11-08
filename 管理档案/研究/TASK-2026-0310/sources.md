# 来源与阅读范围

## S1：Bethesda 制作团队的粒度案例
Joel Burgess、Nate Purkeypile，The Modular Level Design of Fallout 4，GDC 2016，作者上传。
https://www.slideshare.net/slideshow/gdc-2016-modular-level-design-of-fallout-4/59770460
定向读取原课件文字第 69–99 页，非页面 AI 摘要。已取得并实际查看 86、88、94、96、99 页，图片仅本地研究，不拟随稿转载。
- 86：墙、转角、地板、天花被分离标示。
- 88：列出拆分与破坏、互换、布局自由度之间的联系。
- 94：同一展示标注旧方案 20、新方案 123 对象；只能说明这张例子的对象数，不能作为工时或性能数据。
- 96：并列 Pack-In Prefab 与 Exploded Granular。
- 99：区分核心套件可用和后续布局可靠的时点。
原图地址模式：https://image.slidesharecdn.com/gdc16modularldfallout4-160319181438/85/GDC-2016-Modular-Level-Design-of-Fallout-4-86-320.jpg （替换页号即可对应本次已取五页）。没有声称看完整讲座。

## S2：共同制作与原型阶段
Joel Burgess、Nathan Purkeypile，Skyrim's Modular Approach to Level Design，GDC 2013；2013-05-01 作者署名转载。
https://www.gamedeveloper.com/design/skyrim-s-modular-approach-to-level-design
重读 Proof、Level Designer sidebar、Graybox、Build-Out、Polish 的文字。关键定位：正文对应章节。支持灰盒应暴露真实结构约束、跨件视觉元素不能一直占位省略、常用件先行及新增件需有用途判断。其回接论证已被 SOL-ENV-001 吸收，不再新增同题。此轮不重新评价 Skyrim 图片视觉表现。

## S3：Unity 实例覆盖
Unity 6.0 Manual，Override prefab instances，Behavior of overrides。
https://docs.unity.com/en-us/engine/6000.0/manual/working-with-gameobjects/prefabs/override/prefab-instance-overrides
原 6000.0 文档 URL 重定向到该版本页面。文字支持同字段覆盖优先、源值修改不会作用于已覆盖字段。仅作为具体实现例，不等同 Fallout 4 Pack-In。

## S4：解包与依赖边界
Unity 6.0 Manual，Revert a prefab instance to a GameObject。
https://docs.unity.com/en-us/engine/6000.0/manual/working-with-gameobjects/prefabs/unpacking-prefab-instances
全文技术段。普通解包解除所选层链接但保留嵌套实例；完全解包进一步解除嵌套。解包不是“不再引用任何网格或材质”，文档没有支持这种说法。

## S5：变体的定位
Unity 6.0 Manual，Create variations of prefabs。
https://docs.unity.com/en-us/engine/6000.0/manual/working-with-gameobjects/prefabs/prefab-variants
技术文字：变体继承基础预制，覆盖优先，基础也可为其他变体。这里用于区分“可重复例外”与“任意散件”，不展开应用目标按钮教程。

以上网页于2026-11-08本轮研究时读取。无原生 DCC/引擎测试，无玩家或效率实验。全部公开来源只适度摘要，不转载课件。
