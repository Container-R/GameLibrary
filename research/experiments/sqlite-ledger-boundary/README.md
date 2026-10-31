# 本地账本：进程退出/重开与提交后重试

## 实际结果

2026-10-31，Python3.12.14内置sqlite3、运行时SQLite3.53.1，四种场景跨十个实际子进程通过。全部使用单个本地数据库文件、DELETE journal、synchronous=EXTRA，且每连接读取回验；显式LEGACY_TRANSACTION_CONTROL+isolation_level=None，以SQL BEGIN IMMEDIATE/COMMIT/ROLLBACK控制事务。

| 场景 | 实际退出/结果 | 独立进程读取 |
|---|---|---|
| R的余额和receipt写入后，COMMIT之前 | os._exit(41)，记录in_transaction=true、事务内余额125/R数量1；没有RESULT_JSON应答 | 余额100，只有opening100，R数量0 |
| COMMIT成功返回后，调用者应答前 | os._exit(42)，记录in_transaction=false；没有RESULT_JSON应答 | 余额125，opening100及R25，R数量1 |
| 同ID与同payload重试 | duplicate，返回原balance_after=125 | 余额125，两条receipt，没有第二次奖励 |
| 同ID改amount为26 | payload_conflict | 余额与全部receipt不变 |

两个终止场景使用独立初始化数据库。opening不是凭空库存：account从0开始，以opening事件增加100并记录receipt。每次持久快照同时检查完整行集合、余额、sum(amount)、R数量及integrity_check=ok。不得把integrity_check正常理解成全部业务语义已经验证。

这是原经济模型的**存储边界补证**，不改变模型的成长数值或“真实玩家未测试”的结论。终止后新进程实际读取数据库，不是查询死进程留下的Python对象。

## 为什么提交后未应答更有价值

第二个场景中数据库已经提交，但工作进程未给出正常业务结果；调用者可能不知道是否成功。新请求使用相同event_id与相同payload时返回保存的原事件结果，而不再发25。这证明本例单DB合同处理了该明确的不确定窗口，不证明网络恰好一次、远程购买凭证或多节点事务。

账本中金额与幂等receipt必须属于同一事务。只持久化余额却漏receipt，后续重试可能重复发放；只持久化receipt却漏余额，重试可能永久跳过应发奖励。本夹具检查两者，未只看最终余额。

payload比较仅为amount/reason；ID范围为这一个数据库中的存档。作者四场景只验证改 amount 的冲突；后续独立补充检查另验证了 reason 冲突。生产可能需要saveId/币种/业务配置等，不能由这里推导万能幂等键方案。整数/bool/余额边界在应用入口显式检查，但本轮不是完整输入验证套件。

## 运行与证据

```
python run.py
```

每轮在results/下新建databases-*目录，旧数据库及journal不主动删除，以免失败后重跑破坏恢复证据。当前summary.json的database_directory指向本轮；旧目录不应混当本轮。每次读回均启动新worker进程，摘要记录十条实际命令与退出码。没有竞争写者、WAL或跨文件事务。

输出有CONFIG、CHECKPOINT、RESULT_JSON及独立解析JSON；checkpoint是测试观察日志，不是业务应答。固定exit41/42必须同时具有正确检查点，不能把任意非零退出算作成功模拟。其他异常/超时不生成PASS；runner先清旧summary再拒绝-O，并保留超时部分stdout/stderr。源hash、运行时身份与最终数据库hash在results/summary.json；数据库hash只标识归档，不要求不同运行生成相同字节。

### 构建身份

实际`sqlite_source_id()`：`2026-05-05 10:34:17 c88b22011a54b4f6fbd149e9f8e4de77658ce58143a1af0e3785e4e6475127e9`。这是库自报身份，不是独立构建认证。

本机_sqlite3的module spec.origin为built-in，没有独立__file__；/proc/self/maps未发现独立libsqlite3路径。本轮记录实际Python可执行文件SHA-256，而不编造动态库文件。最初假设_sqlite3必有__file__使元数据探针失败，尚未进入账本写入；原源码及错误输出保留historical-probe-failure/，最终已修正并完整重跑。

## 不应外推的结论

