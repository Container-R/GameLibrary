# 双手道具接触与姿势阶段

正文：[双手道具转向后，辅助手为什么没抓住握把](../../../GameLibrary/角色动画/动画运行时/逆向运动学/双手道具转向后，辅助手为什么没抓住握把.md)。

- `python3 -B model.py | cmp - observed.txt`：Python 标准库，固定 2D 刚体位置及方向、受控夹取距离；四个误差分别是送入腕偏离预期、刚解完偏离请求、最终腕相对中间腕移动、最终掌离当前握点。
- Godot 4.7.2，`godot --headless --path . --script probe.gd`，与 [实跑输出](engine-observed.txt)对照。Linux 下可设独立可写的 XDG_DATA_HOME、XDG_CACHE_HOME、XDG_CONFIG_HOME。剧本包含断言。
- 原生探针用两个骨骼、非单位场景根、三段直接改写变换的 modifier。当前主手转 90°、平移 10 厘米；辅助手先对齐，后续另移腕 6、−8 厘米。中间和最终回调即时取值，最后用延迟回调应读回基姿。没有实际臂链 IK、蒙皮绘制、碰撞或物理接触。
