# Niagara 成本拆分：读者视角审读

2026-11-01。技术内容与旧范围处置可接受；已向主编提出首次缩写与 p99 释义的小修，最终字节待下方差异闭合。未执行 Unreal 或采集性能数据，不以本报告代替真实项目测量。

## 初稿绑定

- 新 book.md：`a2d16d550585b980acd6c8079478ec849da290da523dbda4bf220208257ef68d`
- scope-disposition.md：`027a657bfbd37657264756779cde904d936aca25433e269e8a855a04ceb5ec64`
- 完整阅读 batch16 旧 solutions/vfx/niagara-performance-budget.md：`5c7a4a3d6fa9a10aa5891803928340418c67d2402446ecef2fa046e0ebce5a8e`。

未参与此次新正文写作。本次全文对照后实际重新打开六个 Epic 原源的相关正文；没有读运行档案或采用私人执行记录。

## 读者主线与技术判断

烟雾从独立播放到战斗集中出现、再到近镜头的例子明确为虚构，能够引出不同工作来源。先解释 System/Emitter/实例，然后固定场景、拆比较、检查 bounds、保留玩法提示、判断结果，读者能复述为什么不能只选“粒子阶段最快”的版本。

下列重要限制均实际保留：

- 多小/少大先固定可见负载，再恢复真实分布检查剔除；并未把组织成本优势普遍化。
- 关绘制器必须确认模拟、数量、生命周期及范围不变；否则差值不是纯绘制成本。
- CPU/GPU 比较考虑等价功能、双方余量、内存和响应，不只比较一个阶段。
- 近镜头/透明叠层与模拟成本分开；改分辨率同时影响其他全屏阶段，需在时间线定位。
- 固定 bounds 有更新成本优势与剔除损失权衡；全寿命、附着运动、随机极值、离屏重入和恢复不能省略。
- 关键提示按玩法意义而非距离决定；错峰不等于工作免费消失，不得延后必须即时出现的信息。
- GT/RT 不与 GPU 时间混同；调试读回与具名追踪有开销；复杂度颜色不是毫秒。
- 并行计时不能简单相加；交错重复比较、不挑最佳值；从相应帧样本计算汇总分位数，不平均各次 p99；变化落在测量波动内不能声称获益。

初稿两处影响跨工种理解：开头 GPU 未释义，末节 p99 未解释含义。已建议分别写图形处理器（GPU）、帧时间第99百分位数（p99，用于观察较慢一端），并将首次 UE 展开为 Unreal Engine（UE）。这不是追加统计教程或新指标，也不改变实验证据范围。

## 实际原源复核位置

均为新正文末尾的原链接。页面标题明确前四项5.6、后两项5.8，未以URL参数冒充版本验证；没有运行相应版本。

1. [Scalability and Best Practices](https://dev.epicgames.com/documentation/en-us/unreal-engine/scalability-and-best-practices-for-niagara?application_version=5.6)：8–27实例/发射器，44–53模拟目标与bounds，60–75预热/生成；保留文中旧版本前瞻的警告，没有推定当前成熟度。
2. [Niagara Debugger](https://dev.epicgames.com/documentation/en-us/unreal-engine/niagara-debugger-for-unreal-engine?application_version=5.6)：63–95显示对象，124–150范围与GPU读回，274及324–332性能视图。读取文字，不以示例图推性能。
3. [Effect Type Budgeting](https://dev.epicgames.com/documentation/en-us/unreal-engine/performance-budgeting-using-effect-types-in-niagara-for-unreal-engine?application_version=5.6)：全文5–28，集中配置与距离/数量预算。它不替内容负责人决定提示能否丢失。
4. [Performance Profiling Introduction](https://dev.epicgames.com/documentation/en-us/unreal-engine/introduction-to-performance-profiling-and-configuration-in-unreal-engine?application_version=5.6)：3–44帧时间和瓶颈、67–115测量工具及开销；没有采用其示意为本项目保证。
5. [Measuring Performance](https://dev.epicgames.com/documentation/en-us/unreal-engine/measuring-performance-in-niagara)：13–47代表性场景、具名开销与计时，110–130复杂度视图。页面5.8，不要求5.6所有工具相同，不复制官方实验数字。
6. [UNiagaraEffectType](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Plugins/Niagara/UNiagaraEffectType)：2–10用途、61–66相对重要性；页面5.8，不将其字段当作项目5.6分支的实测。

## 旧范围处置

旧六类成本、A–F比较、完整bounds与质量分级、记录要求和候选接受条件均已融入正文；scope逐项说明与实际正文相符。没有需要另建书承接的独有代码或测量结果。删除发现词、研究标签和泛邻题链接不损技术主线；旧文并无已执行实验，不存在将实测偷偷改成纸上建议的问题。

这是内容审读，不是新书架/返回导航验收。没有修改作者稿、stage 或远端；最终小修另行读差异绑定。

## 最终小修闭合

实际读取 `book.before-review.md` 与当前正文的完整差异：仅首次 GPU、UE 展开，以及 p99 的第99百分位释义和“各运行自身p99”措辞，其他正文未变。三处修改解决上述读者问题，没有扩大方法或执行声称。

**最终接受 book.md SHA-256：`7dc68392192d0fca10d2f44c2b286d17970392436b1533b9d13c133a9cf97dfe`。** 初稿 a2d16… 保留为审读历史；scope 中该哈希亦属初稿记录，最终绑定以本段为准。旧范围内容处置仍可接受，不能据此宣称真实优化已完成。
