# 步态混合落脚通知：复现材料

Python 3.12.14（标准库），Godot 4.7.2.stable.official.ed1daf0bf，2026-11-23。

```sh
python3 contact_model.py
godot --headless --path native --script measure.gd
```

在禁止写用户目录的环境，先为 XDG_DATA_HOME、XDG_CACHE_HOME、XDG_CONFIG_HOME 指定可写目录。原生项目生成两段 1 秒动画，各带一个方法键，不播放声音、不创建可视角色。手动每次推进 10 ms；混合斜坡于名义 400–600 ms 从全走路到全跑步。实测 CSV 的 `advance_to_ms` 是试件记录的推进帧标签，`key_ms` 是动画本地时间，不应混为一谈。单分支为控制组；稳态半混、一致键与错开键为观察组。保存的原始输出在 [native-observed.txt](native-observed.txt)。

同步开启时，500/500 的两个方法键同在帧 510、跑步权重 0.55 调用；480/520 时分别在帧 490、530 调用，对换键早晚也有两个回调。本试件同步关闭后跑步分支的回调延后，延长到 1100 ms 才能看清，不能把 700 ms 内没有出现误判为永久抑制。方法回调不是听感，未测混音、实际脚位、引擎间等价或游戏表现。

Python 试件独立比较自拟的主导片段规则与共享相位，不模拟 Unreal/Godot 调度。覆盖 2/0 个接纳、粗细时间切片跨三个标记一致、全局防抖丢一个合法右脚事件。

[返回正文](../../../GameLibrary/角色动画/角色移动/步态同步/步态混合中的落脚通知去重与补漏.md)
