# 空间音频的瞬移与多普勒：来源记录

- OpenAL，[OpenAL 1.1 Specification and Reference](https://www.openal.org/documentation/openal-1.1-specification.pdf)，§3.5.2 Velocity Dependent Doppler Effect。声源与监听器投影、全局因子、声速及边界。正文的 343 m/s 是试件显式设置。
- FMOD，[Core API Reference: System](https://www.fmod.com/docs/2.04/api/core-api-system.html)，2.04，set3DListenerAttributes 与 set3DSettings。核对速度为世界单位每秒与距离换算；未测 FMOD，访问日期 2026-11-24。
- Unity Technologies，[AudioSource.velocityUpdateMode](https://docs.unity3d.com/ja/6000.0/ScriptReference/AudioSource-velocityUpdateMode.html)，Unity 6.0。固定或动态更新应贴合声源移动更新，不推断瞬移处理。
- [原生 OpenAL Soft loopback](../实验/空间音频的瞬移与多普勒/README.md)只使用恒定显式速度隔离基频，不能给任何引擎推断一帧属性实际持续多久。
