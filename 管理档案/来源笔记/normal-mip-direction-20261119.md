# 法线 Mip 与高光方向：来源与试件

## 原始资料

- Michael Toksvig，[Mipmapping Normal Maps](https://developer.download.nvidia.com/whitepapers/2006/Mipmapping_Normal_Maps.pdf)，NVIDIA 2004 技术简报/投稿，印刷页1–5：平均单位法线长度、方向变化的近似、Blinn–Phong 指数与强度修正。旧研究完整原文与图像核对另见 [normal-mip-specular-filtering.json](normal-mip-specular-filtering.json)。新稿没有把历史公式移植为 GGX 公式。
- Marc Olano、Dan Baker，[LEAN Mapping](https://userpages.cs.umbc.edu/olano/papers/lean/lean.pdf)，I3D 2010，§3.2–3.4（平均方向、可线性混合的二阶矩、协方差恢复与基础散布），另核对[作者勘误](https://userpages.cs.umbc.edu/olano/papers/lean/)有关 Beckmann 归一化的剩余事项。仅用于统计表示与模型边界；无作者图片复制或画质断言。
- Epic Games，[Composite Texture](https://dev.epicgames.com/documentation/unreal-engine/composite-texture?application_version=4.27)，UE 4.27 文档，设置、属性和 Issues 节：粗糙度通道、相同 UV 与法线尺寸、纹理留边、只有各向同性补偿。只是版本明确的构建端实例，无该引擎实跑。

## 自有推导与执行

等权法线的幂项为历史说明中的原创代数导入。新试件改用斜率对角线，使两组的平均单位法线（z²=2/3）、斜率均值、两个对角方差和迹都相同，只改变交叉项符号；投影到两个正交对角线时得到互换的方差。逐个纹素先算协方差再合并会得到全零，原始矩在同一线性权重下合并能保留这部分变化。

Python 3.12.14 的 [执行与输出](../实验/法线Mip斜率统计/README.md) 为可复算的精确分数，不读取纹理、不运行 GPU，不覆盖实际图片编码精度或画质/性能。正文的两个材质对照是部署前应执行的项目验证。

## 版本关系

此文将原支持说明移入正式目录并加深为方向性诊断。旧路径保留指向正式正文的入口，旧正文可在固定 Git 版本审阅；预算文章和 Journey 案例中本次直接读到的链接改指正式正文。
