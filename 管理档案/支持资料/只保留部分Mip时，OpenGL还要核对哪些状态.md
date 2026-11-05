# 只保留部分Mip时，OpenGL还要核对哪些状态

删去几级 mip 后，纹理数据量可以重新相加，但预算算对了，不代表新的纹理与采样设置已经匹配。OpenGL 接入者还应检查：实际定义了哪些级，以及这次使用纹理的单元最终采用哪种缩小过滤。

以下只看 OpenGL 4.6 Core 中，逐级定义图像的普通二维纹理，即 mutable storage。例子采用 RGBA8 规范化颜色格式，不是 BC 压缩资源；没有运行 GPU，也不预测具体故障画面。

## 改了纹理的过滤设置，为什么仍然不够

假设只正确创建并填入 level 0 的 64×64 图像，纹理的 `TEXTURE_BASE_LEVEL=0`、`TEXTURE_MAX_LEVEL=6`。若采用 mip 过滤，必要范围是 0 到 6，尺寸应依次缩小到 1×1；只定义第 0 级，不满足这里的 mipmap completeness，即 mip 图像链完整性。[1]

纹理对象自己的 `TEXTURE_MIN_FILTER` 即使已经设成 `LINEAR`，也不一定最终生效。如果同一纹理单元绑定了独立的 sampler object（采样器对象），且它的 min filter 为 `LINEAR_MIPMAP_LINEAR`，该单元采用的是后者，仍需要上述 mip 范围。[1][2] 因此，应沿实际绑定关系检查，而不是只查纹理对象。

## 根据保留意图选择修正

若仍需要完整链，就正确创建并填入后续各级，保证格式一致、尺寸顺序正确。不能只把完整链写进预算，也不能把尚未填好的图像当成有效内容。

若确实只想使用单级，可以让**最终生效的** min filter 采用 `LINEAR` 或 `NEAREST`。绑定了 sampler object 时，应调整或更换实际使用的采样器；只改 texture 的同名参数不会改变它。此时没有后续小图参与缩小过滤，仍需检查远处画质，不能把取消 mip 当成通用优化。

另一个选择是保持 mip 过滤，将纹理的 `TEXTURE_MAX_LEVEL` 设为 0。本例必要范围就成为 0 到 0，单级也能满足 mipmap completeness；“完整”不总是要求直到 1×1。[1] 但这没有生成较小图像，也没有补回它们原本提供的过滤内容。

若保留的是 0 到 2，就应定义 64×64、32×32、16×16 三个同格式图像，并让最大级与此匹配；只定义 0 和 2，漏掉中间的 1，仍不完整。

## 范围限制不等于内存回收

`TEXTURE_BASE_LEVEL`、`TEXTURE_MAX_LEVEL` 属于纹理对象，不是 sampler object 的参数；后者的 `TEXTURE_MAX_LOD` 也不能直接替代这里的最大图像级。[1] 修改范围或过滤不会替你创建图像、填入内容，更不能据此宣称已回收先前分配的显存。

通过 `TexStorage*` 建立的 immutable storage 另有按已分配级数限制范围的规则，不能套用本例“只定义第 0 级、却仍要求 0 到 6”的判断。整数、深度/模板、立方体和多重采样纹理也不在本例范围内。这里解决的是图像定义与采样状态的匹配，不代替内容质量、流送完成或物理驻留检查。

## 参考来源

来源阅读：2026-11-05。本文是规范规则的条件推导，未执行 OpenGL 示例。

[1] Khronos，*OpenGL 4.6 Core Profile Specification*，2022-05-05。§8.2（sampler 状态覆盖）、§8.14.3（必要级范围，印刷页264–266）、§8.17及§8.17.1（完整性与采样器，印刷页268–270）、表23.14/23.18（纹理与采样器参数）。只读取相关部分；范围判断采用§8.14.3的公式与§8.17的明确条件。[官方规范](https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf)

[2] Khronos，*glBindSampler*，官方 reference 的 Description。固定源版本 `4bdf67a73d040f79bd7b087f5c1e588809e1f329`，说明独立采样器覆盖与零绑定行为。[官方源文](https://github.com/KhronosGroup/OpenGL-Refpages/blob/4bdf67a73d040f79bd7b087f5c1e588809e1f329/gl4/glBindSampler.xml#L49-L61)

[返回纹理预算正文](../../GameLibrary/技术美术/环境管线/纹理与材质/计算BC压缩纹理和Mip链的数据量.md)
