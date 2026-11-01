# glTF sparse accessor 来源与证据分层

- 作者/机构：Khronos 3D Formats Working Group。
- 固定来源：[glTF 2.0 Specification.adoc](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc)，commit `59ecbdba704206bb656965ab4e202881806066f1`，源提交日期2026-10-30；本轮读取2026-11-01。
- 定位：Accessor Element Sources；Sparse Accessors Overview、Indices、Values、Usage；JSON Encoding整数值规则。网页折行与原始源码行号不同，以固定commit和章节锚点为定位基准。GitHub网页一次重开cache miss，raw固定源成功；没有以失败页面充作已读证据。
- 同源schema用于字段复核，不是第二个独立规范或实际导入结果。

规范支持基底与替换顺序、严格递增且受count约束的目的索引、独立view跨度/对齐以及紧密排列的稀疏载荷。这里用原创44字节、两种基底和五个错误输入把这些要求转成有限可执行判据。未复制官方示例、第三方资产或整段规范正文。

元数据整数值可有小数/指数写法；本实验明确选更窄的strict-int Python策略，不把拒绝该编码误报为格式非法。此新增证据不继承原160字节网格的Godot导入结果；没有运行引擎、DCC、官方validator、GPU或morph动画。实验预期和字面地址在作者实现及执行前冻结；代码审查前发现的负例URI不一致已修正并留存初稿，没有发生结果后修改预期。
