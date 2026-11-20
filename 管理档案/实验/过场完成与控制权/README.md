# 过场完成与控制权：Godot 试件

在本目录的 native/ 使用 Godot 4.7.2 stable official ed1daf0bf，执行：

```sh
set -eu
tmp=$(mktemp -d)
export XDG_CACHE_HOME="$tmp/cache" XDG_DATA_HOME="$tmp/data" XDG_CONFIG_HOME="$tmp/config"
mkdir -p "$XDG_CACHE_HOME" "$XDG_DATA_HOME" "$XDG_CONFIG_HOME"
godot --headless --path . --script probe.gd > "$tmp/playhead.out"
godot --headless --path . --script ownership_probe.gd > "$tmp/ownership.out"
grep '^{' "$tmp/playhead.out" | cmp - observed.json
python3 - "$tmp/ownership.out" <<'PY'
import json, sys
with open(sys.argv[1]) as stream:
    actual = json.loads(next(line for line in stream if line.startswith("{")))
with open("ownership_observed.json") as stream:
    expected = json.load(stream)
assert actual == expected
PY
```

- `probe.gd`：不循环的两秒 AnimationPlayer，手工推进，方法轨即时。对比逐段推进、从头跳到末尾、电花后跳到末尾、一次 advance。视觉门开度均为 1；只有推进得到完成信号。方法轨记录的是事件／奖励尝试，不会写任务。
- `ownership_probe.gd`：实际 Godot 延迟队列、Camera3D 和视口当前相机；旧回调由试件主动入队，不代表 AnimationPlayer 会以这组时序发信号。比较仅奖励去重、加播放入口检查、加逐资源令牌；分别测试跳过后重发、取消后重发、资源拆分、同步重入。输入用自定义门禁变量，奖励为内存标记。
- 未验证物理门、设备输入、保存事务、重启或其他引擎。同一项目的正式验收仍须把这些真实出口接进测试。
