# 内建 LookAt 顺序与姿态观察：来源及证据范围

2026-10-31。对应既有 [SOL-ANIM-001](../../solutions/animation/turn-in-place-foot-sliding.md) 的独立双骨补证。原四项二维模型、单骨根运动提取与仍未执行的 Unity Rig 工作表各保留原有范围，不互相迁移结论。

## 原始资料实际读取

- [LookAtModifier3D 4.6](https://docs.godotengine.org/en/4.6/classes/class_lookatmodifier3d.html)：Description 的父骨/子骨顺序；relative、duration、origin、forward axis 和限制设置；两个 interpolation getter。文档的 Boolean 描述同时出现“运行”和零剩余的表述，不能只凭方法名构造成功条件。
- [SkeletonModifier3D 4.6](https://docs.godotengine.org/en/4.6/classes/class_skeletonmodifier3d.html)：父 Skeleton 绑定与 modification_processed 读取时机。本文没有实际 AnimationMixer，不能借文档把夹具变成动画混合调度验证。
- [Skeleton3D 4.6](https://docs.godotengine.org/en/4.6/classes/class_skeleton3d.html)：骨架空间 global pose、manual advance、skeleton_updated、reset_bone_poses。世界变换与骨架整体姿态不是一般同义；本夹具固定并记录单位世界变换。
- [固定 skeleton_3d.cpp](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/skeleton_3d.cpp)：311–432 的备份/修正/信号/恢复及延后 advance；908–950 的复位与延后标志；1152–1222 的直接子节点收集、顺序处理及 move_child 失效通知。
- [固定 skeleton_modifier_3d.cpp](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/skeleton_modifier_3d.cpp#L119-L124)：处理后发出信号。信号存在本身不证明瞄准成功，仍须查实际姿态。
- [固定 look_at_modifier_3d.cpp](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/look_at_modifier_3d.cpp)：383–389 两个 getter；515–606 读取父骨整体姿态与写回局部旋转；784–790 零时长初始化处理。只保留定位与原创分析，未复制第三方实现全文。

这些官方文档和固定公开源码是解释参照，不认证当前安装构建。自报 full hash 与公开标签比较提交不同，沿用[共享来源限制](godot-runtime-provenance.md)，不作官方构建、危险二进制或引擎缺陷判定。

## 实际接受与原始失败

[夹具](../experiments/godot-skeleton-modifier-order/README.md)公开冻结协议、五份源文件、作者和独立复验日志。作者首轮错误地增添 is_interpolating 必须 false 的判据，完整验收失败；源码/原始输出仍保留。随后仅移除该未冻结含义假设，保留 Boolean 记录与数值/几何判据，重新执行并独立复验。

总计三个行为进程尝试，每个包含两次手动顺序求值；其中两次完整接受，一次失败；另有三次版本查询。六项合成记录变异由两个 checker 在 normal/-O 下重复拒绝，属于六个不同记录案例，不是额外引擎场景。一次 -O 启动拒绝检查没有启动引擎。新运行器确实采用固定五位置 helper，但没有迁移或扩展旧 fresh harness。

[便携档案检查](../experiments/godot-skeleton-modifier-order/integration/check_archive.py)只核对归档，导入摘要固定的独立审查纯数值 oracle，不执行其带本机二进制读取的 main 分支，不启动运行器、子进程或引擎。它检查原始失败的几何记录仍一致，但绝不将其完整状态改为 PASS。已删除临时目录不重新访问，哈希一致也不证明历史执行真实性。
