# 几何高光足迹：来源与实测范围

- Tokuyoshi 与 Kaplanyan，JCGT 2021，[原论文](https://jcgt.org/published/0010/02/02/paper.pdf)：§4.2–4.3 与 Listings 1–3 区分切线半程向量的投影与斜率；Listing 2/3 的红色删除线不能照抄。§5.1–5.5 式 (10)–(13) 与 Listing 5 给出延迟几何阶段的替代估计及限幅；§6–7 区分测试结果与几何不连续限制。
- Google Filament [Physically Based Rendering](https://google.github.io/filament/Filament.html)，Roughness remapping and clamping：示例引擎把感知粗糙度平方映射为 GGX 粗糙度参数。不是对每个引擎槽位的约定。
- Khronos [GLSL 3.30](https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.3.30.pdf)，Derivative Functions：非一致控制流中的导数无定义。实验使用桌面 GLSL 330，Mesa llvmpipe。
- [实测](../实验/几何高光足迹/README.md)在相同无贴图解析形状和固定半程向量中逐样本对照。只记录 GGX D，不是完整光照；CPU 有限差分和实际 GLSL 导数分别存档。轮廓反例只对试件的法线延拓和解析覆盖负责。

调阅日期：2026-11-23（北京时间）。
