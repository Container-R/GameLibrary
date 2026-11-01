# 主审原始来源核对

2026-11-01。候选范围为 TLOU2 历史混合探针表示的内容适用条件，非实现复现。

## 实际阅读

- Naughty Dog 官方公告 `https://www.naughtydog.com/blog/naughty_dog_at_siggraph_2020`：标题、2021-02-11 日期、署名 Hawar Doghramachi 的光照条目及官方 PowerPoint 链接。公告日期不代替 SIGGRAPH 2020 演讲日期。
- SIGGRAPH 历史档案两页作者文献 `https://history.siggraph.org/wp-content/uploads/2022/08/2020-Talks-Doghramachi_Lighting-Technology-of-The-Last-of-Us-Part-II.pdf`：全文文字，重点第2页 §3 和 §6；未检查图片。文献标注 SIGGRAPH ’20 Talks、2020-08-17，DOI 10.1145/3388767.3407358。
- 工作室直链 `https://s3.amazonaws.com/nd.images/research/2020_siggraph/LightingTechTlou2.pptx`：原始文档 SHA-256 `f2ceec1821ef3855f87b2a6532cf9a11bfc4abd8a0814eb81d567004cb04b283`，64页。主审读取第3、5、16–20、48–50页抽取文字与作者注释，并独立核对 OOXML presentation 顺序及第5、48、49、50页 slide/notes 关系。未观看视频、检查截图或通读全套幻灯片。
- 既有 `roles/rendering/game-lighting-artist.md` 全文：共享灯具实例/预设/场景修改责任，而非本候选的分量空间表示问题。未读取或继承运行归档证据。

## 可支持的限定

§3 与第16–20页区分对象角点插值数据与每像素查询。第48–49页说明基于主要阴天内容的分量变化差异而采用混合存储。顶点承载 ambient base 与 dominant light 的 luminance，方向来自探针；第5、49页的方向提取和 SH masking 依赖不能从讨论中抹去。第50页注释将演示色度变化与主要内容区分，是作者陈述而非本库视觉验收。

假设长墙的窄色度过渡仅是原创接收问题。增加顶点亮度采样并未直接添加探针色度采样位置，不能单凭亮度表现批准该要求；这不等于证明指定墙面失败或任何加密完全无效。来源不足以给出其结果、误差界、密度阈值或新项目预算。

不据此继承性能、玩家、图像或引擎运行验证。不将原始 PPTX、抽取全文或来源图片提交仓库。最终正文及独立审查待核对后记录。

## 最终正文接收

全文核对 `article.md` SHA-256 `c8f08c70665b3a59733f6b75d7449bf8b28ab25c80054d9d093eeb4e2c7d5052`。预发表纠正了将几何笼统列为固定条件而又改变顶点密度的表述：最终方案固定接收表面形状，明确拓扑是 RL 中可能的有意变量，并检查法线插值联动。R0/RL 与 R0/RC 均为未执行隔离设计；探针颜色和方向不能分离时不得作单因素归因。

主审接受其有限历史案例用途：比旧角色篇新增了具体表示约束与内容适用条件，但不提升为运行验证、完整实现教程或全面光照覆盖。独立复核记录应绑定这一最终哈希。
