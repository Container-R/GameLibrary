# Unity 2022.3 要用新版 Input System 的修复，能只移植输入包吗？

项目锁在 Unity 2022.3，按键设置页却有一行空白：键盘上的 W、A、S、D 可以移动，界面偏偏列不出这组绑定。Unity 后来的 Input System 包修了这类问题，但整包提高了编辑器版本下限。这里有两个不同的升级目标：让 UI 正确生成绑定文本，或者让旧引擎具备新版本的输入后端能力。前者值得试一个小补丁，后者不能靠复制输入包实现。

## 先核对两份清单，不要改数字试运气

`Packages/manifest.json` 是项目请求的包版本；包自己目录里的 `package.json` 才声明该包的版本、依赖和编辑器下限。Unity 的 `unity` 写主、次版本；若另有 `unityRelease`，还要核对具体发行版本。[1]

| 官方源码版本 | 清单中的编辑器下限 | 对 2022.3 项目的含义 |
| --- | --- | --- |
| Input System 1.19.0 | `2022.3` | 声明覆盖 2022.3，可以先试这个已声明兼容的基线。[2] |
| Input System 1.20.0、1.20.1 | `6000.0` | 整包不声明支持 2022.3；清单数字改小也不会补齐引擎 API。[3] |

上述清单没有 `unityRelease`，表格只比较这三个固定版本，不等于特定补丁、包源或目标平台已通过测试。先用 Package Manager 解析项目能取得的兼容版本；如果它已经解决问题，没必要维护补丁。若仍有问题，再从发布说明定位**想移植的那条行为**，不要把某条修复的版本条件与整个包的版本下限混成一件事。

## 包内修复：把复合绑定作为一个显示单位

在这个例子里，`2DVector` 复合绑定有一条根和紧跟其后的四条部件。组名 `Keyboard` 只放在部件上。1.19.0 的 `GetBindingDisplayString(action, bindingMask, ...)` 先跳过部件，再要求根匹配组；空组的根匹配不上，四条有组的部件又都不参与顶层显示，结果就是空字符串。1.20.0 修的不是键盘采集：根不匹配时，它再检查这一根连续的部件，只要一条匹配，就用已有的索引重载生成**整个**复合绑定的提示。不把子键各自显示，也不越过第一条非部件绑定借用另一组。[4][5]

可在最小场景中把下面代码保存为 `Assets/BindingLabelProbe.cs`，将组件挂到场景对象上后运行。不调用 `Enable()`，这个检查只比较绑定文本，不检验玩家能否移动。选择无关组的那一项用于排除“干脆显示全部绑定”的假修复。

```csharp
using UnityEngine;
using UnityEngine.InputSystem;

public class BindingLabelProbe : MonoBehaviour
{
    void Start()
    {
        using (var move = new InputAction("Move"))
        {
            move.AddCompositeBinding("2DVector")
                .With("Up", "<Keyboard>/w", groups: "Keyboard")
                .With("Down", "<Keyboard>/s", groups: "Keyboard")
                .With("Left", "<Keyboard>/a", groups: "Keyboard")
                .With("Right", "<Keyboard>/d", groups: "Keyboard");
            Debug.Log($"root=[{move.GetBindingDisplayString(0)}]");
            Debug.Log($"keyboard=[{move.GetBindingDisplayString(InputBinding.MaskByGroup("Keyboard"))}]");
            Debug.Log($"other=[{move.GetBindingDisplayString(InputBinding.MaskByGroup("Other"))}]");
        }
    }
}
```

源码预期：未改的 1.19.0 上 `root` 有文本、`keyboard` 为空；回移这一判断后，两条文本应相同且非空，`other` 仍为空。不硬编码字母大小写或分隔符，因为显示名不是这个补丁的验收目标。正式项目再各测一条普通绑定、一条挨着下一组复合绑定的情况，以及玩家重绑后实际提示是否更新。这个代码例未在 Unity 编辑器运行；这里核对的是实现及匹配条件，不是已经做成的项目补丁。

只在自己维护的一处 UI 使用时，也可以在项目代码里做同样的组选择，然后调用已有的按索引显示接口，避免持续维护一个包分支。若多个调用点或第三方组件都依赖这个重载，才考虑把兼容基线的包嵌入为 `Packages/com.unity.inputsystem/`，只移植相关判断和测试。保留包许可及来源；把嵌入版本纳入项目版本控制，不修改 `Library/PackageCache`。嵌入包会覆盖同名注册表包，回退时从回退分支恢复项目清单、锁文件并移除嵌入副本；只改依赖数字不会切走仍存在的嵌入包。[6]

## 跨到引擎：找到第一个包外调用

Input System 的 C# 源码可以公开查看，但不是 Unity 原生输入后端的源码。例如 1.19.0 的包内 `NativeInputRuntime.DeviceCommand` 把设备命令交给 `UnityEngineInternal.Input.NativeInputSystem.IOCTL`；Unity 2022.3 的 C# 参考源码里，这个接口是通向引擎的 `extern` 声明。复制包没有改变 Editor 或 Player 里负责处理设备命令的实现。反过来也不能因为“设备相关”就直接判定不能回移：若变的是包里的控制布局和映射，旧后端已经送出正确的原始数据，修复仍可能留在包内。先找到原始数据在哪一侧开始不对。[7]

一个可定位的反例是 1.20.0 修复 Unity 6000.5.0a8 及以后版本的 Game View 焦点切换丢失 `OnMouseUp` / `OnMouseUpAsButton`：改动在包里，但它跳过的是由编译条件保护、向引擎 `NativeInputSystem.DoSendMouseEvents` 转发的路径。包的程序集定义分别从 6000.4.0a4 和 6000.5.0a8 启用鼠标脚本事件桥接和焦点事件支持。补丁跳过的是前一条路径上读取了不该用的 Editor 状态缓冲的更新，并不说明 2022.3 的同名回调有同一故障。若你在 2022.3 也遇到丢回调，在同一场景记录旧式鼠标回调和 Input Action 回调：对比保持焦点按下再释放，以及按下后切走焦点、再回到 Game View 释放。先找旧版在何处丢掉事件，不要为让代码编译而强行打开版本宏。[8]

