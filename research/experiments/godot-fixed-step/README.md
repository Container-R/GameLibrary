# Godot 4.6.3 固定回调边界：真实引擎无头夹具

## 范围与运行

本夹具为原创，补充 SOL-PROG-001，不是新引擎物理确定性基准。运行：

```sh
python run.py
```

禁止使用 `python -O`：运行器在执行测试前显式拒绝优化模式，实际拒绝记录见 `results/optimized-rejection.txt`，防止assert被跳过。

要求 PATH 内已有 `godot` 和 Python 标准库；不安装依赖、不下载代码。运行器在 `/tmp/gamelibrary-godot-*` 下建立 HOME、XDG_CACHE_HOME、XDG_DATA_HOME、XDG_CONFIG_HOME，用户数据/字体缓存不会写到默认只读 HOME。Godot 的项目解析和运行均为实际进程，不是 Python 模拟。进程超时20秒、非零退出、stderr、ERROR、结果缺失或判据不符均使运行器失败。重新运行会替换 `results/` 中的运行输出；启动先移除旧summary，只有全部检查成功才写新summary，失败时零散日志不可当整批通过。`results/` 保存每个进程的原始日志、逐回调 JSON、引擎版本、实际配置、命令、墙钟耗时、源文件 SHA256 和汇总。

首次探测命令在重定向 HOME 前出现字体缓存不可写提示；未作为正式测试结果。归档的正式运行全部使用隔离目录且 stderr 为空。

## 原创负载与独立判据

- 单 Node、单线程场景、60 physics ticks/s、max_physics_steps_per_frame=8、physics_jitter_fix=0、time_scale=1；不使用额外累加器。
- `_physics_process` 唯一推进整数核心；tick0/30/90分别设置轴值1/-1/0；120 ticks最终 x=-30。
- tick6/8/9分别提供一次预先编号的攻击边沿，半开有效窗口[6,9)，预期事件严格为[6,8]。
- `_process` 只计算前后整数快照的数值插值与诊断，断言它没有修改 tick/x/axis/previous_x/events。没有实际图形绘制，不能称为视觉质量验证。
- Python 独立计算完整120 tick状态和事件序列，与每个Godot进程逐项比较；不只比较终态哈希。每次引擎回调delta也须为1/60，物理步计数与各主帧步数总和都须为120；逐帧tick增量等于steps。另检查30上限/人工组实际出现多步，144组实际出现零步，并将每帧插值数值与独立轨迹公式比较。

## 两种参数不可混淆

`--fixed-fps N` 禁用实时同步，给主循环人工固定时间推进。本测试在约0.2秒墙钟内完成约2秒游戏时间，**不是测得显示器以N Hz工作，也不是实时压力测试**。运行器另外验证每次 `_process` delta≈1/N。

`--max-fps N` 是主帧速率上限而非准确计时器。本次无头实际执行约2秒，启动与调度抖动使回调数不同；不能把“设置144”说成设备稳定渲染144 FPS。各组在第120个规则tick结束，因此比较同一模拟终点，不比较相同墙钟位置。人工144组的289次主回调包含到达终止tick的回调边界；并不承诺一定恰好288次。记录中的额外无固定步主帧是实际观测，不能硬编码成跨平台保证。

## 正式运行结果（2026-10-31）

引擎 `4.6.3.stable.official.7d41c59c4`；环境 `Linux-6.18.57-x86_64-with-glibc2.41`；Python `3.12.14`。本表为集成复核加强守卫后独立重跑的6个进程，均退出0、检查通过。`author-run-summary.json`保留加强前作者运行的历史摘要，其源码哈希对应此前夹具，不与当前源文件混淆。

| 参数 | 主回调数 | 固定回调数 | 每主回调固定步直方图 | 进程墙钟秒 |
|---|---:|---:|---|---:|
| fixed-fps-30 | 60 | 120 | `{'2': 60}` | 0.2706 |
| fixed-fps-60 | 120 | 120 | `{'1': 120}` | 0.2678 |
| fixed-fps-144 | 289 | 120 | `{'0': 169, '1': 120}` | 0.2796 |
| max-fps-30 | 63 | 120 | `{'0': 3, '2': 60}` | 2.2226 |
| max-fps-60 | 123 | 120 | `{'0': 3, '1': 120}` | 2.2163 |
| max-fps-144 | 290 | 120 | `{'0': 170, '1': 120}` | 2.2153 |

六组完整状态序列 SHA256 相同：`db519adc4374bf18ba72ac2da4fa0e2c12fdebad5d87d0807f0eec6b9b404267`。正式原始计数以 `results/summary.json` 和逐运行JSON为准；重跑的实时计数与耗时可能不同。

## 证据强度与未覆盖项

已建立的是：**这个Godot二进制、配置、原始夹具与规范化命令日志下，不同主帧安排没有改变120个整数规则步骤及事件消费；表现计算未反写核心。** 属于真实引擎回调集成证据，不再只是引擎外模型。

未覆盖：设备输入采样与事件到tick映射、场景暂停/失焦、真实卡顿或持续过载、引擎物理碰撞/浮点求解、Root Motion、GPU/显示器/视觉插值、Unity、不同Godot构建或跨平台确定性。没有做stall实验，也不能推导Godot采取原文Python示例的“保留全部欠账”策略。文章整体仍应保留source-backed，有限执行结果单独标明。

## 官方依据（访问2026-10-31）

- [Godot4.6 Idle and Physics Processing](https://docs.godotengine.org/en/4.6/tutorials/scripting/idle_and_physics_processing.html)：固定与主帧回调的职责、默认固定频率和单线程中的先后关系。夹具未复制其示例代码。
- [Godot4.6 Command line tutorial / Command line reference](https://docs.godotengine.org/en/4.6/tutorials/editor/command_line_tutorial.html)：headless、single-threaded-scene、fixed-fps禁用实时同步、max-fps上限；另与本机4.6.3 `--help` 核对，短摘录见results/cli-help.txt。
- [Godot4.6 Engine](https://docs.godotengine.org/en/4.6/classes/class_engine.html)：实际配置属性及插值fraction API入口。本文只用它做数值只读表现，不宣称验证引擎自动节点插值。

文档版本4.6与实际二进制4.6.3分别记录，不将滚动文档当作该二进制源码审计。
