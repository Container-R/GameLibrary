# 回池重播与迟到归还：来源与证据

- [Unity 6.0 ParticleSystemStopBehavior](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/particlesystemstopbehavior)：停止后保留粒子直至到期，或停止并清除现有粒子。不能推断自定义组件的收尾。
- [Unity 6.0 ParticleSystem.IsAlive](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/particlesystem/isalive)：核对存活/继续生成判据和 `withChildren` 的粒子系统范围。[AddSubEmitter](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/particlesystem/subemittersmodule/addsubemitter) 的示例明确展示死亡触发。均为文档核对，未运行 Unity。
- [Godot 4.5 GPUParticles3D](https://docs.godotengine.org/en/4.5/classes/class_gpuparticles3d.html#class-gpuparticles3d-signal-finished)：一次性 GPU 发射在完成信号后仍可能有短暂的属性重启限制；重开发射周期使用 `restart()`。本次未运行 GPU 路径。
- Godot 4.7.2 `ed1daf0bf`，[CPUParticles2D 源码](https://github.com/godotengine/godot/blob/ed1daf0bf/scene/2d/cpu_particles_2d.cpp#L319-L339) 重置时钟、周期及活动状态，[完成判断](https://github.com/godotengine/godot/blob/ed1daf0bf/scene/2d/cpu_particles_2d.cpp#L1192-L1197) 使用活动粒子状态。[类说明](https://github.com/godotengine/godot/blob/ed1daf0bf/doc/classes/CPUParticles2D.xml) 以持续处理解释非一次性模式；明确对其关闭发射后，本版探针仍收到一次信号，不用这一结果承诺其他版本、其他粒子实现或持续开启的发射器。
- [实验与原始日志](../实验/pooled-vfx-drain-restart/README.md)：真实 CPU 节点区分发射关闭与实际完成；真实引擎定时器制造业务通知的先后顺序。租用编号、互斥状态、多组件收尾和资源优先级是本文的工程设计，不归给引擎文档。模型粒子数不是引擎画面结果。
