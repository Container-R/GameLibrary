# 均匀网格最近命中：独立来源与正文审查

2026-11-01。**接受最终稿，未发现实质阻断问题。** 本审查者没有起草本次门或文章；独立打开决定性原文并手算原始几何。没有运行求交、编译渲染器、生成资产或读取关联运行档案。

## 精确验收对象

- `article.md` SHA-256 `da1e8e8de357dc6ad5b30320e1f2632d0eed9e066467e0f1c4f5de86ddc2ee56`，全文。
- `AUTHOR-NOTES.md` SHA-256 `33e63c069dada74e3ff3a7687afa0243818cbfde4da66005ed849c6c63011722`，全文。
- 前置读取本次 independent-gate.md 与 main-read.md；它们不是原始来源的替代。

## 独立实际阅读定位

- [PBRT 第二版原始章 PDF](https://www.pbrt.org/chapters/pbrt-2ed-chap4.pdf)：物理4/23/25页、印刷186/205/207页的文本。未进行本审查者的页图检查；不据此声称观察图形。
- 作者仓库固定 `e6f6334f3c26ca29eba2b27af4e60fec9fdc7a8d`：[grid.cpp](https://github.com/mmp/pbrt-v2/blob/e6f6334f3c26ca29eba2b27af4e60fec9fdc7a8d/src/accelerators/grid.cpp) 构造赋表、Intersect 与候选/IntersectP 路径；[primitive.cpp](https://github.com/mmp/pbrt-v2/blob/e6f6334f3c26ca29eba2b27af4e60fec9fdc7a8d/src/core/primitive.cpp) GeometricPrimitive::Intersect；[trianglemesh.cpp 127–160](https://github.com/mmp/pbrt-v2/blob/e6f6334f3c26ca29eba2b27af4e60fec9fdc7a8d/src/shapes/trianglemesh.cpp#L127-L160) 参数范围检查。它们闭合本文采用的候选上界与跨格停止链，不认证完整实现。
- [NVIDIA 原始 Chapter 22](https://developer.nvidia.com/gpugems/gpugems3/part-iv-image-effects/chapter-22-baking-normal-maps-gpu)：22.1.1、22.2.1–22.2.2、22.3、22.4.1 文字。确认最近投射目标及网页明示省略辅助函数；未复核配套包目录，未查看图片。有关目录检查只作为主研究记录，不冒充我的独立获取。正文未据此指控应用 bug，边界正确。

书文和源码事实集中在文章；此处不重复其整段摘要。

## 原创几何与停止论证的对抗检查

A 的三个顶点均满足 `y=1−x/5`；与射线的平面交点 x=5/2，且为三正权重的重心，所以不是平面交点落在三角形外的假阳性。第一格的内部见证 `(4/5,21/25,1/2)` 由正权重组成，确实在格内。B 的权重 `(1/4,1/4,1/2)` 给出 y=z=1/2；其 x=3/2 与第一格分离。减去射线起点 x=1/4 后得到 A 的9/4、B的5/4；边界参数3/4、7/4均正确。

两枚图元绕序不应被默认为同向。最终稿已显式使用双面、无背面剔除、不透明且无遮罩的求交前提；因此没有把本反例套进未知烘焙器的单面政策。网格为原创单位格，不是 PBRT 自动构造结果；射线起点也未冒充实际 cage 数据。

停止依据需要已访问区间对应列表不漏图元、候选处理完整及单调遍历共同成立。最终稿没有以列表完整性代替最近候选维护，也没有以有序访问单独推出最近命中。`t_best<t_next` 作为严格充分条件有效；等距身份选择、边界归属与浮点处理明确留给另行合同，不误写为通用等号禁令或完整 DDA 正确性证明。

只保留 A 的提案暴露了区间丢弃加一次性去重的组合风险；不批评所有缓存。上限1排除两交点、任意命中不要求B、调换候选顺序不应改变唯一最近结果，均与原创场景一致，但全部是未执行预期。未执行有限例子也不为性能或最终 normal-map 提供证据。

## 接收结论

文章的增量是具体 nearest-hit/any-hit 停止合同，不是未经证实的软件缺陷报告。来源边界、原创推导、成本讨论及有限接收提案清楚，相关旧研究没有被当作本次验证。作者说明保留不可用来源和不同阅读者的范围，不把未取得着色器补成完整实现。接受上述两个精确文件版本；不扩展为渲染正确性认证。

## 归档绑定增补

随后读取作者说明追加的文稿绑定段，当前 `AUTHOR-NOTES.md` SHA-256 `ff920eff61f20a5d6f5890d2d7db349faaf118f4e054dbeaaacf86c5b8eab783`，接受这一记录增补。article.md 未变；独立复算去除 YAML 及结束分隔行、保留随后原始字节的正文 SHA-256 为 `afb6416aec2c7ff47e18bb822f0ac39a8b4a598dbf5c962b8e46d1949a449b8f`，与记录一致。主研究页图阅读没有转记为作者或本审查者阅读。
