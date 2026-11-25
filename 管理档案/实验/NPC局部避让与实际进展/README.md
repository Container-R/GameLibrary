# NPC 局部避让与实际进展：复现材料

[返回正文](../../../GameLibrary/游戏人工智能/移动导航/局部避让与通行/NPC%20明明有路，为什么一相遇就走不动.md)

[解析试件](probe.py)及[输出](observed.txt)仅限制严格一维对称速度和两个圆在直道同横截面的净宽，不是 ORCA 实现。

真实避让试件：[配置](godot/project.godot)、[脚本](godot/run.gd)、[一次完整日志](godot-observed.txt)、[后续每组 3 轮复验](godot-reruns.txt)。Godot 4.7.2.stable.official.ed1daf0bf，2D，固定 60 Hz：

```sh
export XDG_CACHE_HOME="$(mktemp -d)" XDG_DATA_HOME="$(mktemp -d)"
set -e
for m in center lanes blocked_actuator; do
    godot --headless --path godot --fixed-fps 60 --script run.gd -- "$m"
done
```

脚本在物理帧前提交本步位置与首选速度、等待同轮两个避让回调，再自行按固定时长执行位移；第三组故意忽略回调。用相对位置前后端点之间的线性插值计算两圆最短表面间距；假想直道 `|y|≤1.3` 的墙距直接计算，没有以墙作为避让或物理输入。每组 600 步，两个角色都以离目标小于 0.025 为到达，之后停止。基线的近接触数值会在小范围波动，验证的是保留间距但未到达、侧线对照能到达、故意断开移动时避让输出和实际分离，不要求日志逐字节相同。
