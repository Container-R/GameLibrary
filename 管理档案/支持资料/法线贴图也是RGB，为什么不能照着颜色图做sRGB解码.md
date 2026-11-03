# 法线贴图也是RGB，为什么不能照着颜色图做sRGB解码

RGB 只说明数据分成三个通道，不说明这三个数一定代表颜色。同样一张图片，放进哪个材质槽位、采样后怎样解释，决定了它应走哪条处理路径。这里用 glTF 2.0 的三通道切线空间法线作例子，不给所有引擎指定同一个导入开关。

固定版 glTF 规范区分了两种用途：`baseColorTexture` 的 RGB 按 sRGB 编码，客户端应在与颜色因子相乘前反变换；`normalTexture` 的 RGB 则按线性传递函数编码，用来还原方向分量。后者不是一份还等着转换成线性光的表面颜色。[1]

设采样得到理想实数 `c=(0.5,0.5,1)`，法线强度 `scale=1`，暂不考虑量化、压缩和过滤。按 glTF 的映射 `n=2c−1`，得到 `(0,0,1)`；它表示不向切线或副切线方向偏转。一般还要按 scale 缩放 X/Y 并单位化，这里的默认值不改变结果。[1][2]

如果误先做 sRGB 解码，`D(0.5)=((0.5+0.055)/1.055)^2.4≈0.214041`，而 `D(1)=1`。[3] 随后即使照常执行 `2c−1`，结果也已经变成约 `(-0.571918,-0.571918,1)`。再除以向量长度，只会一起缩放分量，不会把两个非零负分量恢复为零。**单位长度正确，不代表方向仍正确。**

这个反例说明的是错误解释数据的后果，不是某张贴图或某个导入器已经出现了故障。0.5 是理想实数，不声称8位通道能精确存储它；本文没有采样 GPU、加载模型或比较画面，也不把近似小数当作设备精度保证。

排查时，应让模型、美术与渲染侧核对同一张纹理的实际用途、采样格式以及法线重建步骤。若引擎会重打包通道或重建 Z，就按那条实际路径检查，不能机械套用这里的三通道步骤。也不要反过来把所有 RGB 图都取消 sRGB 解释：基色纹理与方向数据的约定不同。修正这一处，仍不代表切线基、UV、压缩或光照都已正确。

## 参考来源

[1] Khronos，glTF 2.0 [材质与 Normal Texture](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#additional-textures-normal)，固定提交 `59ecbdba704206bb656965ab4e202881806066f1`。本次读取基色纹理段及完整法线纹理段，不称全文规范审计；保留基色客户端处理的 SHOULD 与法线编码的 MUST 强度区别。

[2] 同一提交的 [material.normalTextureInfo schema](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/schema/material.normalTextureInfo.schema.json)，完整读取，确认 scale 默认1及作用于重建后的 X/Y。

[3] Khronos，[*Data Format Specification v1.4.0* §13.3.1](https://registry.khronos.org/DataFormat/specs/1.4/dataformat.1.4.html)，sRGB EOTF。本次核对该公式；反例是据映射和公式作的原创计算，不是颜色库或渲染器实验。来源读取日期：2026-11-03。

[返回透明度与颜色处理正文](../../GameLibrary/技术美术/环境管线/纹理与材质/预乘透明度与普通透明度的混用问题.md)
