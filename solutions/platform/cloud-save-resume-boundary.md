---
id: SOL-PLATFORM-001
title: Steam 动态云同步恢复时的存档写入隔离与冲突契约
type: solution
status: source-backed
primary_discipline: PLATFORM
related_roles: [platform-programmer, gameplay-programmer, qa-engineer]
related_topics: [cloud-save, suspend-resume, revision-lineage, asynchronous-io, conflict-recovery]
engines: [engine-agnostic]
versions: ["Steamworks 滚动在线文档，2026-10-31 访问；未锁定 SDK 二进制版本"]
updated_at: 2026-10-31
verification_method: Valve 官方中英文文档核对；原创串行内存模型20项状态测试及1项独立失效反例；未做Steam、文件系统或真实挂起恢复集成测试
sources:
  - https://partner.steamgames.com/doc/features/cloud
  - https://partner.steamgames.com/doc/api/ISteamRemoteStorage
  - https://partner.steamgames.com/doc/features/cloud?l=schinese
---

# Steam 动态云同步恢复时的存档写入隔离与冲突契约

## 具体故障

设备 A 的游戏仍在内存中持有存档 a，挂起后玩家在设备 B 继续到 b。A 恢复时磁盘已经变为 b，但旧自动存档工作仍把 a 写回去。用户看到的不是“云没同步”，而是**同步成功之后被过期进程状态覆盖**。本方案研究单用户单存档槽的应用侧隔离契约；不实现云服务、不配置真实 Steam App，也不宣称支持全部引擎的恢复时序。

## 文档证据与未获保证

Valve 的 *Dynamic Cloud Sync* 描述：恢复前下载其他设备的变化，再通知存活进程；API 和 Auto-Cloud 都适用。文档警告，为不处理相关回调的旧构建全量启用可能丢失数据。[S1]

`RemoteStorageLocalFileChange_t` 表示本地变化；通过 `GetLocalFileChangeCount/GetLocalFileChange` 枚举已发生的更新或删除。路径类型区分 Auto-Cloud 的绝对路径和 RemoteStorage API 相对文件名。`BeginFileWriteBatch/EndFileWriteBatch` 是关联写操作的提示；异步写完成结果描述本地写成功，不等于跨设备已可见。[S2]

以上 API 事实不提供应用内锁、文件系统事务、断电持久性或业务冲突自动合并保证。以下状态机、版本链和失败策略均为原创工程提案，不是 Valve 的内部实现。

## 应用状态与数据契约

一个存档协调器独占生产存档写入口；自动存档、手动保存、退出保存、后台工作线程都不可绕过。状态为：

`Ready → Quiescing → Reloading → Ready | Conflict | Recovery`

- `Ready`：允许产生存档意图；只有当前写代次的任务可进入真实写入层。
- `Quiescing`：关闭新写闸门，增加 `ioEpoch`，使旧排队任务失效；确认真实 I/O 的在途状态。
- `Reloading`：读入独立候选对象，校验身份/格式/完整性，不就地覆盖游戏对象。
- `Conflict`：两个有效分支均需保留，等待明确产品规则或玩家选择。
- `Recovery`：删除、不兼容版本、读取失败、损坏或无法建立安全边界；禁止自动创建默认存档覆盖现场。

建议持久信封包含 `accountScope, slotId, schemaVersion, revisionId, parentRevisionIds, payloadDigest, payload`。新 revision 使用唯一身份；不能用两台设备各自递增的 `revision=42` 冒充全局顺序。父版本表达因果关系，摘要验证内容一致性；本地时间、游玩时长仅辅助解释，不独立裁决谁更新。签名/账户认证另有信任边界，摘要不是反作弊。

## 恢复处理顺序

1. **先隔离，再重载。** 将本地文件变化通知送入协调器串行执行域，关闭写闸门并提升代次。生命周期恢复路径也应触发检查。集成时必须验证：恢复后的自动保存/工作线程不能抢在通知处理之前落盘。不能把“主线程下一帧会跑回调”当作已证明的屏障。
2. **处理实际在途写。** 尚未调用写 API 的旧任务直接拒绝；已经提交给 OS/Steam 的写入不能靠丢弃完成回调取消。必须在具体 I/O 层验证完成、取消或隔离方案；若无法保证不覆盖同步目标，保持停写并进入恢复流程，不能宣称代次令牌解决了竞态。批次提示不能替代这一步。
3. **枚举变化并定位槽。** 复制需要的描述信息，按路径类型送入对应读取适配器。只处理受管理的账户/存档根，规范化后映射槽；未知路径或类型记录诊断。删除作为独立事件，不解释成“读取空值所以新建默认档”。多文件槽先读取清单与全体依赖，避免把一半旧数据、一半新数据发布给游戏。
4. **校验候选。** 检查账户与槽、支持的 schema、大小界限、摘要、必要文件和游戏不变量。加载任务携带 `(ioEpoch, accountScope, slotId)`；完成时任何一项已改变都丢弃该结果，不能让旧槽的慢读取切回当前槽。完成前再次确认候选版本仍对应当前磁盘视图；普通先读后比较并不构成文件系统 CAS。
5. **按因果关系决策。** 内存无未保存改动且候选是基线后代，可加载并重建依赖系统；相同 revision 且内容相同可幂等忽略。相同身份却不同内容进入恢复。内存脏、兄弟分支、缺少祖先证据均不能仅看时间自动胜出。
6. **接受后再开闸。** 新游戏状态、已加载基线 revision 和依赖缓存切换成功之后，才重新接受存档；下一次存档从新基线创建子版本。旧工作完成回调只记录诊断，不得将新状态标记为已保存、清掉新 dirty 标志或重新打开写闸门。

## 冲突、离线与产品选择

