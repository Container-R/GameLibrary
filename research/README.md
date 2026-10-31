# 研究记录与可复核证据

任务以 [队列](../.agent/queue.json) 和 [恢复状态](../.agent/state.json) 为准；草稿、来源审计、模型测试和实际运行证据不混称为完整生产验证。成熟知识见 [CATALOG](../CATALOG.md)。

## 原创 Python 模型

```sh
python3 scripts/run_model_tests.py
```

运行前审阅代码。标准库模型无依赖安装或网络请求；每个 `research/experiments/*/test_*.py` 独立进程执行，任一失败或未找到测试均返回非零。日志文件是记录时的输出，不会被该入口自动更新。通过不证明引擎、设备、声音、网络或平台集成；其中存档在途写反例断言的是限制，而非保护成功。

[有种子的深度对抗实验](experiments/deep-model-qa/README.md)单独执行，保留独立判据、模型哈希与故障变异结果；增加种子数不等于增加真实平台覆盖。

## 实际 Godot 引擎证据

以下夹具需要本机已有 Godot，不由纯 Python 模型入口自动触发。各自记录二进制、源哈希和执行边界；其运行器可能替换自己的 results，应先保留需要的历史输出。

- [固定规则与表现回调](experiments/godot-fixed-step/README.md)：6 组实际进程；人工 `fixed-fps` 与实时 `max-fps` 分开，不证明设备输入、GPU 或物理确定性。
- [暂停与合成输入队列](experiments/godot-pause-input/README.md)：实际输入 API 分发与常驻应用队列反例；固定心跳排除空洞暂停观察，不是物理设备测试。
- [焦点恢复的实例身份](experiments/godot-focus-boundary/README.md)：实际 Viewport owner、信号和延迟调用；不是 Unity、视觉或完整模态输入墙验收。
- [干净检出后的资产导入](experiments/godot-import-boundary/README.md)：遗漏 sidecar 时仍可加载、UID 相同但纹理尺寸不同；[工程契约](../solutions/engine/asset-import-intent-contract.md)区分源文件、导入意图与生成缓存。

## 实际文件系统反例

[Linux/tmpfs 路径替换](experiments/filesystem-save-publication/README.md)：完整旧版本仍可覆盖已发布的新版本；安排好的预调用重检查仅是有限对照，不是 CAS、持久性或 Steam 验证。

## 固定版本来源审计：没有运行时执行

- [ink v1.2.1 宿主边界](source-notes/ink-v1.2.1-host-boundary.md)：General 与便捷重载默认纯度不同；状态格式不等于项目内容或宿主检查点身份。没有 C# 运行证据，不作为成熟叙事文章计入索引。
- [音频来源深度审查](audits/audio-source-depth-review.md)：固定 Wwise 历史提交与 FMOD 启动失败回调边界。

## 审查与分类历史

[初始七篇覆盖快照](audits/initial-coverage-and-taxonomy.md)不是实时完成率；其后 ACCESS 兼容拆分见 [分类说明](../taxonomy/README.md)。[存档草稿对抗审查](audits/cloud-save-adversarial-review.md)保留发布前失败和修复回归。各实际夹具的独立复核记录在其 README 中定位，同一机器的重复验证不冒称跨平台复现。
