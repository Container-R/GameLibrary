# NPC 双向窄门排队：复现材料

```sh
python3 queue_model.py
godot --headless --fixed-fps 60 --path native --script bottleneck.gd
```

- Python 3.12.14 离散模型：两侧排队各三人，当对面在等时批次最多两人，依次发放 A/B、x/y、C、z。一人清空而另一人仍占用不切换，出口被堵不发新许可。不模拟连续移动与间距。
- Godot 4.7.2.stable.official.ed1daf0bf 原生 2D 墙壁和圆形碰撞体。两个对照初始条件相同，均为两人相向、后到侧从侧面并入；唯一改动是是否等合流区空后才准并入。每组 420 步。直接并入双方都没出段；等待并入的两个角色分别在第 140、367 步完全出段，准许第二个并入发生在第 183 步。测两个特定运动策略，不求群体统计、导航网格或 RVO 行为。

见 [Godot 试件说明](native/README.md) 和 [原始日志](native/observed.txt)。在禁止写入默认配置的环境，运行时可将 XDG_DATA_HOME、XDG_CACHE_HOME、XDG_CONFIG_HOME 指到可写临时目录。

[返回正文](../../../GameLibrary/游戏人工智能/移动导航/局部避让与通行/单列窄门的双向排队与放行.md)
