# SQLite REPLACE 与 UPSERT：独立专业全文模型审稿

日期：2026-11-12。结论：**通过**，限定于本文明确的普通父子表、成功语句和保留既有关联的选择任务。非真人试用、非学术同行评议。未参与初稿；不采用作者自评或旧审查结论。

## 审查对象与实际阅读

正文：`GameLibrary/引擎与工具/运行时系统/缓存与存档/SQLite REPLACE 与 UPSERT：更新存档时保留关联数据.md`。
全文 SHA-256：`83d72b02dcc978b5af609b5469778a80f678e9f053b294a0299a03cdc591dc17`。

已读当前技能、05-review、11-calibration、文章全文，以及实验包 README、完整协议、driver、runner、expected、输入清单、两份 output 和两份 result。直接重读 SQLite 官方滚动文档：

- https://www.sqlite.org/lang_conflict.html ：完整技术正文，特别是 REPLACE 与触发器段；页面更新 2025-11-22。
- https://www.sqlite.org/lang_upsert.html ：Description、Examples、Limitations、History；页面更新 2024-04-11；未检查语法图图像。
- https://www.sqlite.org/foreignkeys.html ：§2、§4.3、§6 第 3 项，并查看相关即刻/延迟约束文字；页面更新 2026-10-25。

这些来源分别支持冲突替换的删除步骤、定向更新和失败边界、外键配置及级联机制；没有将当前网页当成已执行二进制的来源认证。

## 独立判断及反例检查

1. 选题价值成立。父行编号和耐久完全正确却丢失从属词条，是备份校验之外独立的保存语义问题，不只是 SQL API 摘录。
2. 核心因果完整。第一节给出实际约束及外键开启要求，再解释删除旧父行如何删除子行，以及重新插入同键不恢复词条；第二节用同初始状态的目标冲突更新对照，未把已损坏分支上的 UPSERT 当恢复。SQL 目标与 PRIMARY KEY 一致，更新项不含父键。
3. 关键反例：若 UPSERT 改父键、引发触发器或违反其他约束，其结果不能沿用“词条保留”。正文明确限定更新列、无用户触发器和其他约束，并说明 DO UPDATE 的 ABORT 边界，因此没有泛化成 UPSERT 无副作用保证。
4. 另一反例：REPLACE 并非在所有外键动作下都删除子行，RESTRICT 可以阻止删除，NO ACTION 也不等同 CASCADE。正文以明确 ON DELETE CASCADE 教学结构推导，没有宣称所有关联都必丢；无需为该范围扩写全部外键动作矩阵。
5. 关闭 recursive_triggers 不能挽救本例。官方外键限制段与实际配置/输出吻合；正文正确区分用户 DELETE 触发器和外键动作。关闭 foreign_keys 不是合理修复，也已明确指出。
6. 方法足以支撑目标读者独立判断。例如同结构装备 52 拥有两条词条，要从耐久 6 更新到 7，应选择只更新 durability 的定向 UPSERT，写前后核对编号 52 的全部词条及耐久。只核对父行或保存成功不足；任一词条缺失都不满足保留既有关联的业务意图。基础 SQL 读者不需后台材料才能推导这一判断。
7. 没有把必要解释藏在管理材料中。正文包含结构、两条 SQL、前提、选择依据、验收对象和失败/版本限制；实验包用于复现而非补齐主论证。生产迁移、并发、恢复不在本文承诺内，不因未提供这些协议而否决文章。

## 实验材料审查

driver 的每个分支分别 connect(':memory:')；在建表和 BEGIN 前开启并读回外键。初始化显式 COMMIT 后采集基线，再运行一条保存 SQL，随后通过 SELECT/fetchall 实读父子行。结果没有从 expected.json 回填。保存与关闭完成点的位置合理；第一分支失败不继续第二分支。

runner 独立读取字面 oracle，验证输入摘要和复制前后字节，以新运行目录、有限环境及超时运行 driver；接受要求完整字段和类型相等、零返回码、无 stderr、确认退出及清理无错误。静态阅读没有发现可使该成功结果被错误判为合格的实质缺口。不是对 runner 全部异常路径的动态测试或安全认证。

两份原始 output 都包含各自两分支的基线、配置、保存完成、最终查询和关闭点。REPLACE 最终父行 [[41,9]]、子行 []；UPSERT 最终父行 [[41,9]]、子行 [[41,"frost"]]。两份回执均自报 Python 3.12.14 / SQLite 3.53.1、返回码 0、stderr 空及 PASS。实际以脚本核对两份 checkpoint 与固定预期一致、output 摘要与回执一致、artifact-manifest 每项大小与 SHA-256 一致。

两份输出和回执分别逐字相同与确定性记录形式相容，但不单凭相同字节证明历史上有两次执行。正文已经披露同环境、独立执行者先读作者结果及版本来源限制，未夸大为盲复现或跨平台验证。

## 材料字节绑定

下列路径相对 `管理档案/支持资料/SQLite替换关联行观察/`，均为本轮实际计算 SHA-256：

| 材料 | SHA-256 |
|---|---|
| README.md | 06fe2a4bbd340cfe982d25acf01061343692faafe5beaf7b6ca8211a9adb8b8d |
| artifact-manifest.json | 57994411be12b8a6bdcf1e3b6990701eaa5c46ebca098fe34def29cd0b096b33 |
| fixture/PROTOCOL.md | fd5ce9826cb1a8b9621c67524b5df78d24243fb4db3e890e22c97963cceda513 |
| fixture/driver.py | 1f20139d9eb4d2985142fdd1fd718294aadee42564327c0223a903cae3ad8307 |
| fixture/runner.py | dd4076a88aa15dd80989a24bec8e28a6837709a1c91dfa97653651e78928b4d2 |
| fixture/expected.json | 570d8c0786bbb59db7761abce6a95d56f76a4141f4c532dceaf24dca49d7b14a |
| fixture/manifest.json | e5961d67d7382f9bbc44506fbd2754aa9ad86e210ab923128aecbb98bbcf4de2 |
| observations/author-1/output.json | 7c0ba9c782e07b76bf1914065c9739e4f01efb5b15d8703c97c6a6258b8c0e96 |
| observations/independent-1/output.json | 7c0ba9c782e07b76bf1914065c9739e4f01efb5b15d8703c97c6a6258b8c0e96 |
| observations/author-1/result.json | 05882f4c40af6077a50c40043dcdd41825bcbb79219e8ca41b005a5596b0fd89 |
| observations/independent-1/result.json | 05882f4c40af6077a50c40043dcdd41825bcbb79219e8ca41b005a5596b0fd89 |

## 未执行与责任边界

没有重新执行 SQL 实验，没有执行 driver 或 runner，没有故障注入、真实游戏接入、磁盘持久性、并发或引擎包装器测试；本轮是全文机制、来源和既存材料独立审查，而非第三轮复现。未独立核验 1373a74f 远端树及所谓编辑前逐 blob 同一性，当前工作目录不是 Git 仓库，远端版本校验归集成检查。未执行根入口导航审查。未修改候选正文、代码、输入或输出，未远端写入。

无阻断性修订意见。该判断只绑定上述正文与材料字节，不自动覆盖后续技术改写。
