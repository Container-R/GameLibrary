# 高分辨率 Mip 已加载，为什么这次绘制还是发糊

镜头停在一面墙前，纹理流送面板显示请求的层级已经到齐，墙上的砖缝却没有变清楚。把采样改成“固定取第 0 层”仍然发糊，也不能据此断定高分辨率层没有加载：**第 0 层是相对当前绑定的纹理视图说的，采样器也可能把请求的级别限制到更粗的一层。**

本文以普通二维 Mip 链为例，先核对该纹理请求什么、实际驻留什么，再定位可访问的视图和本次绘制的采样。本例不用虚拟纹理，也不把全局池的指标当作单纹理状态。

## 先把层数换成同一套索引

停住镜头，选定确实发糊的绘制及材质纹理槽。记录帧号、纹理身份、平台和质量配置；注意同一资产在另一种质量配置下可能绑定到不同资源。流送系统对这张纹理估计的需求、预算下实际发出的请求、当前资源持有的层数，以及着色器读了哪层，分别是不同证据。请求数和驻留数相等，只说明此时两项计数一致，不证明原始最细层可用；并且这两个数可能是零、尚不可用或只是另一个时点的快照。

在 Unreal Engine 5.5 的 `FStreamableRenderResourceState` 中，`NumRequestedLODs` 是当前请求完成后预期拥有的层数，`NumResidentLODs` 是资源当前拥有的层数。先确认资源已初始化；采用 `LODCountToAssetFirstLODIdx(count)` 把两者各自换算到资产索引。`RequestedFirstLODIdx()`、`ResidentFirstLODIdx()` 返回资源索引，不要跟资产索引直接相减。[1] 若从资产的 `GetStreamableResourceState()` 采样，记录游戏线程的采样帧；渲染资源的状态在渲染线程内一致，不能把前者无条件当作后者某次绘制的快照。若帧边界难对齐，先固定镜头采连续帧，直到目标与驻留不再变化，再与抓帧核对。[1][2]

例如某纹理资产有 0–8 共九层，某资源的 `AssetLODBias=2`，`MaxNumLODs=7`，因此这项资源至多覆盖资产 2–8。请求七层对应资源从 0、资产从 2 开始；驻留五层对应资源从 2、资产从 4 开始。这里“资产 0”是该构建中的资产索引，不一定等于源贴图的全尺寸层。如果稍后七层都到齐，这项资源的最细层也仍是资产 2；提高流送池并不能让超出资源范围的层出现。这个数字例用连续层表示，项目代码应使用对应引擎版本的转换接口。[1]

接着按看到的差异缩小范围：

- **需求先算低了。** 如果受控镜头下，构建给流送计算的 UV 通道与采样比例不符合材质的实际用法，先看该材质和网格的流送数据与精度视图，而不是加池。UE 的材质数据不是从所有采样表达式都能精确推导；例如有些程序坐标需要额外核对。[3]
- **需求与请求不同，或请求和驻留不同。** 前者先查预算、质量限额及优先级等约束；后者在同一资产连续采样，看是否有挂起、是否收敛。不能单凭差两个层就断言 I/O 慢。`STAT STREAMING` 可以解释全局压力，但其中的 Wanted Mips 不是单资产未受预算裁减的需求字段。[4]
- **资源有预期的层，绘制仍发糊。** 抓实际那一笔绘制，核对资源身份、绑定视图公开的层级范围、采样器的上下限和偏置，以及着色器的梯度或显式 LOD。驻留记录回答不了这些问题。

## 固定 LOD 0 不是最后一步

做一个不经过光照与后处理的诊断：同一纹理每级填不同颜色，颜色直接说明读到哪个**资产层**。把实际材质缩减到同一个纹理采样点，保持绑定和坐标，依次读取隐式采样、原采样器显式 LOD 0，以及仅更换为不限制 LOD 的中性采样器后的显式 LOD 0。这里的显式 LOD 用 `textureLod` 这类采样函数，不是直接指定纹素和整数级别的 `texelFetch`。替换采样器时保留过滤方式、纹理与 UV；若诊断材质会重建绑定，重新抓帧确认视图范围、相对基准和采样条件仍可比。最后查当前视图公开的第 0 层尺寸和层数。

在 Mesa llvmpipe 的 OpenGL 4.5 中，实际上传同一张 256×256 的九级纹理，用 OpenGL 纹理视图与采样器对象控制条件。着色器用最近层、最近纹素读取单一颜色；表里数字是由读回像素反推的资产索引，不是着色器写下的预期值。[5][6]

| 故意造成的粗采样 | 隐式采样 | 显式 LOD 0 | 中性采样器 + LOD 0 | 绑定视图第 0 层／层数 |
| --- | ---: | ---: | ---: | --- |
| 完整视图，采样器最小 LOD 为 2 | 2 | 2 | 0 | 256×256／9 |
| 子视图从资产 2 开始，采样器不限 | 2 | 2 | 2 | 64×64／7 |
| 完整视图，梯度选择粗层，采样器不限 | 2 | 0 | 0 | 256×256／9 |

三种情况正常采样都得到同一种颜色。原采样器下显式 0 已恢复，就去查坐标梯度、采样偏置或实际分支；只换中性采样器才恢复，就查有效采样器的限制；两次仍是粗层且视图基准已经变小，先查视图范围和实际绑定，不再反复改显式 LOD。项目中的图形 API、过滤、各向异性和偏置组合可能与试件不同，要以目标 API 的定义和实际抓帧为准。三线性过滤还可能同时访问两层。如果目标层在实验中可读、实际画面仍糊，继续排查纹理内容、压缩、后处理等，不把一切模糊都归给流送。

[软件 OpenGL 实验与观测](../../../../管理档案/实验/texture-streaming-wanted-resident/README.md)只改变已有存储的视图或采样方法，不观察引擎流送、GPU 内存提交或 I/O。池与 BC 空间的基础另见[计算 BC 压缩纹理和 Mip 链的数据量](./计算BC压缩纹理和Mip链的数据量.md)。

## 参考资料

[1] [Unreal Engine 5.5：FStreamableRenderResourceState](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/Streaming/FStreamableRenderResourceState?application_version=5.5)。  
[2] [Unreal Engine 5.5：UStreamableRenderAsset](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/Engine/UStreamableRenderAsset?application_version=5.5)。  
[3] [Unreal Engine 5.6：构建纹理流送数据](https://dev.epicgames.com/documentation/en-us/unreal-engine/building-texture-streaming-data-in-unreal-engine?application_version=5.6)。  
[4] [Unreal Engine 5.6：纹理流送指标](https://dev.epicgames.com/documentation/en-us/unreal-engine/texture-streaming-metrics-in-unreal-engine?application_version=5.6)。  
[5] Khronos：[OpenGL 4.6 Core](https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf)，§§8.2、8.11、8.14、8.18。  
[6] Khronos：[GLSL 4.60 的纹理查询与纹理查找函数](https://registry.khronos.org/OpenGL/specs/gl/GLSLangSpec.4.60.html#texture-query-functions)。
