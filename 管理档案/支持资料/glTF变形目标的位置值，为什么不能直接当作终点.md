# glTF变形目标的位置值，为什么不能直接当作终点

变形权重越大，位置却越不对？单个目标的 `POSITION` 保存的是**位移差（delta）**，不是终点。[1] 原位置为 `p`、位移差为 `d`、权重为 `w` 时，应算 `p+w*d`。

下面是原创纸面算例，不是运行结果：取 `p=(10,2,0)`、`d=(0,3,0)`。

| 权重 w | 正确：`p+w*d` | 错误：`(1-w)*p+w*d`（把d当终点） |
|---:|---|---|
| 0 | (10,2,0) | (10,2,0) |
| 0.5 | (10,3.5,0) | (5,2.5,0) |
| 1 | (10,5,0) | (0,3,0) |

错误式在零权重时也保留原位置，因此只查零权重抓不到**这一个错误**。

## 参考来源

[1] Khronos Group，glTF 2.0 Specification，固定修订 `59ecbdba704206bb656965ab4e202881806066f1`，2026-11-04读取。[Morph Targets：Overview](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#morph-targets-overview)、[Difference Data Storage](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#morph-targets-storage)、[Applying Morph Data](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#morph-targets-usage)。

[返回模型导入书架](../../GameLibrary/技术美术/环境管线/模型导入/README.md) · [读取glTF交错顶点数据时的偏移与步长](../../GameLibrary/技术美术/环境管线/模型导入/读取glTF交错顶点数据时的偏移与步长.md)
