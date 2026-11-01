# 资源释放与复用路由：作者范围记录

日期：2026-11-01。新产物为 `research/source-notes/resource-release-and-reuse-routing.md`，本记录拟归档 `research/audits/resource-release-routing/AUTHOR-NOTES.md`。无新增 solution / role ID；不编辑 CATALOG 或自动生成索引。

## 实际材料与版本

本次读取下列安全来源说明／指定 source-only 小节，并核对正文 SHA-256；未进入链接运行档案。作者参与过这些机制稿件，因此这是作者综合，不是全新的独立实现验证。

| 输入 | SHA-256 | 本次使用范围及其原始依据 |
|---|---|---|
| `research/source-notes/nativearray-copy-and-disposal-ownership.md` | `fc070bebc24debcb35551ef3936ae2d26914e03b11d959292f7a2de971fea856` | 全文；UnityCsReference 6000.0.0f1 固定 `0d0e6a11923ed73f1e8481eb5a6b2e67fe5ddc09` NativeArray.cs 字段／Dispose／释放 job；Collections 2.1.4；引擎 6000.0 CombineDependencies / Complete 文档，三者版本分别保留 |
| `solutions/engine/addressables-content-update-baseline.md` | `971f27e4c38c6da3f3e3b83440349ed161debbd635f508f21ff208119acc6092` | §4.1；官方 Addressables 1.21.21 LoadContentCatalogAsync 手册与 API，不采用 build-time state 文件作为运行时释放证据 |
| `research/source-notes/fmod-event-bank-teardown.md` | `42cbdf6cb4a30cf312db01f0937195ec8969370b6451da6cb0d44424464f0080` | 全文；FMOD 2.04.00 EventInstance、Bank、Studio API Guide；文档页脚 2026-09-29，不认证发行日或安装构建 |
| `solutions/audio/music-state-transition-contract.md` | `0fb9f95ae8070e74c803275dec6b54ca46ab4f0efd297cf680439f54ce4294cb` | 仅 source-only 场景退出段；不转移旧假端口模型、Wwise 或虚拟化证据 |
| `solutions/rendering/presentation-queue-latency-boundary.md` | `00e190d5737b3533a7996775f78b14439319f42aaed112f748ac189e30eb5023` | §1.1；Khronos Guide 固定 `82887e8444045655cc4578827e4183be9de593ff`，快照日期 2026-10-23；Vulkan 1.3.296 固定 `486e4b289053a7d64784e7ce791711843c60c235`，不扩展至任意提交 stage mask 或关闭路径 |

原始 URL 和精确函数／章节范围由上述链接材料保留，本路由不复制一轮长篇机制摘要。没有新的跨 SDK 执行证据，也不认证文档／源码与某个安装组合一致。

## 原创贡献与集成限制

四行路由用于拒绝丢失责任单位的 adapter；四项接收字段与 retire 队列反例均为原创未执行审查方法。它们不是公共状态枚举或完整销毁算法。FMOD 行明确其他使用者与产品尾部政策，单一 callback 不充当 bank 回收屏障；Vulkan 行只覆盖正常成功循环复用。

只新增 note 与本审查记录，以及由集成者确认的安全阅读索引链接。不得改动旧文章、自动生成元数据或编造 document ID。没有运行、私有归档处理或远端写入。
