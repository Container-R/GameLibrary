# Flipbook 双影：来源与试件

- Unity VFX Graph 17.0，[Shared Output Settings and Properties](https://docs.unity3d.com/Packages/com.unity.visualeffectgraph@17.0/manual/Context-OutputSharedSettings.html)：UV Mode、Flipbook Layout、Motion Vector Map 与 Motion Vector Scale。
- Unity Graphics 固定提交 `0efc28ea742b1966b9dd9cc4489e58b986a13faf`：包清单 `Packages/com.unity.visualeffectgraph/package.json` 标 17.7.0；同目录的 `Shaders/VFXCommonOutput.hlsl:3–15`、`Shaders/VFXCommon.hlsl:742–758` 给出先使用两帧纹理 RG、再偏移采样并插值的顺序。版本 17.0 的用户文档与 17.7.0 源码快照分别使用，不互作版本证明。不推断最终生成的全部材质变体、压缩、采样器状态。
- SideFX，[Labs Flipbook Textures 1.0](https://www.sidefx.com/docs/houdini/nodes/out/labs--flipbook_textures-1.0.html)，Motion Vector 的 Export Resolution、Motion Vector Encoding、Boundary Alpha、Padding Ratio 和 Max Speed Allowed。速度描述、专用高精度模式及材质过滤要求不能跨编码套用。未将其导出结果实际导入 Unity，也未承诺所有插件组合的转换关系。

[复现实验](../实验/烟雾帧间重投影/README.md)由作者以受控形状模拟透明度，目的分别是隔离采样偏移、没有时间对应和跨格串色。笔记中的 GitHub 源码未被实验执行。SVG 由同一二维试件生成并经栅格化目检。
