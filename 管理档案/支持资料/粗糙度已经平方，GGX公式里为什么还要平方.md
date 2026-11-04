# 粗糙度已经平方，GGX公式里为什么还要平方

同一份材质换一条着色路径，高光形状却变了。先不要急着重画粗糙度贴图：两个接口都把参数叫作 roughness，并不保证它们接收同一种数。这里以固定版 glTF 与 Khronos 示例渲染器为例，只查材质参数怎样进入 GGX 分布，不诊断某个实际画面。

## 先分清三个数

glTF 的金属粗糙度纹理以线性传递函数存储，绿色通道提供粗糙度，再乘 `roughnessFactor`；没有纹理时，对应样本按1处理。把合成后的材质粗糙度记为 r。固定规范的微表面模型将它映射为 `α=r²`；后续 GGX 法线分布公式又包含 `α²`。[1]

因此，“线性存储”不意味着可以跳过平方映射；它说的是纹理数据解释，不是 GGX 函数的参数。这里的 α 也不是图片的透明度通道。

参考实现把这几个阶段分开命名：`getMetallicRoughnessInfo` 合成参数，`pbr.frag` 将 `perceptualRoughness` 平方为 `alphaRoughness`；普通各向同性直接光路径把后者传入 `BRDF_specularGGX`，再原样交给 `D_GGX`。最后一个函数内部才计算 α²。[2] **映射 r→α 与公式使用 α²，是两步不同的运算。**

## 用0.5追完一次传递

取没有粗糙度纹理、因子为0.5的理想输入，不考虑量化与数值误差。正确传递为：

```text
材质参数 r = 1/2
分布参数 α = r² = 1/4
公式中的 α² = 1/16
```

只看各向同性 GGX 的法线分布项 D。设 N 是单位表面法线，H 是光照与观察两个单位方向相加后归一化得到的半程方向，t=N·H，且0<t≤1、α>0，则：[1][2]

```text
D(t, α) = α² / {π [t²(α²−1)+1]²}
```

令 H 正对 N，即 t=1，分母中的方括号化为 α²，因而 `D(1,α)=1/(πα²)`。同一个原始0.5输入，由不同接线得到：

| 传入需要α的函数之前发生了什么 | 函数收到的α | 正对法线时的D |
|---|---:|---:|
| 按约定映射一次 | 1/4 | 16/π |
| 漏掉映射，直接传r | 1/2 | 4/π |
| 已得到α，又误把它当r平方一次 | 1/16 | 256/π |

第三行的错误发生在**函数入口之前**。第一行进入 `D_GGX` 后继续计算 α²，恰恰是公式所需，不能为了“不要平方两遍”把它删掉。

这些是同一分布公式的原创代入，不是像素亮度或反射能量比。D 只描述微表面法线的分布；完整画面还需要其他反射项、照明与显示处理。峰值不同也不表示所有方向都按同一比例变化，更不能据此判断完整反射模型是否能量守恒，或哪个渲染器更准确。

## 把接口约定写在交接处

排查时，可以列三栏：资产保存什么、材质接口接收什么、分布函数接收什么。为每一栏写清是 r、α，还是已经算好的 α²，再沿调用关系寻找转换位置。若目标材质入口接收的仍是 r，就不应提前把0.25冒充原来的0.5交给它；若直接调用接收α的分布函数，则由接入层完成一次所需映射。

不要仅凭名字含有 GGX 就统一替换参数。不同函数可以采用不同接口，规范也允许不同的光照实现；其示例实现部分是说明性的。[1] 本例只核对上面固定代码的这条路径，不覆盖其他引擎、各向异性、清漆、环境光预过滤或所有材质扩展。

零粗糙度需要单独处理，不能把α=0直接代入这里的普通函数。[1] 本例没有选定一个适用于所有项目的最小值，也没有编译着色器或比较画面。若真正的问题来自法线缩小后的信息丢失，应另读[法线Mip与高光过滤](法线贴图缩小后，高光为什么不能只靠重新归一化.md)，不要把参数换算当作过滤补偿。

## 参考来源

[1] Khronos Group，glTF 2.0规范源码，固定提交 `59ecbdba704206bb656965ab4e202881806066f1`。[材质段](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#metallic-roughness-material)、[微表面参数](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#microfacet-surfaces)、[示例GGX公式及零值说明](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#specular-brdf)。另核对同提交的材质schema。只阅读相关文字与公式，未查看或转载原图。所用规范源文件依[CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)授权，见固定仓库[许可说明](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/COPYING.adoc)；本文是解释与原创算例，不是Khronos发布的规范。

[2] Khronos Group，glTF-Sample-Renderer，固定提交 `df3e51cbea7b0843789be5c9fd27eaa8bb510d4c`。[参数合成](https://github.com/KhronosGroup/glTF-Sample-Renderer/blob/df3e51cbea7b0843789be5c9fd27eaa8bb510d4c/source/Renderer/shaders/material_info.glsl#L229-L243)、[参数映射](https://github.com/KhronosGroup/glTF-Sample-Renderer/blob/df3e51cbea7b0843789be5c9fd27eaa8bb510d4c/source/Renderer/shaders/pbr.frag#L134-L139)、[直接光调用](https://github.com/KhronosGroup/glTF-Sample-Renderer/blob/df3e51cbea7b0843789be5c9fd27eaa8bb510d4c/source/Renderer/shaders/pbr.frag#L400-L410)、[BRDF调用桥接](https://github.com/KhronosGroup/glTF-Sample-Renderer/blob/df3e51cbea7b0843789be5c9fd27eaa8bb510d4c/source/Renderer/shaders/brdf.glsl#L159-L165)与[D_GGX](https://github.com/KhronosGroup/glTF-Sample-Renderer/blob/df3e51cbea7b0843789be5c9fd27eaa8bb510d4c/source/Renderer/shaders/brdf.glsl#L93-L98)。这是源码阅读，不是运行验证。

来源读取：2026-11-04（UTC）。

[返回纹理与材质书架](../../GameLibrary/技术美术/环境管线/纹理与材质/README.md)
