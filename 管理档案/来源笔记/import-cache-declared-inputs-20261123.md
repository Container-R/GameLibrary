# 增量导入规则依赖：来源记录

访问日期：2026-11-23。

| 主张 | 一手出处和定位 | 工程边界 |
| --- | --- | --- |
| 只在设置缺失时赋值，不会自动替换已有设置 | Unity 6.0，[AssetImporter.importSettingsMissing](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/AssetImporter-importSettingsMissing.html)，Description | 优先级、默认或强制均由项目定义。 |
| Unity 区分静态与动态依赖 | Unity 6.0，[Refreshing the Asset Database](https://docs.unity.com/en-us/engine/6000.0/manual/assets-and-media/asset-database/refreshing)，Dependency tracking | 不推断自动发现目录之外的自定义策略。 |
| 自定义依赖应在导入之外更新注册，在导入上下文声明；刷新后生效；导入产物另有依赖接口 | Unity 6.0，[Managing importers with scripts](https://docs.unity.com/en-us/engine/6000.0/manual/assets-and-media/import-assets/scripted-importers#import-dependencies-and-determinism)，Import dependencies and determinism；[RegisterCustomDependency](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/AssetDatabase.RegisterCustomDependency.html) 与 [DependsOnCustomDependency](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/AssetImporters.AssetImportContext.DependsOnCustomDependency.html) | 这些是官方文档，不是本次 Unity 运行结果。 |
| 构建期间输入改变可能让缓存结果不正确 | Bazel 5.4.1，[Remote Caching](https://docs.bazel.build/versions/5.4.1/remote-caching.html#known-issues)，Known Issues | 模型单独演示原因；不将特定 Bazel 开关作为其它系统的通用解。 |
| 发现变更与缓存键是两层，需观察实际导入输出 | [GNU Make / Pillow 试件](../实验/增量导入规则依赖/native/README.md)；[缓存模型输出](../实验/增量导入规则依赖/cache-model-observed.txt) | 原创可复现材料；Make 验证基于文件时间的调度，模型验证键与有效值，不验证 Unity 引擎。 |
