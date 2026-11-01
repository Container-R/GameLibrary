# TASK122 独立来源审查

日期：2026-11-01。结论：**接受既有 §4 的有限深化；不认定原文错误。**

审查 gate SHA256：`d8ccf2f79c227d8439df5dab2f24891b43dba99cb641f35afb08e8460dc97020`。全文读取 `solutions/engine/addressables-content-update-baseline.md`，本轮只涉及其纯来源正文，没有打开相邻运行归档。

## 独立读取的官方来源

三个页面均成功直接打开，页面元数据标为 Addressables **1.21.21**；`@1.21` 是版本系列 URL，不是不变提交。生成器日期显示 2024-05-16，不将它当作包发布日。

1. [Manage catalogs at runtime](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/LoadContentCatalogAsync.html)：Load additional catalogs 114–121、Update catalogs 136–174。
2. [LoadContentCatalogAsync API](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/api/UnityEngine.AddressableAssets.Addressables.LoadContentCatalogAsync.html)：两种重载声明 117–123、175–181；参数 199–203；两处 Remarks 165–170、230–235。
3. [Check for content updates at runtime](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-check.html)：110–124，旧资产责任与可选 bundle 缓存清理。

## 核对结果

- 来源明确区分 catalog 加载操作缓存与 hash 控制的 catalog 缓存。先前同 catalog 加载操作未释放时，后续调用可复用该操作而不下载新远端 catalog；手动加载的 catalog 更新前也要求释放其加载操作。释放操作不等于卸载 catalog。
- API 的显式 bool 重载将 `autoReleaseHandle=true` 定义为完成时自动释放。另一个 `(string, string)` 重载没有该 bool；只据此文档不能声称它的默认值为 true，也不能把 `CheckForCatalogUpdates` / `UpdateCatalogs` 的默认参数照搬给它。建议正文使用明确 bool 的所有权选择，不依赖省略参数推断。
- 在进入相应加载流程的前提下，hash 未变可使用 catalog 缓存。释放旧操作只去掉一个复用阻碍，不能推出必有网络下载或最新内容；API Remarks 不应绕过手册的操作缓存前置条件解读。
- 旧资产释放仍由应用负责，未引用 bundle 缓存清理是另一操作；两者不能代替 catalog 加载操作的所有权收束。反过来，释放加载操作也不会自动替换已加载对象。

## 增量的实用性与边界

既有正文已正确分开 catalog 更新和旧对象处理，但尚未说明附加 catalog 的加载操作复用，故可在 §4 增加一个窄的前置条件表，而不另建泛化缓存文章。

“持有旧操作 / 已依所有权释放”两种条件与远端候选 catalog/hash 是原创待实施对照，不是网络结果。后续应核对 locator 和内容语义，不能把成功状态或第二次调用本身当作版本身份。

自动与手动释放是同一拥有引用的替代策略，不是在自动完成之后再手动 Release 一次；也不要让示例在自动释放后读取句柄结果。手册 Update catalogs 示例存在省略默认参数后又 Release 的写法，本轮不将示例照抄为已验证生命周期方案。若还有其他持有者，仅释放某个调用方自己的引用也不能擅自宣布所有先前操作责任已经结束。

不扩展取消、异常、并发请求仲裁、所有缓存键、CDN 一致性、签名、更新原子性或内容兼容性保证。正文和来源记录应增加本次阅读范围，而非覆盖先前分日阅读事实。无 Unity 运行、构建、下载测试或远端写入。
