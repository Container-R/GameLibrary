# 单纹理流送状态与绘制采样：来源记录

- Epic 5.5 [FStreamableRenderResourceState](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/Streaming/FStreamableRenderResourceState?application_version=5.5) 与 [UStreamableRenderAsset](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/Engine/UStreamableRenderAsset?application_version=5.5)：请求和驻留是层数；资源 LOD 0 可对应非零资产 LOD；资产缓存与渲染资源状态的线程一致性不同。数字例为连贯层假设，不是 Unreal 运行结果。
- Epic 5.6 [流送数据与精度视图](https://dev.epicgames.com/documentation/en-us/unreal-engine/building-texture-streaming-data-in-unreal-engine?application_version=5.6) 与 [全局统计](https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-streaming-metrics-in-unreal-engine?application_version=5.6)：区分场景流送输入、需求、计划、完成；不把全局 Wanted Mips 当成某一纹理的需求字段。
- Khronos [OpenGL 4.6 Core](https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf) §§8.2、8.11、8.14、8.18；[GLSL 4.60 纹理查询](https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.html#texture-query-functions)。底层纹理存储、视图公开的层与采样 LOD 限制属于不同状态。实验用 Mesa 4.5 Core 而非完整 UE 渲染路径，目的是验证三种选级诊断的对照。
- [实验记录](../实验/texture-streaming-wanted-resident/README.md)：真实软件 OpenGL 输出，改变已预先上传的资源如何被访问。没有运行 Unreal，也没有做显存或 I/O 的性能测试。
