# Unity 子资产身份：来源与读者审查

2026-11-05。支持稿SHA-256 `4311436b2f4f6d21956d8bfeabba503c1601e7d79a1c7b89ab334dea120bee2a`；宿主只增加步骤2后的选读入口，原正文SHA-256 `1624509f7624dc2e170322157a81d4cebe6c381f45b57f19f4ce7bce14dd92c3`，当前为 `aca37f4a71d8c19337f16d7841ee09f1d287751bd8c1b8d0d2e10ebce39b1355`。既有Godot导入观察、LFS与URI等说明不变，不借用历史实验认证Unity行为。

独立完整读者视角审读及四项原始官方技术正文核对通过：Unity6000.0 Asset metadata、TryGetGUIDAndLocalFileIdentifier、LoadAllAssetsAtPath、AssetImportContext.AddObjectToAsset。版本网页可变，不是补丁源码或实测身份。GUID与局部fileID用于对象级引用，文件分组与单对象记录不同；对象重载须检查成功并以long接收，主资产不保证在数组0号。

门框/门扇与G、101、202是原创纸面例，非实际输出。自定义导入器的字符串identifier要求文件内唯一并为同一对象保持确定性，不等于数值fileID。列表顺序改变的例子只否定以当前位置证明语义身份，不推断具体内置导入器的编号或故障；保留meta仍需检查对象与内容。没有Unity、FBX、Sprite、跨机器导入或版本升级实验，没有自动改写引用或修复工具。

[支持稿](../支持资料/Unity里同一份资产为什么还要区分子对象.md)；[宿主](../../GameLibrary/技术美术/环境管线/资产导入/换一台电脑后如何保持资产导入结果一致.md)。
