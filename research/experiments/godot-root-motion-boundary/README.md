# Godot原生根运动：读取delta不是消费事件，也不是自动移动角色

## 首轮实际结果

2026-10-31，当前作者运行 `results/e53803a1-eab0-4823-a9f8-69e5624522c3/` PASS。**两个新Godot行为进程，加一次独立`--version`命令**；不是三种行为场景。无初始失败，未修改预冻结预期去适配结果。所有首次输出与命令、退出码、源码/引擎hash保存在唯一UUID目录。

这个实验是新增原生运行证据。此前现有文章只有4项Python二维接触几何模型测试和未执行的Rig依赖工作表；不得回写为此前已有Godot根运动验证。基线为6492be88、`gamelibrary-publish-rig`；执行前纠正了门槛稿最初错误使用旧gltf stage的出处。`gate.md`保留当前基线逐字摘录与纠正说明。

## 输入与观察

原创一骨Skeleton3D，无网格/下载角色/DCC。AnimationPlayer只提供资源，AnimationTree单个AnimationNodeAnimation播放，MANUAL唯一驱动，`root_motion_local=false`。两秒非循环clip线性位置0→(4,0,0)、旋转绕Y轴0→90°；RESET明确identity。初始化`advance(0)`后才进行固定非零推进，不经过循环边界。

| 配置/步骤 | 实际读回 |
|---|---|
| 普通姿态，无root_motion_track；advance(0.5) | 骨位置(1,0,0)、yaw22.5°；父Node3D仍identity |
| 指定Skeleton:root提取；advance(0.5) | getter位置delta(1,0,0)、旋转delta22.5°；骨与父Node3D仍identity |
| 不advance，再读position/rotation | 两个getter仍返回同一非零delta，不是第二次返回零 |
| 显式应用第一delta零次/一次/两次 | 三个独立Node3D位置x=0/1/2，yaw=0/22.5/45° |
| 再advance(0.25) | 新delta位置(0.5,0,0)、yaw11.25°；不是累计位置1.5/角33.75° |

数值判据在代码前冻结的`contract.json`；位置分量容差1e-5，四元数检查单位长度及q或-q到预期四元数的欧氏距离≤1e-5。重复getter原始值还要求精确相等。完整四元数而非仅格式化角度保留在原始RESULT_JSON与解析JSON。没有把四元数符号相反误判旋转不同。

应用接收者是独立Node3D，**不是CharacterBody碰撞移动**。平移按明确父坐标分量相加、旋转同轴相乘；未验证任意旋转/平移组合的根运动积分。0/1/2由实际循环写入和最终Node3D读回核对，不是声称引擎内部有消费计数。捕获函数每次实际调用两个getter，另一次读取用于明确应用，顺序由源码可核；calls数组只记录advance调用，不冒称所有getter调用的独立追踪器。

## 工程结论与局限

在本例同一求值与下一次求值之间，getter读取不破坏delta。重复读本身不移动节点；**应用代码重复使用同一结果**才使演示接收者走两次。需要由游戏的运动适配层决定一次评估结果何时、由谁应用；本实验没有实现通用评估ID或恰好一次消费系统。

正常轨道对照确保不是路径失效导致一切为零。提取后父节点不移动，是此原创场景的观察，不代表所有用户脚本或其他轨道都不能移动父节点。只有一骨与固定两次推进，没有IK、足底质量、真实角色、混合、循环、seek、中断、物理碰撞、网络或Unity/Unreal证据。

## 原始来源与构建身份

访问2026-10-31：
- [Godot4.6 AnimationMixer](https://docs.godotengine.org/en/4.6/classes/class_animationmixer.html)：root_motion_track、root_motion_local、MANUAL/advance以及位置/旋转getter。local=true与false语义不同，本例显式false。
- [Godot4.6 AnimationTree](https://docs.godotengine.org/en/4.6/classes/class_animationtree.html)：关联Player仅管理资源，Tree控制播放。
- [固定比较源码animation_mixer.cpp](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/animation/animation_mixer.cpp)：1046–1053新混合重置；1870–1905提取和普通姿态应用分支；2091–2096getter返回成员。没有复制完整第三方实现。

实际引擎SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`；本轮version.stdout与Engine.get_version_info原始记录身份。共享[来源限制](../../source-notes/godot-runtime-provenance.md)：安装构建自报7d41c59c4与公开tag对应35e80b3a不一致，比较源码不是已认证的精确二进制来源。此观察不证明官方真实性，也不推断引擎不安全或有缺陷。

## 复跑与新鲜性

```sh
python -B run.py /tmp/new-native-root-motion-evidence
```

每次生成新UUID目录，先STARTED，所有检查成功才PASS；失败记录FAIL与真实错误，已有UUID不覆盖。每条命令20秒等待上限，超时记录部分输出。原生进程不创建外部子进程；Python对超时直接子进程执行终止等待，不保证整机故障、不可终止内核调用或所有OS的时间界限。临时工程/HOME/XDG缓存自动清理，不发布字体缓存或下载资产。失败也保留原始stdout/stderr和源码hash；没有另做超时故障注入，不能声称清理分支实测通过。

没有assert型验收，但作者本轮只执行普通Python模式；未把未执行优化模式算通过。summary输出hash是归档一致性，不是执行真实性的密码学证明。`contract.sha256`是预代码协议摘要；`SHA256SUMS`给出冻结源与文档摘要。

## 独立复核

[独立复核](review/REVIEW.md)在隔离副本执行两种配置及一次版本命令，UUID `8f7817ac-8c38-44ed-80a9-b861b168ac3d`。独立判据读取原始RESULT_JSON，以符号不变的四元数旋转矩阵比较、实际骨/父/接收者位置和调用配置验证结果。作者两行为进程、审查者另两行为进程，各有一次版本命令；没有额外负例或真实角色运行。当前验收不扩大原4项Python模型或未执行Rig工作表的范围。

Public archive layout: author UUID under `results/`, independent UUID under `review/evidence/`. Historical `review/run.stdout` and `review/check.py` retain original local output paths; use the portable integration checker for this relocated archive rather than interpreting those old paths as live. To rerun, copy `run.py`, `main.gd`, `project.godot` and `contract.json` into a new external directory and invoke the copied runner with a new external output directory. Do not add runs to this reviewed archive.

`SHA256SUMS` preserves the author handoff before this public-layout note; it is not a current manifest for edited documentation. Runtime source bytes are unchanged and bound by both UUID summaries. [Portable archive check](integration/README.md) reads both relocated receipts without launching Godot or accessing the historical binary path.
