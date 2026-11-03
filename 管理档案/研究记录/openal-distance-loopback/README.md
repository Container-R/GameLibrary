# OpenAL 最大距离：五个静态配置的离线观察

本包保留两次无渲染能力门，以及随后两轮五静态配置的loopback数值观察。技术信号由内存渲染取得，不是声卡录音或听觉测试。

## 实际发生了什么

第一轮按1.24.3来源基线要求检查，库自报 `1.1 ALSOFT 1.24.2`、renderer为 `OpenAL Soft`，因此正常清理并停为 SOURCE_VERSION_REVIEW_REQUIRED。它没有继续读取实际格式/HRTF/limiter属性。第二轮先完成固定1.24.2来源比较，另行冻结输入，再执行一次能力检查，结果SUPPORTED：实际48000Hz、mono、float、HRTF关闭、limiter关闭，清理成功。

两轮各有一个loopback设备/context，source、buffer、render调用均为0。两轮是同环境下不同版本接受条件的能力门，不是独立机器复现，也不是两个不同音频实现。技术版本自报不等于官方二进制构建认证；两轮都明确 configuration_fully_excluded=false。

- [旧版本停止结果](capability/run-author-1/result.json)
- [新来源基线下的能力结果](capability-1.24.2/run-author-1/result.json)
- [有限审查与输入身份](CAPABILITY-REVIEW.md)
- [原始扩展与设计范围](GATE.md)、[配置限制](CONFIG-AND-CAPABILITY.md)、[1.24.2版本复审摘要](VERSION-1.24.2-REVIEW.md)

## 后续数值观察

一次主操作者运行，加一次已知首轮结果的同环境独立操作者重复；不是盲测或跨机器。每轮五case、十五render、72000帧。两轮原技术流逐字节相等，合并存一份[observations.jsonl](numeric/observations.jsonl)，[主轮result](numeric/run-author-1/result.json)与[独立轮result](numeric/run-review-1/result.json)各自保留。

预注册固定窗条件下，比值分别约1、0.1、0.1、0.2、0，全部通过有限门槛。详见[数值审查摘要](NUMERIC-REVIEW.md)、[冻结协议](numeric/PROTOCOL.md)及[独立离线工具/历史说明](numeric-independent/PACKAGE-NOTES.md)。来源默认条件见[补核摘要](NUMERIC-DEFAULTS-REVIEW.md)。旧版本停止、执行前失败证据修正及独立checker结构修复均保留，不合并成一路无问题的成功记录。

## 冻结输入与历史时态

两个能力目录各含原字节的PROTOCOL、driver、runner、isolation helper、受控配置和输入清单。协议中的“尚未执行/待审”是执行前冻结时态，保留原样，不是本包否认后来发生的两次运行。结果与本README说明后续事实。原协议提到的配置合并记录见[公开摘要](capability/CONFIG-MERGE-NOTES.md)。根部来源与审查说明都是明确衍生文本，不冒充本地原报告的相同字节或SHA。

清单分别为：
- capability/INPUT-SHA256.json：1e782e8eaf49dbd1867261357545ca68daed4fe7c2abd31e11bc32c4d8fab996。
- capability-1.24.2/INPUT-SHA256.json：76ddad985dfca1e1ec0a8c454b88e33913c54c08d412e106f6808ecce2487148。

五输入的SHA由相应清单绑定；原清单本身由上述摘要及审查绑定。结果内绑定的是这些技术输入，不是安装库指纹。

## 阅读与再次执行不是一回事

可直接阅读协议、代码和JSON，不必运行任何东西。若另行决定复现，需要Linux、Python 3和可被正常动态加载器选中的 libopenal.so.1；本包不附安装库、不安装替代品、不包含上游源码全集，也不保证另一环境支持该格式。

先核输入清单和文件字节，再在所选能力目录中使用一个全新且未存在的运行名称，例如 `python3 -I -B runner.py reader-check-1`。这个命令会加载库并创建loopback/context，**不是只读归档检查命令**；不应为了阅读本记录自动执行。不要用author-1覆盖包内保留结果。预期版本不符或能力不足就停止，不改版本比较或后台约束追求SUPPORTED。

原runner会创建本地私下日志与环境目录，它们不在本包中。result中的returncode为runner记下的child返回值，不是外部工具对runner退出的独立原始证明。本包没有复制原外部工具记录；不以SUPPORTED标签替代全部运行证据。

文件身份见[公开文件清单](PUBLIC-MANIFEST.json)。返回[超过最大距离，为什么声音还没有消失](../../支持资料/超过最大距离，为什么声音还没有消失.md)。
