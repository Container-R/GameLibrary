# ICU证据runner的六个有限反向检查

2026-10-31。仅检查复制的runner如何拒绝坏输入，不是六次ICU行为测试。v1检查时，原fixture的case.py与run.py未改；inputs/保留其原始源，错误输出case使用原baseline.json作为静态伪载荷再改一个输出字段，不调用ICU。

当前v2运行：`python check.py`，输入为inputs-v2/。原始v1副本在inputs/、check-v1.py和historical-results-v1/。结果为`results/observations.json`与各case的harness.stdout/stderr、注入child、复制runner、其内部结果文件。`run-output.txt`为历史v1实际输出，`run-output-v2.txt`为当前v2输出。下面表格记录v1发现，不是v2结果。

| 检查 | 实际行为 | 旧PASS摘要 |
|---|---|---|
| python -O | 非零退出，Refusing -O；child未执行 | **仍存在**，内容仍为预置sentinel，无新PASS |
| child退出7 | runner非零退出，保留child stdout/stderr及returncode | 已删除 |
| 非JSON载荷 | JSON解析异常，runner非零退出 | 已删除 |
| 两个RESULT_JSON载荷 | payload count拒绝 | 已删除 |
| 载荷某输出改为WRONG | actual output拒绝 | 已删除 |
| child休眠2秒，复制runner timeout改0.05秒 | TimeoutExpired，runner非零退出 | 已删除 |

除timeout外，复制runner与原run.py字节一致。timeout仅用于验证失败分支到达，明确不代表原20秒阈值或ICU性能实测。每case开始都种入同样的旧PASS摘要，不能把检查后还存在的sentinel视为新成功。child标记文件证明是否执行；不只根据退出码猜测。

## v1实际发现

-O guard在ROOT/OUT构建及summary删除之前，所以拒绝确实早于case执行，却保留旧成功文件。原README“任何失败不留下新的PASS”仍可成立，但如果消费者只看到旧summary就当作本次成功，会产生证据歧义。建议将输出路径初始化和旧summary删除放到-O拒绝之前；这是源码变更，需保留历史后重跑真实四case并更新独立复核，不应偷偷复用旧源hash结果。

v1的另一个代码范围限制：其timeout except只保存异常文字，未保存TimeoutExpired携带的部分stdout/stderr。当前注入child没有输出，故没有观察到实际丢失内容，不能说这个无输出case验证了输出保全。若将其加固，应另以先输出再超时的有标记child验证，而不把该分支当成已经完整归档。

## 原始来源hash

- case.py `6305b982792337ccab59e0ae23237d2b834683408090e20365840bfa75702e45`
- run.py `09d317dbfaf41a0411c6d082221c03fa9ef96a760a86e7e5c7d6722ab3e3176c`

check.py结束再次检查inputs字节hash；v1检查时未修改原fixture；后续获准的v2改动仅在draft，始终未修改main staging。只证明声明的六个拒绝路径，不是fuzzer、恶意载荷安全证明或通用进程监督器认证。

## 获准的v2加固与实际重跑

v2把旧summary删除提前到-O拒绝之前；超时分支保存stdout/stderr（处理bytes/None）及含timed_out、timeout_seconds、returncode=null的命令记录。没有改动ICU调用或pattern。

实际再次运行六个负例：全部非零拒绝并移除预置旧PASS；-O仍未执行child。timeout仍是复制runner改0.05秒的分支测试，但child先flush两条标记再休眠；stdout与stderr标记均在结果文件中找到，并核对超时元数据。当前results/observations.json、run-output-v2.txt为证据。bytes路径由实际TimeoutExpired输出覆盖，None分支按代码处理但没有独立声称实测。

另外真实ICU四case已用新runner重新执行通过，结果在兄弟fixture目录，**不计入这六个runner负例**。新run.py SHA-256为3798aae09d1db0402116ed90b083d39d90b5783c548a6cce05068e14a9bf5eac；case.py仍6305b982…；原始四case源与结果保存在fixture/historical-runner-v1/，不覆盖原证据。当时等待新版独立复核；现已完成，见[独立审查](../review/README.md)。

v2负例harness自身也在入口删除旧observations.json，仅全部检查完成才写入本轮观察汇总；不是通用原子收据或整个结果目录清理保证，旧case文件可能保留，消费者不能把它们单独当作本轮完成。此加固后六case再次执行通过；harness SHA-256为942739f4c812c9645d6750841152f9beed447d4540dc75260ec9888134156378。

公开选择说明：当前六项负例保留原始输出和 observations；逐例生成的 run.py/case.py 不重复发布，由冻结 check.py 重建。v1 历史保留汇总与 optimized 的原始旧 PASS 反例，其余旧逐例输出省略；check-v1.py 与 inputs 保留用于复现。不要把历史目录当成当前完整结果集。