## 怎样算回移成功

在独立分支固定 Editor 完整版本、输入包解析结果和 `Active Input Handling`；切换输入后端设置后要重启 Editor。[9] 用同一项目的**原版、补丁版、回退版**运行同一组检查：

| 层次 | 至少留下什么结果 |
| --- | --- |
| 包解析和编译 | 干净检出后能解析同一输入包；实际选中预期来源。检查改动是否引入 2022.3 不存在的 API、程序集依赖或序列化数据，不以“消掉编译错误”为终点。 |
| 编辑器内行为 | 比较上面的三行日志，保留一个明确不应匹配的例子；项目中读取实际重绑后的提示。 |
| 目标 Player 与设备 | 用项目真实构建目标、脚本后端和设备，分别记录设备是否出现、原始控制值是否变化、动作是否触发、UI 标签是否更新。设备值进来了但显示空，继续查后两层；原始输入没有进来，别拿一个正确的标签当设备支持证据。 |

能在项目层绕过就先绕过；确实缺包内行为才移植最小改动。若目标行为要靠旧 Editor 或 Player 没有的 API、设备数据或原生语义，就评估升级 Unity 或另找受支持的接口，不发布未经目标构建和设备验证的整包替换。

## 来源

1. Unity 2022.3 手册：[包清单的 `unity` 和 `unityRelease`](https://docs.unity3d.com/2022.3/Documentation/Manual/upm-manifestPkg.html#unity)。
2. Unity Input System：[1.19.0 包清单](https://github.com/Unity-Technologies/InputSystem/blob/ca8d898356596a91bda6505e506cc1a4bb3a9fa6/Packages/com.unity.inputsystem/package.json)。
3. Unity Input System：[1.20.0 包清单](https://github.com/Unity-Technologies/InputSystem/blob/27757ebb14c0659ce1dbe39822ce97b33adea6c9/Packages/com.unity.inputsystem/package.json)、[1.20.1 包清单](https://github.com/Unity-Technologies/InputSystem/blob/a934411756c8862cb0f54da514a9b7cc1c000a2b/Packages/com.unity.inputsystem/package.json)。
4. Unity Input System 1.19.0：[显示重载](https://github.com/Unity-Technologies/InputSystem/blob/ca8d898356596a91bda6505e506cc1a4bb3a9fa6/Packages/com.unity.inputsystem/InputSystem/Actions/InputActionRebindingExtensions.cs#L311-L336)、[组匹配条件](https://github.com/Unity-Technologies/InputSystem/blob/ca8d898356596a91bda6505e506cc1a4bb3a9fa6/Packages/com.unity.inputsystem/InputSystem/Actions/InputBinding.cs#L840-L846)（同文件 878–888 行检查组字段）。
5. Unity Input System 1.20.0：[修改后的重载](https://github.com/Unity-Technologies/InputSystem/blob/27757ebb14c0659ce1dbe39822ce97b33adea6c9/Packages/com.unity.inputsystem/InputSystem/Runtime/Actions/InputActionRebindingExtensions.cs#L311-L354)、[发布说明 UUM-141423](https://github.com/Unity-Technologies/InputSystem/blob/27757ebb14c0659ce1dbe39822ce97b33adea6c9/Packages/com.unity.inputsystem/CHANGELOG.md#L14)。
6. Unity 2022.3 手册：[嵌入包的覆盖和恢复](https://docs.unity3d.com/2022.3/Documentation/Manual/upm-embed.html#embed-cached)；Input System 1.19.0：[包许可](https://github.com/Unity-Technologies/InputSystem/blob/ca8d898356596a91bda6505e506cc1a4bb3a9fa6/Packages/com.unity.inputsystem/LICENSE.md)。
7. Unity：[1.19.0 输入包设备命令](https://github.com/Unity-Technologies/InputSystem/blob/ca8d898356596a91bda6505e506cc1a4bb3a9fa6/Packages/com.unity.inputsystem/InputSystem/NativeInputRuntime.cs#L41-L47)、[2022.3 C# 参考源码的引擎声明](https://github.com/Unity-Technologies/UnityCsReference/blob/a322ce5f78a82cf7ea211857a45338136ed7a22f/Modules/Input/Private/InputModule.bindings.cs#L35-L40)。
8. Unity Input System 1.20.0：[鼠标回调修复说明](https://github.com/Unity-Technologies/InputSystem/blob/27757ebb14c0659ce1dbe39822ce97b33adea6c9/Packages/com.unity.inputsystem/CHANGELOG.md#L35)、[`FinalizeUpdate` 中的转发条件](https://github.com/Unity-Technologies/InputSystem/blob/27757ebb14c0659ce1dbe39822ce97b33adea6c9/Packages/com.unity.inputsystem/InputSystem/Runtime/InputManager.cs#L4049-L4062)、[程序集的版本条件](https://github.com/Unity-Technologies/InputSystem/blob/27757ebb14c0659ce1dbe39822ce97b33adea6c9/Packages/com.unity.inputsystem/InputSystem/Unity.InputSystem.asmdef#L95-L104)。
9. Unity Input System 1.19.0：[安装与启用新输入后端](https://github.com/Unity-Technologies/InputSystem/blob/ca8d898356596a91bda6505e506cc1a4bb3a9fa6/Packages/com.unity.inputsystem/Documentation~/Installation.md#L31-L40)。
