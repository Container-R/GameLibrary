# Unity 输入包回移兼容：来源核对

- [正式正文](../../GameLibrary/玩法程序/玩法系统/输入接入/Unity%202022.3%20要用新版%20Input%20System%20的修复，能只移植输入包吗？.md)；[回归试件与边界](../实验/Unity输入包的复合绑定组/README.md)。
- 2022.3 UPM 手册的 [package.json 版本下限](https://docs.unity3d.com/2022.3/Documentation/Manual/upm-manifestPkg.html#unity) 和 [嵌入包章节](https://docs.unity3d.com/2022.3/Documentation/Manual/upm-embed.html#embed-cached)：区分项目请求、包声明及实际解析；嵌入包覆盖缓存中的同名包。未通过本机 UPM 实测注册表可用性。
- Unity Input System 的固定源码：1.19.0 `ca8d898356596a91bda6505e506cc1a4bb3a9fa6` 的 `package.json` 声明 2022.3；1.20.0 `27757ebb14c0659ce1dbe39822ce97b33adea6c9` 与 1.20.1 `a934411756c8862cb0f54da514a9b7cc1c000a2b` 均声明 6000.0，三份均未设置 `unityRelease`。正文来源 2–3 链到确切文件。
- UUM-141423：实际对比三参数组掩码重载及 1.19 的 `InputBinding.Matches` 特别是组字段。旧实现跳过所有部件；新实现只扫描同根连续部件，匹配后仍调用旧的按根索引显示。核对过 1.19 `CompositeSyntax.With` 的 `groups` 参数和索引重载；现在有正例、无关组和相邻根反例。这不改变输入采集，也不宣称一切组掩码只按组字段匹配。
- 原生边界：1.19 `NativeInputRuntime.DeviceCommand` 转给 2022.3 C# 参考源码中的 `extern IOCTL`；参考源码声明不是原生实现。1.20.0 `Unity.InputSystem.asmdef` 声明两道不同的版本门槛：`6000.4.0a4` 的鼠标脚本事件和 `6000.5.0a8` 的焦点事件；`FinalizeUpdate` 显式不为 Editor 更新转发 `DoSendMouseEvents`。故障适用范围来自 1.20.0 CHANGELOG，未在 2022.3 重现同一故障。
- 包的许可与 2022.3 引擎托管层参考源码的许可不同。本文只链接，试件不复制引擎源码。
