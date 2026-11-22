# 叠层效果到期与周期：合成时钟

[返回正文](../../../GameLibrary/玩法程序/玩法系统/战斗状态/叠层效果的持续时间到底刷新了谁.md)。

```sh
node clocks.js
node collision.js
```

Node v24.22.3 的输出分别是 [observed.json](observed.json)、[collision.observed.json](collision.observed.json)。
- [clocks.js](clocks.js) 在每个模拟步先到期、再接受新应用、最后计算组级脉冲；对照独立层、共享清除、阶梯掉层、周期重置、满层拒绝/仅刷新和同应用重发。一个统一的 5 步时长与间隔只用于本试件。
- [collision.js](collision.js) 固定步骤 8 同时到期和周期到点，交换执行次序。两边结束时均零层，先脉冲会在归零前留下两层贡献的结算记录。

只运行了自定义教学逻辑。未运行 UE、GAS、实机伤害/属性、动画或网络；没有复制正式资产的实现或执行顺序。没有模拟不同层伤害与来源、模拟步外的事件或非周期伤害。
