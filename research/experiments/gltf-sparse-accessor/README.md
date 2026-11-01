# 有限 glTF sparse accessor 表示实验

44字节原创数据，FLOAT SCALAR count4，两种基底：密集10/20/30/40与无view零初始化；索引1/3替换为7/9。预冻结协议在protocol.md。最终reader f4236fac、runner a1364f54，全文摘要见SHA256SUMS和summary.sources。

## 真实执行与复现

作者命令 `python -B run.py`；审查者在独立复制目录执行 `python run.py`。各2个正配置、5个内存直接拒绝用例，均退出0、stderr为空，源码before/after一致。同样7种用例跑2次，不是14种情况。作者author-execution/与results/；独立review/independent-repeat/execution/与results/。标准库CPU，不调用引擎、DCC、官方validator或外部原生探针。

在一次性目录复制reader.py、run.py、protocol.md，然后执行 `python -B run.py`，会写results/中的两份JSON和summary。不要直接在归档目录覆盖历史输出。运行前runner清掉旧summary并拒绝-O，代码审查了该行为，本次没有新增启动失败探针，不能借用旧密集夹具的负例宣称此runner实际通过相同故障测试。仍需核对真实退出状态，不以遗留JSON单独认证执行。

独立oracle在作者实现检查前冻结；review/independent-oracle/check.py没有导入作者reader。对每份结果执行：

```
python check.py ROOT --stdout STDOUT --stderr STDERR --exit-code EXIT --source-pins source-pins.json
```

路径分别指向作者或复跑证据。审查者2次静态检查，主整合者另2次静态读回，不增加解码用例。静态检查比较完整输入/字面值/地址/7条日志和摘要关联，不提供执行身份认证。负例变更后的完整输入未逐份存档，拒绝证据来自冻结源码和实际日志；不称为5次磁盘导入。

## 保留的审查变化与范围

historical-pre-run-review/为未执行初稿：负例显式bytes已变更而URI仍原始；运行前修正URI与bytes一致并澄清文档措辞，reader和协议不变，没有结果后调整。CODE-REVIEW与CODE-CLOSURE分开保留。独立oracle中的NOT_EXECUTED是其前置冻结时状态，不是最终运行状态。

严格整数元数据是本reader更窄的政策；glTF规范允许整数值的小数/指数编码，不把不支持解释为格式非法。只有uint16索引、FLOAT SCALAR、1buffer/3views/1accessor，count最多4，无扩展/mesh/normalized/morph。两个有效配置仅为表示实验；无引擎导入、GPU、DCC、性能或安全解析器保证。旧160字节网格及Godot归档完全未改。
