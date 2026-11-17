# Godot 无头合成输入复现

运行 `godot --headless --path . --script main.gd`。在引擎真实物理回调中，测试驱动通过 Input.parse_input_event 和 flush_buffered_events 向 Node._input 提供合成 InputEventAction，不直接调用规则入口模拟输入。逻辑是已发表教学合同的 GDScript 子集，试件观察回调交付、窗口首步的攻击启动以及同一步打断优先。步 5 观察到已拒 ID 再投递，但即使它被错误地重新入队，也会在下一次窗口首步前的到期检查中被清掉；当前断言不能单独验证它没有重新入队。事件的 tick 与 ID 由试件显式设定；不测硬件、设备映射、画面、方法轨、真实玩家手感或游戏实现。

版本自报 Godot 4.6.3.stable.official.7d41c59c4；执行文件 SHA-256 f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3；未认证发行字节来源或与固定源码的构建关系。正常输出见 output.txt（exit 0）；将 rules 的 `if interrupt:` 改为 `if false and interrupt:`，其余原样，可看见第二击错误启动、测试 exit 1（mutation-output.txt）。
