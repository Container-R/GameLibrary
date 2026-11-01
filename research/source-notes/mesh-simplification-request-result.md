# 网格简化请求与返回结果：目标比例不是资产验收回执

访问与核对日期：2026-11-01。本文仅核对 meshoptimizer 固定源码，并提出原创、未执行的接收示例；没有生成网格、运行简化器、观察画面或测量性能。

[glTF 属性与几何交接](../../solutions/modeling/gltf-interleaved-attribute-contract.md)关注数据解释和实际导入所得几何；[BC mip 预算](../../solutions/rendering/block-compressed-mip-budget.md)区分纹理 payload 与其他存储层次。它们都不能证明一次网格简化达到了请求比例或保留了所需外观。这里补充的是请求端到资产接收端的另一条边界。

## 固定版本与实际读取的合同

官方 meshoptimizer **v0.25** 对应提交 `6daea4695c48338363b08022d2fb15deaef6ac09`。普通 `meshopt_simplify` 返回实际索引数；拓扑与误差条件可能使它提前停止。输出仍引用原顶点，目标索引数不是目的缓冲区的容量保证：容量须覆盖原始 `index_count`。[头文件合同](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/meshoptimizer.h#L432-L448)

README 把误差描述为近似度量，而不是视觉通过证据。[Basic simplification](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/README.md#L431-L454) 本说明只讨论普通 API、`options = 0`、合法三角形列表和有限非零尺度；不混入 Sparse、绝对误差、属性加权、顶点更新或 permissive 变体。

| 源码定位 | 支持的有限结论 |
|---|---|
| [meshopt_simplifyEdge 主循环](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/simplifier.cpp#L2421-L2460) | 没有候选边或没有执行折叠时可结束；并非一直运行直到达到目标 |
| [performEdgeCollapses](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/simplifier.cpp#L1462-L1491) | 误差限制与折叠目标参与停止判断 |
| [返回及普通包装函数](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/simplifier.cpp#L2554-L2565) | 返回实际数量和换算后的误差；普通包装不提供属性误差输入 |
| [rescalePositions](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/simplifier.cpp#L546-L599)、[尺度调用位置](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/simplifier.cpp#L2301-L2341) | options 为零时按所提供顶点数组取最大轴向跨度，不是包围盒对角线，也不是自动只取被索引引用的顶点子集 |

这些分支不是完整算法证明。仅看到返回数量高于目标，不能唯一诊断为哪一条拓扑限制或哪一次误差判断所致。

## 两个请求，不能预填两个结果（原创、未执行）

假定同一个合法输入具有 **300 个索引，即 100 个三角形**。两次请求分别从同一原始输入开始，不串联简化；顶点数组、属性身份、索引、普通 API 与 options 都不变。

| 请求 | 目标索引数 | 相对 target_error | 目的缓冲区容量前提 | 实际结果 |
|---|---:|---:|---|---|
| A | 150 | 0.01 | 至少容纳原始 300 个索引 | 未执行，未知 |
| B | 75 | 0.01 | 至少容纳原始 300 个索引 | 未执行，未知 |

150 与 75 是索引数，不是顶点数。B 的请求更小，并不在此证明 B 必然返回更少索引。折叠是离散操作，接收时应检查实际数量是否满足声明的**上限**，不把目标值改写为精确相等要求。

若实际返回数超过目标上限，即使函数正常返回，也应记录“未达到请求预算”，而不是依据文件名或请求参数标为“减面成功”。反过来，即使数量满足上限，也只关闭了数量这一项，不能自动关闭外观、变形、材质和性能验收。

### 原创接收表

| 接收项 | 应读取什么 | 不能推断什么 |
|---|---|---|
| 实际减量 | 返回索引数、结果索引范围及引用的原顶点身份 | 不能用目标数替代返回数，在仍须保留相关属性差异时，也不能仅因坐标相同就合并顶点；有意舍弃不再需要的属性后重新索引属于另行明确的输入变更 |
| 误差合同 | result_error、选用 API／options、尺度及对应顶点数组 | 不能视为最大表面位移、屏幕像素误差或 UV／法线／蒙皮质量保证 |
| 存储交付 | 实际索引表示、仍保留的顶点数据及后续重排／压紧结果（若有） | 索引减少不自动减少已分配的顶点字节，更不证明 GPU 工作量或帧耗时下降 |
| 数量短缺后的决定 | 记录未达标；检查资产约束或重新协商目标 | 不能无声放宽误差、换算法或取消边界限制，再把改变后的合同当作原请求通过 |
| 外观与使用条件 | 项目另行定义的视角、材质、变形和下游使用验收 | 本文没有提供这些检查的实测结果或通用通过阈值 |

## 误差单位也需要绑定输入

[`meshopt_simplifyScale` 合同](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/meshoptimizer.h#L540-L546)规定：绝对量除以尺度转为相对输入，返回相对误差乘以尺度转回模型单位；[实现](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/simplifier.cpp#L2870-L2879)返回上述最大轴向跨度。

**纯算术例子：**假设尺度分别为 2 和 20，某个相对度量值为 0.01，则乘积分别是 0.02 和 0.2 模型单位。没有资产单位约定就不能称作米；没有运行与独立几何比较就不能称作测得偏移，更不能称作最大视觉误差界。

尺度必须来自同一份所提供的顶点数据。在本例 options 为零的条件下，不能擅自只对引用子集算尺度。零尺度不能用于上述除法；Sparse、绝对误差或属性加权模式需另建单位合同，不能沿用此例或重复换算。

## 适用边界

本说明没有证明任一未知网格的返回数量、误差或停止原因，也没有推荐通用减面比例。目标变小、函数正常返回、索引上限达标与最终资产可接受是四件不同的事。后续若要声称某项实际资产通过，应提交对应输入、返回数据和项目验收证据，而不是把本次源码阅读或关联文章的导入证据充当简化测试。
