# 基础资产更新与半径覆写：对照步骤

对应正文：[改了基础敌人的碰撞体，为什么有些预制体变体没更新](../../../GameLibrary/引擎与工具/资产工具/预制体继承与覆写/改了基础敌人的碰撞体，为什么有些预制体变体没更新.md)。

## 已执行：检查标量与来源归属

运行 `python3 model.py`。模型每层保存一个值或留空；留空时向上读取来源。Python 3.12.14 运行 [model.py](model.py)，五组断言通过；[原始输出](model-output.txt) 四列依次为 Patrol、Scout、Scout-A、Scout-B，括号内为保存值的层。第三组与第四组从同一次改基础资产后的状态各自出发；脚本在两组之间恢复了 Scout-B 的覆写。

模型只核对在所列前提下每一步的结果，不读取 .prefab、不模拟 Unity 的 Apply、组件身份、同值覆写生命周期或物理形状。

## Unity 6.0：编辑器复现方案（未执行）

1. 新建临时 3D 场景，建 BaseEnemy，子对象 Body 上添加 Capsule Collider，Transform 各层缩放固定为 (1, 1, 1)，高度设为 2，Radius 设为 0.40。拖入 Project 保存为普通 Prefab；不替换或复制组件。
2. 在 Project 从 BaseEnemy 创建两个 Prefab Variant：Patrol 不改半径，Scout 在 Prefab Mode 将同一个 Body 的 Radius 改成 0.35 并保存。向场景放入两份 Scout；只在第二份的同一属性写 0.30，保存场景。标记两者为 Scout-A/B 不要求修改预制体资产名。
3. 在 BaseEnemy 的 Prefab Mode 把 Radius 改到 0.50。记录两个变体资产和两个 Scout 实例的 Radius、覆写状态、直接来源。预期 0.50 / 0.35 / 0.35 / 0.30。
4. 单独 Revert Scout-B 的 Radius，预期回到 0.35。把它重新设为 0.30；再单独 Revert Scout **资产**的 Radius，预期 Scout 与 Scout-A 都为 0.50，B 保留 0.30。每一步保存并重新选中或打开对象核验。
5. 把 BaseEnemy 调到 0.55；确认 Patrol 与 Scout-A 跟随，而 B 保持 0.30。还原探针。若实际不同，先记录精确 Editor 版本、链接到的资产与组件、属性覆写状态、是否保存成功，再判断是否偏离本例前提。
