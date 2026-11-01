# Valve 情境对白规则选择：来源与读取范围

核对日期：2026-11-01。对应[CASE-NARR-002 历史正文](https://github.com/Container-R/GameLibrary/blob/d0c87c1985778a6956374624b9b5e3c6ddbfd7cb/case-studies/narrative/valve-contextual-dialogue-rule-selection.md)；当前读者正文见[Valve如何根据游戏情境选择对白](../../../GameLibrary/叙事设计/运行时叙事/情境对白/Valve如何根据游戏情境选择对白.md)。本记录不重复案例的来源概括；规则和事实名字、三行推导及接收建议均为本库原创未执行分析。

## 唯一内容主源

Elan Ruskin，*Rule Databases for Contextual Dialog and Game Logic*，Game Developers Conference，2012 年 3 月。[Valve 官方 publications 的 2012 条目](https://www.valvesoftware.com/en/publications)确认作者、月份、标题和幻灯片入口。具体日期及 PDF 修订日期未知；这是历史演讲资料，不是当前 Source API 文档。

[官方 PDF](https://cdn.fastly.steamstatic.com/apps/valve/2012/GDC2012_Ruskin_Elan_DynamicDialog.pdf) 共 143 个物理页，本次取得文件 SHA-256：`b78f5d89f5b47eee49ae01f3f5e4a269eff9670746d40001b437e5c2547ac436`。该摘要指认所读公开文件，不证明当前引擎与它对应。

## 精确定位

以下均为从 1 开始的物理 PDF 页码；括号内为需要区分的印刷页码。

| 位置 | 本案例使用范围 |
|---|---|
| 48–49 | query、criterion、rule、response 的基本关系 |
| 54–59，尤其 57 | 当前事实与角色历史进入 query |
| 62（63）、64（65） | 先拒绝不满足或缺失事实的规则，再比较匹配规则的条件计数 |
| 65（66） | 同一 response 内的表达变体，不等同于平行规则 |
| 67–69（68–70） | 历史条件、写回与后续询问；未据此建立音频完成事务保证 |

起草者读取了选定页的文字及作者注释：35–36、48–70；不是通读全套或观看演讲。主审另读相关段落，并视觉核对物理页 62、64、77；这种图文核对没有产生游戏或听觉实测证据。正文只采用上表所列的选择机制，不引入演讲的性能评论。

## 访问与再利用边界

网页阅读器因文件体积限制未展开 PDF，随后通过正常公开下载取得文件并抽取文字；没有绕过登录或访问限制。整份 PDF、抽取全文、幻灯片图片及游戏对白均不随案例转载。本文仅给出处、限定阅读范围，并以短篇释义和原创分析说明用途。

DOOM 演讲正文不可读的研究门仍独立暂缓；本来源不是其实现的替代证据。既有 ink 宿主调用与存档说明也不为这里的规则计数背书。
