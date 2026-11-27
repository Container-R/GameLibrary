# 粒子排序的作用范围：来源

- [正文](../../GameLibrary/视觉特效/特效制作/粒子渲染/粒子开了深度排序，为什么两团半透明还是会遮反.md)；[试件与读回](../实验/粒子排序的作用范围/README.md)。
- Khronos，[glBlendFuncSeparate](https://registry.khronos.org/OpenGL-Refpages/gl4/html/glBlendFuncSeparate.xhtml) 的 RGB 和 alpha 独立因子。在所有主试件中 source-over、透明深度只读、线性 RGBA16F、黑底；深度写入只在对照打开。
- Epic UE 5.5，[NiagaraSpriteRendererProperties](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/NiagaraSpriteRendererProperties?application_version=5.5) 的 Sort Mode 针对粒子，Sort Order Hint 作用于同 Niagara 系统内的同类型材质排序；[TranslucencySortPriority](https://dev.epicgames.com/documentation/en-us/unreal-engine/API/Runtime/Engine/Components/UPrimitiveComponent/TranslucencySortPriority?application_version=5.5) 针对透明 primitive；[MaterialTranslucencyPass](https://dev.epicgames.com/documentation/en-us/unreal-engine/python-api/class/MaterialTranslucencyPass?application_version=5.5) 区分景深前后等通道。必须核对实际材质所在通道，不推断引擎的私有命令构造。
- Unity 2022.3 [Particle System Renderer](https://docs.unity3d.com/2022.3/Documentation/Manual/PartSysRendererModule.html) 中 Sort Mode、By Distance、By Depth 与 Sorting Fudge。仅指内置粒子系统文档。
- 原创 Mesa 试件手工提交每面片，不读 Niagara 或 Unity 的自动排序，也不测实际项目、硬件和毫秒数。
