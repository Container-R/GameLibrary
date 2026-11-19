# 过肩镜头换边

[返回正文](../../../GameLibrary/玩法程序/玩法系统/镜头控制/过肩镜头换边：保住观察点，检查整段过渡.md)

在本目录运行几何试件；脚本只使用 Python 标准库：

```bash
python3 -B check_shoulder_path.py | diff -u observed.json -
python3 -B draw_path.py
```

第二个脚本将原创几何图写到当前目录的 `shoulder-path.svg`；可把脚本复制到临时目录来比较 SVG，避免改动检出文件。

原生试件使用 Godot 4.6.3 stable official、GodotPhysics3D。若在只读 home 的机器运行，可设临时 XDG 目录：

```bash
d=$(mktemp -d)
mkdir "$d/cache" "$d/data" "$d/config"
XDG_CACHE_HOME="$d/cache" XDG_DATA_HOME="$d/data" XDG_CONFIG_HOME="$d/config" \
  godot --headless --path native-godot --script res://check.gd |
  sed -n 's/^OBSERVED //p' | diff -u native-godot/observed.json -
```

项目只生成两支长度 3、显式半径 0.2 的弹簧臂；添加两件静态球体并调用独立形状与射线查询。查询中 Y 固定为 0，正文的平面前方 +y 对应引擎 −Z。JSON 验证端点臂长、横扫与绕行、三条观察线和初始重叠的反例。它不把两支弹簧臂拼成一个游戏换边控制器，也不验证渲染、插值曲线、近裁面、视线扫掠时间或目标机性能。