- 显式os._exit不会运行连接close/finally，但不是OS杀进程、OS崩溃、整机断电、磁盘撕裂或文件系统fsync验证。
- 小事务可能仍在缓存中；恢复成旧状态不证明本次实际走了某条热journal回放路径。我们未通过journal内部字节认定热日志，也不将所有journal存在都称为热日志。
- EXTRA配置按实际值记录，不保证底层硬件履行flush或锁合同；不声称断电持久性实测通过。
- BEGIN IMMEDIATE和单写者文档不等于本例验证了并发冲突、公平性、BUSY重试、性能或大存档迁移。
- 本地文件可修改；事务不是反作弊、账号授权或云同步边界。无真实货币、支付或远程权益测试。
- SQLite是此次可用的验证载体，不是所有游戏的存档技术推荐。

## 官方依据与版本范围

详细提案在proposal.md；访问均2026-10-31：

- [SQLite Transaction §2–2.3](https://www.sqlite.org/lang_transaction.html)：显式事务、写者与锁/BUSY边界。
- [SQLite Atomic Commit §1/2/4/9](https://www.sqlite.org/atomiccommit.html)：rollback journal机制及环境假设；不是本次断电实验。
- [PRAGMA synchronous](https://www.sqlite.org/pragma.html#pragma_synchronous)：EXTRA含额外目录同步，未知PRAGMA可能静默忽略，因此读取回验。
- [Python3.12 sqlite3 transaction control](https://docs.python.org/3.12/library/sqlite3.html#transaction-control)：显式LEGACY模式下isolation_level=None允许SQL事务控制。该滚动文档当时标题3.12.16，而实际运行3.12.14，不能称为精确安装源码匹配。

代码与有限场景均原创，无第三方存档数据。独立复跑仍是同机/同构建范围，不扩大为全部SQLite或生产游戏保证。

## 文本发布中的数据库证据

最终本轮目录为`results/databases-l2rwagl2/`，和summary.database_directory一致；早期`results/databases/`为更早运行的历史目录，不是当前证据。`database-artifacts/`包含本轮before.db/after.db的无损base64文本与manifest（解码字节数与SHA-256），不是SQL dump重建。原始二进制保留在draft；发布者可仅归档文本副本。

只在新建的临时目录解码，不覆盖现有存档；先核对manifest哈希再读取。例如从fixture根运行以下独立片段（仅重建证据副本，不是测试runner）：

```python
import base64, hashlib, json, pathlib, tempfile
src = pathlib.Path('database-artifacts')
out = pathlib.Path(tempfile.mkdtemp(prefix='sqlite-ledger-evidence-'))
for item in json.loads((src / 'manifest.json').read_text())['artifacts']:
    raw = base64.decodebytes((src / item['encoded_file']).read_bytes())
    if len(raw) != item['bytes'] or hashlib.sha256(raw).hexdigest() != item['decoded_sha256']:
        raise RuntimeError('artifact mismatch')
    with (out / item['filename']).open('xb') as f:
        f.write(raw)
print(out)
```

本次已实际检查两个base64的解码hash均与归档原文件一致；没有由SQL重建后冒称文件同一。最终文件是在恢复/查询之后保存，不是中断瞬间的数据库或journal快照。

## 独立审查与归档位置

[独立复核](review/README.md)在新目录重跑四场景、十个实际子进程，并以另一原始日志判据核对退出码、检查点、应答缺失及完整持久行集合。另一个独立进程执行十组补充检查：布尔/浮点/越界金额拒绝、余额界限回滚、reason 冲突、余额后来变化时返回原收据，以及 receipt INSERT 被测试触发器拒绝时回滚先前余额更新。十组不是十个额外终止场景，不代表完整输入或并发覆盖。

文本仓库省略原始二进制数据库目录，保留作者及审查者各自的 database-artifacts 无损副本。summary 中的绝对路径仍是历史运行位置，不要求检出后存在。初始 metadata 探针失败的源码与输出保留，空数据库未作为成功成果归档。集成者核对了四个 base64 解码摘要，并再次检查保存的原始日志；没有宣称第三轮十进程重跑。

后续独立扩展见[双写者握手](../sqlite-writer-contention/README.md)：只补 BEGIN 被拒绝后同请求重试序列，原退出/重开夹具与源码未改，不将两者范围混合。
