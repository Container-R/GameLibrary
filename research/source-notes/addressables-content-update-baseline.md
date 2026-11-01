# Addressables 内容更新：来源与适用性记录

核对日期：2026-10-31。对应 [SOL-ENGINE-002](../../solutions/engine/addressables-content-update-baseline.md)。本记录仅列来源定位与阅读范围，不保存官方全文、图片或大段翻译。

## 版本与方法

下列五篇均来自 Unity 官方 `com.unity.addressables@1.21` 英文文档，实际返回 HTML 的包元数据与标题标识 **1.21.21**。生成器日期 2024-05-16 不是已验证的包发行日期；版本化 URL 也不是不可变源码提交。此次实际读取正文，而非只读搜索摘要。行号仅指当次 HTML 文本视图，稳定定位优先使用章节标题；页面可能更新。

| 编号 | 官方页面与实际阅读章节 | 当次正文定位 |
|---|---|---|
| S1 | [Content update builds overview](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-overview.html)：引言、Content update build workflow、Content update tools、Build updated content、When to perform a full rebuild | 110–149 |
| S2 | [Content update build settings](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-settings.html)：Update a Previous Build setting、Group Update Restriction settings、Unique Bundle IDs setting | 110–172；精确缓存条件在 135–138 |
| S3 | [Build a content update](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-create.html)：输出说明、Update a Previous Build、Check for Content Update Restrictions tool | 110–148 |
| S4 | [Content update examples](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-examples.html)：假想静态/非静态分组示例及 implications；依赖示例起始部分仅作阅读背景，不据其声称完整依赖算法 | 110–270；措辞在 138、171，本地旧数据说明在 190 |
| S5 | [Check for content updates at runtime](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-check.html)：检查、更新与旧资产处理 | 110–124 |

## 保留的边界

- S2 与 S4 的静态选项措辞不同；未用不同版本页面消除差异，也未声称检查过安装版 Inspector。
- S4 明确是官方假想示例，不是生产案例或本库实验。正文只作短用途说明，没有照搬全套资产表。
- S2 所述远程缺失回退条件不能外推为所有 HTTP 故障处理。本次未读包实现，未验证具体错误码、缓存竞争或选择观测接口。
- S1 的代码改变与旧内容复用是有限条件说明；不能由包版本相同推导所有序列化内容兼容。
- 正文的摘要登记、输入交接、阻止晋级和 QA 表是原创建议。五篇文档没有为本项目实现“实际读取字节已认证”的机制；真实工具链的选择/读取观测仍待验证。

## 当前没有的证据

未执行 Unity、Addressables 构建、远程服务请求或旧版 Player 加载；未安装或探测本机 Unity 能力。没有构造 Python 替身来冒充包行为。邻近 Godot 导入、候选依赖隔离及同路径请求实验不适用于本次运行结论。需要合法可用的对应 Unity 项目和隔离托管环境后，才可执行正文的有限对照；未执行状态不能因来源审阅通过而升级。

## 2026-11-01 补充阅读：依赖消费者与输出粒度

保留上文 2026-10-31 的阅读记录：当时 S4 的依赖示例仅作为起始背景，未据其建立完整依赖算法。此次追加阅读不把原记录追溯改成“当时已完整核对”。

本次实际读取 [Content update examples — Content update dependencies](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-examples.html#content-update-dependencies) 正文与 HTML 表格（当次位置 272–387），覆盖单支、共享依赖及资产间引用链的官方假想示例；另重新读取 [Content update build settings — Unique Bundle IDs setting](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-settings.html#unique-bundle-ids-setting)（163–172）。并追加读取 [Content Packing & Loading schema reference — Advanced Options / Bundle Mode](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/ContentPackingAndLoadingSchema.html#advanced-options) 的配置行（238–239），仅用于说明组内打包模式需要记录，不据此扩展压缩、缓存或完整打包实现结论。三页实际包标识均为 **1.21.21**，不是不可变实现提交；未检查图片或包源码。

文章 §3.1 据此区分直接编辑、依赖消费者、检查后资产组织与最终 bundle/catalog。装备与共享纹理场景及接收表是原创、未执行的交接建议；没有把官方示例换名当作独立实验，也没有从资产数量推导输出文件或下载字节。具体迁组与输出保持未知，等待实际工具结果。

此补充不验证任意传递闭包、循环或隐式依赖的检测实现，也不把 `Unique Bundle IDs` 的 bundle 重建影响与限制检查的迁组混成同一机制。没有执行 Unity、构建、客户端加载或测量更新成本；原有运行证据边界不变。

## 2026-11-01 补充阅读：catalog 加载操作与不同缓存层

- [Manage catalogs at runtime](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/LoadContentCatalogAsync.html)：Load additional catalogs、Update catalogs（当次 HTML 114–140）。用于先前加载操作的释放要求与操作缓存复用，区分操作释放和已加载 catalog。
- [LoadContentCatalogAsync API](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/api/UnityEngine.AddressableAssets.Addressables.LoadContentCatalogAsync.html)：两种重载、bool 参数和 Remarks（117–235）。用于自动释放时点及 hash 参与的 catalog 缓存选择，不能脱离手册的操作缓存前提解读为无条件下载。
- 既有 [S5：Check for content updates at runtime](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-check.html)（110–124）的资产释放与 bundle 缓存清理边界仍有效；新补充不替换这些责任。

新增两页实际元数据均为 **Addressables 1.21.21**；`@1.21` 是版本化文档地址，不是不可变源码提交。未检查包实现。附加 catalog C 的再次加载情景、单一操作所有者及两个待验条件是原创未执行建议，不是已观察网络结果或厂商完整管理器。

本次不增加 Unity、服务请求、构建或客户端测试。没有把释放操作写成刷新 CDN、保证下载、自动替换资产或清空所有缓存，也未给出取消、并发协调或多引用者仲裁实现。既有构建基线、依赖打包与运行验收仍保留原适用范围。
