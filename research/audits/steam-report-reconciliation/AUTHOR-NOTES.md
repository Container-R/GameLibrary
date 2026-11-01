# 作者说明：Steam流量报表对账

2026-11-01。拟发布位置：`research/source-notes/steam-report-reconciliation.md`。仅新来源笔记；不更改既有文章、不新增岗位。正文最终内容仍待独立审查。

## 来源与读取范围

两页均为Valve公开英文滚动文档，读取日期2026-11-01，无固定发布版本或统一修订日期：

- https://partner.steamgames.com/doc/marketing/traffic_reporting?l=english ：完整文字正文，重点 Accessing Reports、Visits、Notes on Data collection date ranges；本次提取365–394行。
- https://partner.steamgames.com/doc/marketing/utm_analytics?l=english ：正文及FAQ已读，正文采用的定位仅 Privacy、Discrepancies Between UTM Analytics and Traffic Breakdown、Testing a link；本次提取369–375、437–439、460–466行。

正文保留两段短来源概括；本说明不重复事实摘要。未观看视频、分析截图、访问账户或提取报表。页内单项功能或收集起始日期不冒充全文修订日期。

## 原创部分与范围收缩

初始候选门中宽泛归因、跨设备路径与10次购买的反事实例子均未纳入最终正文。采用两组微型有限集合，分别给出负差和正差；共同计数单位是为了隔离数学问题的额外假设，不是对Steam报表已成立的判断。T\U也不自动等于实际未带参数的访问；即便后者已知，也仍不能据此判为自然来源。没有估计交集、隐藏数量或补全算法。

接收表是原创建议，不是Valve要求的内部字段格式；提取时点与转化成熟条件分别处理。链接只关联既有素材交接及分母概念，不继承其测试。正文使用拟发布路径下的相对链接。

## 精确文件绑定

- `note.md` 完整UTF-8文件SHA256：`d04fb350402ea71ce6b5e2bcd96f34df8e0c57a922f8827f054fa38703ff0da2`。
- 正文SHA256（去除首个YAML frontmatter及其结束分隔行，保留其后原始字节）：`417cfce59b4a25435fc6e2715e467cd7a515f0539b29f2598b85865bde0ac0e7`。
