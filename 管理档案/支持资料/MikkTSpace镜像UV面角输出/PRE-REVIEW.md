# MikkTSpace 有限原生单元：执行前独立审查

## 初审结论：须修正消费端，原生执行仍暂停

完整读取 GATE、PROTOCOL、SOURCE-MANIFEST、fixture、字面 oracle 与 consumer；读取本地固定上游头文件及 C 的入口、输出和 UV 导数段。没有编译、启动夹具或调用生成器。仅在完成静态阅读后运行了下面明确区分的纯合成 Python consumer 反例。

### 必须修正

1. `validate.py` CLI 信任相邻 `expected.json`，没有核其冻结身份。`check_rows` 对 expected 使用 zip 而不检长度，因而被缩短的 oracle 会漏验。外部执行流程核清单可以保护那一次受控调用，却不能使公开 consumer 自身保持所宣称的固定字面判据。最小修法为在 parse 前验证已知 oracle SHA，并让受支持的消费入口不能传入任意未经绑定的 expected；或提供等价的有限固定输入守门，不需通用 schema 框架。
2. 返回摘要 `generator_calls:1` 是源码/协议预期，不是 JSON 观察独立证明的调用计数。改为 `expected_fixture_calls` 或同样明确的标签，不能让 consumer 看似测量了调用次数。

修正后应更新清单并重新独立检查，而不是基于此初审直接构建。

## 几何、完整记录与映射

独立手算：F0 的两条边为 +X、+Y，叉积 +Z；F1 从旧0到旧3为 −Y、到旧1为 +X，叉积同为 +Z。F0 的 UV 边为 (1,0)、(0,1)，有向面积为正；F1 为 (0,1)、(1,0)，有向面积为负。对应参数化 P=(u,v,0)、P=(u,−v,0)，两面 T=+X，B 分别为 +Y、−Y；N×T=+Y，所以 sign 为 +1、−1。

六行 oracle 的 face/corner/old、P、N、UV、T 和 sign 均与上述输入一致。共享旧0、旧1在两面拥有相同 P/N/UV，却要求不同 sign，不能靠四槽覆盖同时保留两面的角输出。

前向覆盖最后保留 F1 的旧0、旧1，六角符号为 [-1,-1,+1,-1,-1,-1]，丢失 F0角0/1。反向覆盖最后保留 F0 的旧0、旧1，符号为 [+1,+1,+1,+1,-1,+1]，丢失 F1角0/2。其他属性在这个特定输入仍一致；不是任意网格都只有 sign 变化。

正确对照保留六条完整记录，用 F0=(0,1,2)、F1=(3,4,5) 查询，代码实际经 indices 取 correct 记录。这个一角一记录的方案不声称最小去重。输出行的 face/corner/old 是查回时的角身份，P/N/UV/T/sign 才来自所查询记录；本例共享槽的非切线属性相同，设计与冻结对照相符。

## 上游合同与 C 输入安全范围

本地上游头文件完整阅读到许可及回调说明：basic 回调足够，结果按 face/vertex 返回且未索引；副切线由 sign×cross(N,T) 重建；已有索引平均或覆盖会破坏结果。C 入口224–285、输出401–419、导数965–1007与这些合同相符。默认入口传180度，只有一个 basic 输出回调实际安装。

fixture 在所有数组取值前验证 face/corner，输入索引均落在四记录中。Capture 零初始化、重复/过量回调在写 order 前失败，切线及 sign 检查有限，生成返回及六个 seen 全检查后才消费。两次覆盖重放都遍历全部六角，四槽均在读取前有赋值。ctx/interface/必要输入回调在生成之前完整设置；没有故意空指针或越界输入。原生分配失败、平台行为和所有上游算法路径没有因此被认证。

## 实际纯合成 consumer 检查（不是原生结果）

静态发现后做两次有限 Python 检查：

- 第一次将 oracle raw 缩空且给六个空行，consumer 在后续读取第14项时抛 IndexError，没有 PASS；这不是所需的完整验证，亦不计为原生失败。
- 随后将 oracle raw 与两组 mismatch 均设为空，给四组各六条15项全零记录，同时保留表层 output_count/order/indices。consumer 实际返回 PASS，尽管没有正确的六角身份、法线或符号。它证明可替换 oracle 会削弱判断，不能归咎于 MikkTSpace。

