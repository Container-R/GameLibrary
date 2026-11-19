# 循环根运动：来源和证据

- Epic Games [UAnimMontage::ExtractRootMotionFromTrackRange](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/UAnimMontage/ExtractRootMotionFromTrackRange?lang=en-US)，UE 5.8，Description：从连续 Montage 轨道范围取根运动，不能将整个 Montage 回绕或不连续 section 跳转伪装成一个调用的范围；为循环子动画或不同动画拆成步骤并按顺序处理，输出组件空间。未运行 UE。
- Godot [AnimationMixer](https://docs.godotengine.org/en/4.6/classes/class_animationmixer.html)，4.6，单次位移动量、混合位置值、循环相减可能跳变、manual advance 与 local 开关；[Using AnimationTree](https://docs.godotengine.org/en/4.6/tutorials/animation/animation_tree.html)，Root motion。文档提醒的回绕和大步跨多圈是不同问题；未从文档推断它一定忽略多圈。
- [Godot 最小实测及精确二维复现](../实验/循环根运动/README.md)。4.6.3 Linux headless 自报 7d41c59c4，构建相同不等于已验证官方源码或发行链；这不是渲染帧或完整角色模拟。分别存单次大步、分段总时长相同的结果；初始与结束相位相同的比较排除“只是最后姿势不同”。另用精确整数刚体变换验证非零初始姿势、循环末端、两段相乘和逆时间。二维参考不证明 Godot 对旋转的处理，也不模拟项目的碰撞、动画混合和 seek。
