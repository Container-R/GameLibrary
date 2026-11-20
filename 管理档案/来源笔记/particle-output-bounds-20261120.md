# 粒子输出包围盒：来源与适用范围

- Unity Technologies，[*Visual Effect Bounds*](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.0/manual/visual-effect-bounds.html)，网页元数据显示 17.0.4，2026-11-20 核对 Setting Bounds 与 Bounds Recording。Manual 可直接设置或用 Operator 接到输入；Recorded 可用 VFX Control，也可用输入覆盖。Update 阶段的计算限于 Automatic 或正在进行的 Recorded，Output 的 size、position、scale、pivot 不计入该帧的这个结果。Bounds Padding 按轴扩张；Automatic 强制始终重算与模拟。不据此断言其他引擎或只录一次的上界保证。
- 区间补边与仿射 AABB 为本文推导。对第 i 个输出轴，线性组合每项的极值分别为正负 abs(M[i,j])e[j]；固定盒覆盖全寿命和条件的要求来自保守剔除判据。
- 原创几何与图形试件见 [实验与读回](../实验/粒子输出包围盒/README.md)。剔除是自写 CPU 逻辑；Mesa llvmpipe 实际输出 64×32 RGBA8。代码不执行 Unity 或 Niagara 的模拟、工具或接口。