未修改冻结 oracle、夹具或上游文件。没有运行编译器，没有生成 observation，没有把合成反例当实际生成器输出。检查使用普通 Python；本初审未声称已做 consumer 的 -O 回归。

## 初版精确绑定

| 文件 | SHA256 |
|---|---|
| GATE.md | 60feb7d53f5cfaac0aad4522578245b46344eb0e315832e8adb7c8ed393c4dd9 |
| PROTOCOL.md | fdbb5e6e35d0600734ccac5dd3c2bef9e1f565f2fa4cc70cd0883b96790086b7 |
| SOURCE-MANIFEST.json | ad1c0a7f9afa659bdbd65bb94be762cbe11f476dc58567ba62278deadbbecf87 |
| fixture.c | 315529ee9079983bebadefa8fe3ee02233fc48c614fbe29b0d3651f15d8e43d5 |
| expected.json | bb0b71cc525a8f4438a1ddc464e2a42d16aa83055bfc232be129f6139e3a3532 |
| validate.py | aa264c8bce15a939c83d6edf87cc30c74454167611cbc5037f16de398bbf5480 |
| upstream/mikktspace.c | de87e74107df766ce68108801262bd8d53899414236b59810509a8fc2a51e288 |
| upstream/mikktspace.h | 17fc433894f24c73753d548086cc4d8c5c0379f4a6edfb98b5da243e4f0bc3d0 |

独立以本地完整文件字节计算 Git blob，分别为 C `0342ae0146f1e14854ad8d3309bbbc3d27adc9bc`、H `52c44a713c60ebff71133a41e0711bbf7199fc5e`，与清单声明一致。此轮没有重新联网证明 commit→blob 关系；上游固定链接与来源读取由已有门槛记录承担。

公开候选只含源身份、数学输入、程序和拟议安全输出，不需要主机路径、安装二进制指纹或进程身份。之后构建诊断和退出信息仍需独立审核，不能因本协议安全便自动认领未来全部输出可公开。此次审查不修改 stage 或远端。

## 有限修订复核：预执行接受

实际重新读取修订 consumer 和协议差异：`validate(observation)` 不再接收 expected 参数；入口先读取相邻 oracle 原始字节、核对冻结 SHA256，然后才解析同一份已核字节。摘要变更、格式变化或缩短 oracle 都不能静默更改判断。输出改名 `expected_fixture_calls`，协议明确其为要求而不是独立计数。初版发现及其失败证据以上保留。

最终绑定：

- PROTOCOL.md：`8ca3ef52313f411cc6d18b658b69e5bf8a1d9d652fddae6cdf6d5447b5772ef5`
- validate.py：`c9210e5017c2ef50b40c9008634d99068d1cb282d7e237425ba9f4818b61dd13`
- SOURCE-MANIFEST.json：`49ecb85282c057d78a4851074aee9f13c808f655bca0aed603cd925288bcd9a8`
- expected.json、fixture.c、两份上游文件保持初版绑定；实际逐项计算清单列出的所有文件摘要均匹配。

独立编写 `synthetic-consumer-review.py`，只在临时副本调用 Python consumer。14个相同合成情形分别在普通及 `-O` 运行，均符合预期：一份合成正确输出（故意逆序 callback_order）接受；缺角、身份错误、sign错误、P属性错误、索引错误、重复回调、bool 数值、超容差切线、错误覆盖重放均拒绝；缩短 oracle、只加空白的 oracle、重复 JSON 键、NaN token 均非零退出且不输出 PASS。安全结果分别存 `synthetic-normal.json`、`synthetic-optimized.json`，不保存子进程 stderr 中的临时路径。14是同一情形集合，不计为28个独立输入。

合成正确输出来自先前独立确认的字面表，只能检验消费器接受与拒绝逻辑，不能证明生成器会输出这些数据。容差仍是预定绝对1e-6，未根据原生结果调整；本轮没有原生结果。

**这两个必要修正已闭合。接受冻结几何、六行完整 oracle、接收对照与当前程序进入主编分阶段授权流程。** 本人仍没有编译或运行 fixture；是否允许构建、审阅诊断后是否允许一次原生调用，须分别由主编执行既定门槛。没有承诺编译必过、原生值必符或未来载荷自动安全。
