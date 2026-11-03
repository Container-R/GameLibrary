# EnTT 更新通知三条件：v2执行前闭合

2026-11-03。**接受当前有限协议与实现，三项v1拒稿理由已闭合；可交主编另行决定一次固定协议执行。** 本报告本身未执行或自动授权原生程序。

## 最终绑定

- INPUT-MANIFEST.json：`65186c150b7bd98a96dcec89a6c9395d597a605395e7f56e5bc6a33b5f1740aa`
- PROTOCOL.md：`1014c0eb8ea178fef45850be8e0e9a3a69215ce55d034ddfb8f72191daebdd2e`
- runner.py：`172bc276a9f2ff18a0ec302149564b0d12d68ed90a6b45bb68b146caf83fc8fa`

清单全部七文件实际摘要再次匹配。fixture、checker、expected、头文件及LICENSE与v1身份不变；fixture、checker、expected还与history/v1逐字比较。旧清单原样保留为 `4b04b18d370dab64541d7da4498a0a32c36b44343476427c1a08006f2f16296a`，原PRE-REVIEW及初版纯反例不覆盖。

## 有限修订实际闭合

全文对照旧/新runner与协议。三条件、编译argv和60/10秒阶段预算不变。

1. TERM/KILL及leader有界wait后，最多31次查询原拥有进程组是否存在、间隔0.1秒。ProcessLookupError结束确认；持续存在、权限或其他错误留下收尾错误并阻止接受。纯mock覆盖持续存在31次、已不存在、PermissionError三支。循环次数和等待有限，但不是严格实时调度上界，也不是沙箱、所有任意后代消失或全系统审计。
2. `check_bound`在复制后、build后、native后且导入checker前及最终阶段核原输入、副本和启动manifest身份。原反例再次在临时复制checker追加无害标记代码，现于导入前拒绝，标记文件没有创建；不是仅最终拒绝。
3. manifest以启动原始字节摘要冻结；原反例在mock build中将来源清单改为`{}`，现于build后拒绝，未继续mock native。最终receipt不再pass。正常无修改的mock路径前后manifest摘要相等。

协议开头另移除内部选题稿依赖，指向包内来源描述与固定官方链接；不扩大源码阅读或实验覆盖。没有因修复更改三条件的字面结论。

## 实际纯检查

`independent/test_preexec_v2.py` SHA256：`3f941daf3b9f0729edaa70f50430eb0c447d6bf1f2b41fa6ab9187b3c08498a9`。

普通模式8方法完成：严格类型/重复键/缺额外行/非有限数/坏oracle/非空stderr；mock启动失败、cleanup错误、日志写失败；组确认三分支；manifest篡改；复制checker篡改且禁止导入；正常mock路径前后绑定及旧目录拒绝；receipt.pending写失败时不发布正式receipt。完整原始输出存 `independent/v2-pure.stdout` 与 `v2-pure.stderr`。

`-O`只重复消费者正反例1方法，存 `v2-consumer-optimized.stdout/stderr`；runner本身按合同拒绝-O，未将全部mock方法在-O下运行，也没有把两模式当不同原生覆盖。

全部Popen/信号与整次模拟的command为mock；临时文件只用于纯文件身份、解析及发布顺序检查。测试中PASS字符串来自合成mock路径，不是EnTT原生结果。本轮零编译、零fixture启动、零真实进程信号，无安装、网络或stage/远端修改。

## 保留结论

三独立registry、真实回调读值、具名连接寿命、输出实际观察后再检查及首错停止的静态结论沿用PRE-REVIEW，未被修订破坏。消费者只确认三行是否匹配字面表；后续实际接受还须runner外部退出0、正式receipt pass以及前后身份成功。没有结果前仍不能声称三条件已原生验证，更不能推为所有字段写入通知、所有缓存一致或线程安全。
