# Detour 输出容量：独立原生重复审查

2026-11-01。**本次获单独授权的独立重复通过。** 这是同一工作环境、同一固定输入与构建参数的重复，不是跨机器、跨平台或新场景覆盖。未追加节点耗尽、权重走廊、导航烘焙或真实角色移动。

## 实际执行与身份

先核源候选 CODE-MANIFEST.json 为 `5cb938c46fecce826907b4f1555b283f3a2b742be2cf9ab1a73b65a758210877`，8 项候选 SHA 与 16 项上游 SHA/Git blob 全相符。创建此前不存在的 `independent-repeat/`，只复制这 8 文件、CODE-MANIFEST.json 与明确的 16 上游文件，逐字节对照原件；没有复制任何 execution、已编译程序或旧 PASS。

随后实际调用一次运行器。下列命令已归一化为包内入口，不是原命令路径的逐字节副本：

```
python -B run.py
```

未修改 runner、fixture、oracle、源码、编译 argv 或诊断字节。runner 在新目录下使用固定 `execution/attempt-002/`，60 秒构建/10 秒 fixture 限额不变。实际返回 0、receipt pass/complete：build returncode=0、stdout 空，stderr 与已审 warning 整份字节相同；native returncode=0、stderr 空。

最终 receipt 的 source_before/source_after/copied_after 均为24项且相同。审者另从独立源目录和实际工作副本逐一重新读48个文件核SHA，均匹配；四个实际输出流SHA也均与receipt吻合。该身份链不含公开主机路径、进程或工具二进制指纹。

固定源码仍为 `6dc1667f580357e8a2154c28b7867bea7e8ad3a7`。fixture SHA `dce68bd7eeb9508f72e1c207c0de67e36cca578934ff49f5d70747326728c085`；oracle SHA `c30414c81af4d665d787312aba22f0f259556bde645013dac4bba43efc609140`。

## 实际观察及独立读回

完整读 `independent-repeat/execution/attempt-002/native.stdout`：

- builder/nav.init/query.init 各1；mesh_checked 在 query_init 之前，最终 released；query_calls=2。
- data_size=496，header依次3/8/3/6/0/0/12；8个实际顶点和3个poly均与预冻结输入一致；flags=1、area=0，默认filter为65535/0/1，节点池容量16。
- 本次实际 refs 为 A=4、B=5、C=6，非零互异有效；neis 和四条内部有向 links 正是 A↔B↔C，side=255，没有额外分支。

| 实际查询 | status | pathCount | 全部三槽 | 实际索引映射 |
|---|---|---:|---|---|
| maxPath=2 | 0x40000010 | 2 | 4、5、0 | 0、1、null |
| maxPath=3 | 0x40000000 | 3 | 4、5、6 | 0、1、2 |

第一行成功位与输出不足位共存，不含 PARTIAL_RESULT/OUT_OF_NODES，第三槽仍0；第二行完整含目标。它只确认该固定合法链的这两次输出，不能把哨兵观察提升为通用内存安全证明。

独立原生输出 SHA256：`0edf850d701be23d45c1fdca270b578081b7cc62371a2165d267dca198404674`。与主编 `execution/attempt-002/native.stdout` 实际逐字节相同；两份成功 receipt 的源身份集合相同。没有用主编原生结果修改本轮输入或预期。

另外分别以普通 Python 与 -O 调用独立工作副本 validate.py 消费这一份输出，两者均返回 consumer_only/pass，绑定相同观察SHA。它们没有再次启动 fixture；也不能脱离整体 receipt 当作执行验收。

## 真实数量与保留失败

- **本审者重复：1 次构建、1 次 fixture 启动、2 次 findPath。**
- 首次 attempt-001：1 次构建、0 次 fixture、0 次 findPath，仍是未审诊断导致的整体 fail。
- 主编已授权 attempt-002：1 次构建、1 次 fixture、2 次 findPath。
- 三份现有尝试合计：**3 次构建、2 次 fixture、4 次 findPath；只有同一输入的两种容量重复两遍**。不是四种不同查询情形，普通/-O消费不增加原生数量。

已审 class-memaccess 警告并未消失：两次成功构建都按新精确门槛保留它。该源实现的实际清零路径可达，有限观察通过不证明标准层面的任意 memset/对象生命周期/ABI安全，也不为生产环境推荐压制诊断。首FAIL和执行前源码/协议修订事实均保留。

本轮结束，不自动再构建或重跑。公开材料可保留固定源/输入、有限观察及本报告；无需发布程序二进制、安装信息或无关执行元数据。


公开归档说明：已将早期研究副本的目录前缀归一化；这些历史定位不表示本归档附带原执行目录。可复现输入与实际观察以README映射为准，技术结果未改，本文件不是原审查原字节副本。