这些策略需要产品、存档工程和 QA 共同定义，不是 SDK 默认保证：

| 情况 | 保守处理 | 不应做的事 |
|---|---|---|
| 干净内存，可信直接后代 | 校验后载入；关卡无法热切时回到安全加载界面 | 仅修改存档对象而保留旧场景/任务缓存 |
| 两个有效分支 | 保留双方版本、摘要和上下文；选择分支或执行明确领域合并 | 全字段取最大值；货币/任务标记可能互相矛盾 |
| 有本地未保存进度 | 先保护独立恢复副本，再询问或按已说明规则分叉 | 为了“清空队列”先把旧内存写回同步槽 |
| 删除或未知 schema | 保留诊断/备份，明确兼容或恢复流程 | 自动生成新档使删除或升级问题不可逆 |
| 离线继续游戏 | 从当前基线创建独立分支，保留因果记录；重联重新比较 | 假设离线时间较晚就应覆盖所有其他设备 |
| 冲突选择窗口又收到变化 | 使旧决策令牌失效，重新展示最新候选 | 旧弹窗确认覆盖第三个新版本 |

恢复副本应放在项目明确的独立恢复区域，避免自动云匹配规则把“备份”当主档同步；控制容量、保留期限和个人数据。实际备份成功前不能声称双方已安全保存。分支选择的提交也要经过同一个写闸门，保留未选版本的可恢复性。Steam 层可能已有文件冲突处理，不能假设应用必定能取得所有历史云分支；本文仅处理当前可取得的本地/内存候选。

## 原创模型与验证边界

配套实验目录：`research/experiments/cloud-save-resume/`，仓库根目录运行 `python3 research/experiments/cloud-save-resume/test_cloud_resume.py`。2026-10-31 实际执行 **20 项状态/保护测试通过**：旧排队写隔离、干净快进、脏分支保留、旧加载结果拒绝、删除不重建、不兼容格式停写、抽象无通知磁盘变更、重复通知幂等、兄弟分支冲突、同 revision 内容改变、关闸拒绝编辑、同基线任务只执行一次、加载期间磁盘再变；新增派发前同 revision 异内容的无变更拒绝、祖先身份重用拒绝、已排队/已观察身份重用拒绝、身份类型检查、身份登记容量耗尽，以及入站祖先 ID 循环和已预留身份冒用拒绝。

审查发现初版仅检查 revision 的派发闸门会覆盖“同 revision、内容已改变”的磁盘候选；现改为与已加载基线完整对象比较，回归测试断言拒绝时协调器全部字段不变且候选保留。身份分配使用最多256项的教学登记表，拒绝重用已知/已预留身份，容量满则停写而非驱逐旧身份；入站候选若复用已知/预留的非当前身份则保守进入恢复，防止 a→b→a 被伪装成快进；重复冲突候选也可能需人工恢复。跨设备、跨进程唯一性仍由调用方负责，不是完整版本图验证。

模型只使用串行方法调用及不可变整数存档对象；“磁盘”是内存字段。只实现直接父版本快进，未知祖先关系保守冲突；恢复副本仅在内存，未实现玩家选择。测试假设通知失效处理先于后续派发，未测试这项真实平台前提。未覆盖多线程、已经派发的 I/O、崩溃恢复、账号切换、真实磁盘错误、云上传或 Steam 集成，因此整篇仍为 `source-backed`，不是平台验证报告。

另有独立反例 `test_inflight_counterexample.py` 实际执行1项：人为令已派发的旧写在新下载后生效，即使丢弃旧完成令牌，磁盘仍保留旧内容。此测试断言的是**失效确实可在该假设交错下发生**，不计入20项保护测试，不声称模拟了真实 Steam 调度。

真实项目的下一验收必须记录 SDK/header 版本、Steam 客户端构建、OS、存档格式与应用构建；在受控测试账户和可丢弃存档上覆盖：A 挂起/B 保存/A 恢复、两端离线分叉、恢复即自动保存、回调延迟、在途写、删除、损坏、磁盘满、重复恢复和旧客户端。比较最终内容及版本链，而不只看“云同步成功”图标。官方本地测试流程可以辅助复现，[S1] 但本研究没有执行这些命令，也未改动任何 App 配置。

## 来源记录

- **[S1] Valve / Steamworks Documentation — Steam Cloud**。定位 *Dynamic Cloud Sync* 与其后的 *Pre-release Testing*；访问 2026-10-31。滚动文档未呈现可锁定 SDK 版本，不冒称具体版本。<https://partner.steamgames.com/doc/features/cloud>
- **[S2] Valve / Steamworks Documentation — ISteamRemoteStorage Interface**。定位 `RemoteStorageLocalFileChange_t`、`GetLocalFileChangeCount`、`GetLocalFileChange`、`ERemoteStorageFilePathType`、`BeginFileWriteBatch/EndFileWriteBatch`、`RemoteStorageFileWriteAsyncComplete_t`；访问 2026-10-31。同为未锁定版本的在线 API 文档；需与项目实际 headers 二次核对。<https://partner.steamgames.com/doc/api/ISteamRemoteStorage>
- **语言交叉检查**：Valve 简体中文《Steam 云》“动态云同步 / 预发行测试”，访问 2026-10-31；与英文同源，不计独立证据。<https://partner.steamgames.com/doc/features/cloud?l=schinese>

未引用第三方实现代码；实验为原创。中英文发现关键词：`Steam Dynamic Cloud Sync resume stale save` / `Steam 动态云同步 挂起恢复 存档覆盖`。

## 关联知识与复核

[独立失败与修复复核](../../research/audits/cloud-save-adversarial-review.md)保留发布前发现的反例；[经济事件账本](../design/single-player-economy-ledger.md)说明经济事件幂等不自动等于持久存档事务。
