# Addressables 读者视角审读

2026-11-01。接受本次新正文及所述旧范围处置，未发现需返修的实质问题。这是文档审读，不是 Unity 更新测试，也不签署全库或上线安全。

## 绑定与独立性

- book.md：`21866802ceb109ab7990b3ce6c0abd4f6fb4828d446c499fb3f65d99b2bd1d31`
- scope-disposition.md：`9ab5f7f03521813aeec875b824032693bb1b1669b6f873d16649a25500dc7c79`
- 完整阅读 batch16 旧 solutions/engine/addressables-content-update-baseline.md：`971f27e4c38c6da3f3e3b83440349ed161debbd635f508f21ff208119acc6092`，与作者所列 batch22 旧稿字节身份相同。

我未写本次新正文，但曾参与旧稿依赖、catalog 所有权补充及关联构建书的作者工作。故本次为对另一编辑新稿的独立读者视角复核，不宣称对全部旧来源毫无先前参与。实际重新打开八份官方原源，而非仅信任作者报告。

## 读者能否辨认问题与行动

装备换纹理的开篇建立了旧客户端这一接收对象，随后先解释 Player、bundle、catalog。读者可据正文分清：选对原始发行输入，才能讨论这次更新；依赖变动决定需关注哪些内容，实际打包再决定文件；旧客户端实际加载仍另需检查。四步检查是建议而非既成结果，冷/旧缓存、未改内容和连续更新没有被一次成功吞并。

P/Q 例准确限定远程 state 缺失且缓存已有文件的条件，没有将超时或权限错误泛化。独立工作目录、摘要、构建成功均不被当成真实输入或兼容性认证。会话更新与启动加载分开；操作缓存、catalog hash 缓存、已加载资产、bundle 缓存及制作基线缓存的区别足够清楚。两种 bool 管理选择不鼓励自动释放后访问或重复释放；其他持有者与释放不保证下载也已交代。

文字有技术密度，但顺序能让开发者知道先找什么、下一步看什么及不能据什么下结论，没有以大表代替讲解。不要求为缩短正文删除真实机制。

## 本轮原源复核

重新读取正文列出的 Unity 官方 Addressables 1.21.21 页面，页面元数据与版本标识可见。最初网页输出含 HTML 导航，随后定位到正文，不把仅打开页面当作读完。

- [Overview](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-overview.html)：115、121–149，发行前远程目录、每平台归档、重复更新原基线与完整重建限制。
- [Settings](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-settings.html)：130–171，缺失回退、restriction、Unique Bundle IDs。文中没有把共存机制写成兼容证书。
- [Create](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-create.html)：117–148，输出引用、脚本限制、分支、依赖哈希局限。
- [Examples](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-examples.html)：138–190、264–387，旧本地数据与依赖传递；两装备不等于两个新包的原创建议与文档示例未混同。
- [Runtime check](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-check.html)：110–124，旧资产由调用方释放；未要求本书扩成缓存清理教程。
- [Packing schema](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/ContentPackingAndLoadingSchema.html)：238–239，实际 Bundle Mode；按主要资产分开的表述没有改成所有子资产一一分包。
- [Manage catalogs](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/LoadContentCatalogAsync.html)：114–140，操作缓存和 hash 缓存、更新前释放；操作释放不等于卸载目录。
- [API](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/api/UnityEngine.AddressableAssets.Addressables.LoadContentCatalogAsync.html)：175–203、230–235，带 bool 重载及 Remarks。没有推断未核对的默认重载实现。

## 旧范围和链接

旧§1–6及3.1/4.1全文已对照。基线登记/真实读取、分组依赖、输出引用、旧客户端负例与缓存条件、连续更新、会话释放、完整重建、成本及未证范围均有正文承接。三个保留支持入口确实到达旧技术标题，而非只在作者记录中口头保留：

- `#2-原创交接协议把选择结果变成可核对的证据`：细分责任与记录。
- `#4-旧版客户端验证最小有区分力的候选测试`：四类有限检查安排。
- `#41-手动加载附加-catalog先交代加载操作的所有权`：对象及操作持有条件。

按目标新书目录解析，三链接均退回仓库旧 solutions 文件；标题生成的锚点一致。构建新书链接也指向实际存在的同区域岗位书。精确支持保留是有效范围处置，不意味着可删除旧文件，亦不代表本次验证了支持中的未执行方案。未读运行附件、无新实验或远端写入。
