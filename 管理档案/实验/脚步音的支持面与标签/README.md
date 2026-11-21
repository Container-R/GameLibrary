# 脚步音的支持面与标签

对应正文：[左脚踩金属、右脚踩石板，为什么脚步音却一样](../../../GameLibrary/声音与音乐/游戏音效/表面音效/左脚踩金属、右脚踩石板，为什么脚步音却一样.md)。

**原生射线。** 运行 `python3 -B run.py`；若 `godot` 不在 PATH 可用 `GODOT_BIN` 指向安装的二进制。脚本临时启动两个独立的 Jolt 项目，默认设置一组，只开 Ray Cast Face Index 一组，均执行 [probe.gd](probe.gd)。[固定输出](observed.json) 来自 Godot `4.7.2.stable.official.ed1daf0bf`。两脚在同一 Floor 的形状 0，默认 −1/−1，启用后 0/3；平移 X+3 后相同。局部坐标派生的标签只是试件的石/土选择，不是从音频素材测得。脚右侧添加木板，左侧添加 Area，比较是否查询 Area。当虚拟直线射到 Floor/Wood/Trigger，只能说明查询命中，不说明真实脚已经承重。

**合成几何。** 执行 `node face-lookup.js`，输出见 [face-lookup.json](face-lookup.json)。四个三角形的 ID 是试件指定的 10、11、20、21，不等于 Godot 的 0/3，不和真实存档配对。物体级标签相同，碰撞面的表或物体局部区能区分金属和石；平移 3 后，固定世界 X=0 的标识会误选。此组没有引擎、材质音效或力学。
