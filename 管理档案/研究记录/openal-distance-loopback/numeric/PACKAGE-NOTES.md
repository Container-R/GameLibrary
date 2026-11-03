# 数值冻结素材与结果的归档说明

本目录先收七个冻结输入及INPUT-SHA256.json，后在结果审查完成后追加两份原result和一份共享observations.jsonl。冻结协议字节不变，实际结果见[数值审查摘要](../NUMERIC-REVIEW.md)。两轮同字节技术流合并保存不减少实际两次运行，也不增加独立条件。

清单SHA256为f6675bf6958660964b74a5d6f677379e417243ad781657cd06e9984120a41271。原协议的准备/未执行时态属于冻结当时，原字节保持；后来的实际结果已另经审查收录，不能改协议时态再沿用原SHA。

协议引用的RUNNER-DERIVATION.diff和history/pre-partial-evidence属于未附本地编辑材料，不是本包可访问附件。没有复制完整history。可以比较已附[能力runner](../capability-1.24.2/runner.py)和[数值runner](runner.py)：其派生范围为七输入绑定、数值JSONL消费及结果汇总，仍为唯一child、有限通信/回收、新运行根和严格环境白名单。该比较不等于新增故障测试。

旧未运行候选的静态缺口是：失败时部分已取得的getter值可能未进入报告。修订增加partial_actual/failure_values；非有限getter用明确标签保留，不伪造0或让JSON输出直接丢失失败现场。成功结构与消费者未因此扩展预期。这里记录静态发现，不声称实际API曾失败或执行过故障注入。协议末节保留原修订身份，本包不附旧候选输入，因此不把它写成完整历史复现包。

协议中的capability/...和capability-1.24.2/...是包根相对历史路径，可由[旧结果](../capability/run-author-1/result.json)和[新能力结果](../capability-1.24.2/run-author-1/result.json)访问。来源摘要为[版本复审](../VERSION-1.24.2-REVIEW.md)、[默认条件](../NUMERIC-DEFAULTS-REVIEW.md)、[配置边界](../CONFIG-AND-CAPABILITY.md)；这些衍生摘要不冒充原报告摘要绑定。

文件身份见包根的[公开清单](../PUBLIC-MANIFEST.json)。不要为查看文件执行runner；执行会加载音频库并渲染，需要另行作出决定。返回[观察包说明](../README.md)。
