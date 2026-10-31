# 固定步长边界：原始来源索引

访问日期：2026-10-31。以下仅保存定位、证据用途与原创说明，不镜像正文或第三方源码。

| ID | 原作者/组织与来源 | 定位/版本 | 用途与限制 |
|---|---|---|---|
| SRC-FIXED-001 | Glenn Fiedler, [Fix Your Timestep!](https://gafferongames.com/post/fix_your_timestep/), 2004-06-10 | Semi-fixed timestep; Free the physics; The final touch | 固定 dt、积累器、过载代价与展示插值原理；不是当代引擎 API 保证。 |
| SRC-FIXED-002 | Unity Technologies, [Fixed updates](https://docs.unity3d.com/6000.0/Documentation/Manual/fixed-updates.html) | Unity 6000.0; When frame rate is higher/lower than the fixed update rate | 官方说明一帧可能发生零次或多次固定更新；不是跨平台确定性证明。 |
| SRC-FIXED-003 | Godot Engine contributors, [Physics interpolation introduction](https://docs.godotengine.org/en/stable/tutorials/physics/interpolation/physics_interpolation_introduction.html) | stable 文档，Physics ticks and rendered frames / In the past；滚动版本未冻结 | 官方解释物理与展示频率差异和插值延迟；迁移前需核对目标版本。 |

许可处理：不复制任何来源代码；本库调度模型独立编写。文档只转述必要原理，不主张拥有来源的再分发许可。

补充正文直接使用来源：

- SRC-FIXED-004：Glenn Fiedler，[Deterministic Lockstep](https://gafferongames.com/post/deterministic_lockstep/)，2014-11-29，Determinism / Networking Inputs；相同步长不等于跨构建位级确定性，输入需有帧归属。
- SRC-FIXED-005：Unity，[Input settings](https://docs.unity3d.com/Packages/com.unity.inputsystem@1.11/manual/Settings.html#update-mode)，元数据版本 1.11.2，Update Mode；仅核对更新时机，未测试设备行为。
- SRC-FIXED-006：Unity，[Handling variation in time](https://docs.unity.com/en-us/engine/6000.0/manual/scripting/managing-time-and-frame-rate/time-handling-variations)，6000.0，Limiting recorded time variation / Time variation and the fixed update loop；最大时间限制与游戏时间语义。

多语言检索：固定時間ステップ、最大許容時間ステップ、固定步长、fixed timestep。日文官方译版仅作术语交叉定位，不作为独立复核。
