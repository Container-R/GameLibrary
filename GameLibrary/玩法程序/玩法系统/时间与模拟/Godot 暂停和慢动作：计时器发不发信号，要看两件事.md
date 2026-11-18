# Godot 暂停和慢动作：计时器发不发信号，要看两件事

玩家打开暂停菜单，技能冷却却还在走。另一个场景开启慢动作，菜单里一条本来很短的提示迟迟不消失。两处都用了 `SceneTree.create_timer()`，但问题不同：前者没规定暂停能不能走，后者没规定按哪种时间走。更容易漏掉的是，业务节点即使停止了每帧更新，已经连上的超时信号仍可能执行。

本文用 Godot 4.6 的单次 SceneTreeTimer 说明如何选这两个条件，并在一个无界面工程里对照实际回调。这里讨论游戏进程仍在运行时的暂停与慢动作，不把本地计时器用于跨进程、系统挂起或服务器期限。

## 先决定停不停，再决定走得多快

`SceneTree.create_timer(seconds, process_always, process_in_physics, ignore_time_scale)` 创建一个到期发出 `timeout` 的计时器。三个布尔项容易写混：[1][2]

- **暂停时是否继续：** `process_always` 默认为 `true`，即使 `SceneTree.paused` 打开也继续。设为 `false`，场景树暂停时这个计时器暂停。
- **时间累计是否受慢动作影响：** `ignore_time_scale` 默认为 `false`，计时受 `Engine.time_scale` 影响。设为 `true`，才用不受该倍率影响的经过时间；但它不能绕过前一条暂停政策。
- **何时更新：** `process_in_physics` 默认为 `false`，在普通处理帧更新；打开后改到物理帧末更新。它改变回调跟哪种帧走，不是把计时改成真正的后台任务。

例如，规定技能冷却随玩法慢动作变慢，暂停时不消耗，就用 `create_timer(seconds, false, false, false)`。暂停菜单里必须与慢动作无关的提示，可用 `create_timer(seconds, true, false, true)`，但只让回调影响该提示。也有合理的第三种需求：计时需要在暂停时冻结，玩家恢复后仍以不受慢动作影响的速度继续。这里应当同时用 `process_always=false` 和 `ignore_time_scale=true`，不是在二者之间选一个。

项目里若经常用这几种语义，建议封装成按用途命名的入口，并在调用旁说明会改变哪类状态。特别不要只看一串 `true, false, true` 判断意图。

## 节点停了，不代表连在它上面的信号也停了

Godot 的暂停文档说明，节点因处理模式而暂停时，`_process` 等回调不再定期执行，但已经连接的信号仍可调用函数。[3] 因此，把技能逻辑放在随场景树暂停的节点上，不能弥补一个允许暂停时到期的计时器。例如，超时函数若直接开门，暂停菜单还在时门状态也可能改变。

对有副作用的回调，按玩法明确它该继续、等待或取消。若必须随玩法冻结，先选对计时器。若使用暂停也继续的计时器，但回调只对当前一轮提示有效，应用结果前再核对该提示的身份或轮次；不要把「到期」当成旧任务仍有效的证明。相反，若需要暂停期间让玩家继续操作菜单，还要检查菜单自身的节点处理模式；计时继续并不使所有输入和界面更新自动恢复。

## 在原生运行中分开这两条规则

以同一 Godot 4.6.3 Linux 可执行文件运行一个无界面工程。场景树暂停，`time_scale=0.05`，创建四个设置为 0.08 秒的单次计时器，都按普通处理帧更新。脚本用另外的、不受暂停和时间倍率影响的计时器作观察点：较短暂停后检查一次，较长暂停后再检查，然后在仍为慢动作时解除暂停，最后再恢复正常倍率。

| `process_always` | `ignore_time_scale` | 较短暂停后 | 较长暂停后 | 恢复后仍慢动作 | 恢复正常倍率后 |
| --- | --- | --- | --- | --- | --- |
| true | true | 已到期 | 保持已到期 | 不重复发出 | 不重复发出 |
| true | false | 尚未到期 | 已在暂停时到期 | 不重复发出 | 不重复发出 |
| false | true | 尚未到期 | 未到期 | 到期 | 不重复发出 |
| false | false | 尚未到期 | 未到期 | 尚未到期 | 到期 |

在分别设为 60、120 的帧率上限时，两次日志都归入这四类。记录回调的节点有活动期 `_process` 调用，暂停期间没有 `_process`，但允许暂停继续的计时器仍调用了连在节点脚本上的函数。这是对回调阶段的检查，不是精确定时测量；日志里的毫秒数不应当拿来给每种机器设容差。

接手实际故障时，可先记下创建时的四项参数，再分开记「什么时候超时」「哪个业务结果何时被应用」。在确定冻结语义后，用一次长于短提示的暂停和一次足以看出差异的慢动作复测。只开暂停、从不改变倍率，不能查到提示为什么因慢动作变迟；只测慢动作、从不暂停，也不能验证冷却是否真的冻结。

[运行最小 Godot 工程并查看两次观察记录](../../../../管理档案/实验/Godot暂停时间与计时器/README.md)。

## 参考资料

1. Godot Engine，[SceneTree](https://docs.godotengine.org/en/4.6/classes/class_scenetree.html#class-scenetree-method-create-timer)，4.6 文档，`create_timer` 的三个开关及更新顺序。
2. Godot Engine，[SceneTreeTimer](https://docs.godotengine.org/en/4.6/classes/class_scenetreetimer.html)，4.6 文档，一次性计时器及 `timeout`。
3. Godot Engine，[Pausing games and process mode](https://docs.godotengine.org/en/4.6/tutorials/scripting/pausing_games.html)，4.6 文档，节点处理模式、暂停时不被定期调用的函数及信号。
