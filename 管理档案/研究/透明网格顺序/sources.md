# 透明网格优化：来源与主张

核读日期：2026-11-09。仓库研究基线为 e591e20fcaeb4f5522e2962e32b78dcf18efe0f7；候选只在本地准备。以下区分规范事实、源码事实、本文推导与运行观察。

## 合成和 API 顺序

1. W3C，2024-03-21 Candidate Recommendation Draft，Compositing and Blending Level 1，§5.1、§9.1.4。直接读取预乘颜色及 alpha 的 source-over 公式。支持正文两层展开；交换差 αAαB(UB−UA) 是本文推导，要求同一片段集合、输出及覆盖。来源：https://www.w3.org/TR/2024/CRD-compositing-1-20240321/#simplealphacompositing 。该来源不规定 GPU 图元执行。
2. Khronos Vulkan 1.3.296，commit 486e4b289053a7d64784e7ce791711843c60c235。drawing.adoc 743–789：索引绘制从低索引缓冲地址向高地址确定 primitive order。primsrast.adoc 462–521：同一 render-pass instance / subpass / sample 处的混合和颜色写入采用 rasterization order；默认 STRICT，AMD RELAXED 是显式例外。仅将规范用于普通三角形列表和严格路径，不推广到 mesh shader 或自定义存储合成。来源：https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/drawing.adoc#L743-L789 及 https://github.com/KhronosGroup/Vulkan-Docs/blob/486e4b289053a7d64784e7ce791711843c60c235/chapters/primsrast.adoc#L462-L521 。
3. Khronos OpenGL 4.6 Core，2022-05-05，§2.1 文内页9、§7.13.1 文内页160。直接读取 framebuffer 输出的图元顺序与 shader storage writes 次序区别。不据此宣称 shader invocation 串行执行，也不将 OpenGL 4.6 文档误当实验驱动版本。来源：https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf 。

## meshoptimizer 0.25

固定 commit：6daea4695c48338363b08022d2fb15deaef6ac09。

- README 的 Core pipeline、Vertex cache、Overdraw、Vertex fetch、Index buffer compression、LOD：cache/overdraw 交换三角形；fetch 在最终面序后整理顶点；triangle codec 可循环旋转角而不改变面序；共享 LOD 顶点域采用一致的 fetch 布局。https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/README.md 。本文据此提出按共享顶点域重映射，不把 LOD 推荐次序硬套成透明 draw 次序。
- src/meshoptimizer.h 180–241：cache/overdraw 各 draw range 分别处理；overdraw 必须接 cache 输出；threshold 1.05 是缓存效率限制；fetch 返回实际使用顶点数，多流使用 remap。https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/meshoptimizer.h#L180-L241 。
- src/vfetchoptimizer.cpp 全文：递增遍历索引位置，首次引用分配新编号，原位改写同一位置；没有面槽位重排。src/vcacheoptimizer.cpp 全文与 allocator.cpp 用于实验执行路径审查。保留完整流和所有引用是本文提出的语义条件，不是库替调用者扫描外部数据的功能。https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/vfetchoptimizer.cpp 。

## three.js r170 默认普通 WebGL Mesh

固定 commit：beab9e845f9e5ae11d648f55b24a0e910b56a85a。已读取完整有关文件并沿调用链核对。

- WebGLRenderer.js 1193–1201、1321–1417：建立列表、对象中心投影 z、材质数组按 groups 入队；单材质只入队一次。WebGLRenderLists.js 27–148：透明排序比较 groupOrder / renderOrder / z / id，非逐三角形排序。groupOrder 来自场景 Group.renderOrder，不是 geometry group 下标。
- WebGLRenderer.js 746–830、886–910、1583–1633：drawRange/group/index.count 交集，普通索引三角形绘制，以及 DoubleSide 透明两次剔除 pass。
- WebGLIndexedBufferRenderer.js 11–27：drawElements 的 offset=start×bytesPerElement。WebGLGeometries.js 79–107：属性更新未插入三角形排序。
- GLTFLoader.js 3568–3593、3748–3813、3865–3885：BLEND transparent=true/depthWrite=false；每个 primitive 建独立 Mesh/SkinnedMesh，多者返回场景 Group。

直接链接由正文来源[4][5]列出。源码用于描述默认实现，不代替用户自定义排序、BatchedMesh、WebGPU 或其他引擎行为的验证。合并对象会改变排序粒度是对已核查链路的推导。

## gltfpack 0.25 资产处理链

与 meshoptimizer 相同 commit，已直接读取这些版本文件，未运行完整 gltfpack。

- gltf/parsegltf.cpp 158–214：每个 primitive 建内部 Mesh 并保留 material/type/indices。
- gltf/mesh.cpp 210–276：兼容合并与拼接；不同 material 禁止合并，没有针对 alpha mode 的通用禁止分支。
- gltf/gltfpack.cpp 419–435：合并和滤空后处理全部 Mesh。
- gltf/mesh.cpp 1146–1176：triangle 路径调用 optimizeMesh，没有 BLEND 例外；958–985：cache/cacheStrip → fetchRemap → 索引与全部 streams remap，没有 overdraw 调用。
- gltf/material.cpp 590–619：factor alpha != 1 会保留 alpha；没有有效 alpha 的材质可变 OPAQUE。因此“输入 BLEND 一定输出 BLEND”不成立；保留 BLEND 的普通非空 triangle mesh 也不自动免于 cache。
- gltf/write.cpp 1125–1172、gltf/gltfpack.cpp 579–635：按内部 Mesh 的 indices 段建立 accessor 并写 primitive/material，物理 BufferView 拼接不等于一次 draw 覆盖全部段。

固定路径基础：https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/ 。核心直接行号链接见正文来源[8]。

## 实验与新增推导

运行观察详见 ../../实验/透明网格顺序/README.md 及 structure.json、raster.json。结构实验实际运行固定 meshoptimizer C++；离屏实验实际调用软件 OpenGL，不把 CPU 公式当像素。两面交换是显式正对照，未声称 cache 对该两面输入会换序。未运行 overdraw、完整引擎、真实 gltfpack 文件转换或 GPU 性能计时。

共享顶点域统一 remap、原始身份验收、并列排序风险与审批方法是本文根据接口/数据流提出的工程方法。结构负对照只覆盖一个具体错误实现，不能证明所有管线都以同样方式出错。
