# Factorio的锅炉只收水，为什么润滑油仍能穿过去

2024 年的 Fluids 2.0 把相连管道、地下管道和储罐合成共享的“段”，液体不再逐节传播。[1]

raiguard 在 2026 年 6 月记录了一个相关故障：锅炉用于生产的内部缓冲只收水，管线缓冲却没有过滤，藏在锅炉里的部分也不显示。润滑油能够经过，不代表锅炉拿它来生产。[2]

修复去掉这层重复缓冲，把过滤放到管线上。但成员变化时，还得协调各自的过滤与已有液体：只准水的一段遇到装有润滑油的一段，冲突清除前不合并，并显示警告。[2]

这项保护针对双向合并，不能保证泵或单向输出不混液。修复后示意图中，锅炉也只看自身那部分水。[2]

后续 2.1 稳定版公告提到了防混液与流量调整。[3] 本文只解释历史案例，没有运行游戏、检查存档或取得源码，不据此判断任意当前补丁的行为。

## 参考来源

[1] raiguard，Wube Software，[Friday Facts #416 — Fluids 2.0](https://factorio.com/blog/post/fff-416)，2024-06-21，The new algorithm。

[2] raiguard，Wube Software，[Friday Facts #442 — Flip, Flow, and Fresh Paint](https://factorio.com/blog/post/fff-442)，2026-06-12，Fluid system updates、Fluid mixing prevention，以及[修复前](https://cdn.factorio.com/assets/blog-sync/fff-442-boiler-diagram-before.png)与[修复后](https://cdn.factorio.com/assets/blog-sync/fff-442-boiler-diagram-after.png)原图。

[3] Factorio team，[Friday Facts #449 — 2.1 Stable](https://factorio.com/blog/post/fff-449)，2026-10-23，2.1 Stable、Flipping and fluids。

所引文字与两张原图于 2026 年 11 月 4 日读取。未观看视频；原图只作查证，不转载。

---

[返回本书架](README.md)
