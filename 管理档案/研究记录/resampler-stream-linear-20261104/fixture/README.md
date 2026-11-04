# 一个有限的连续重采样实验夹具

先读 [PROTOCOL.md](PROTOCOL.md)。这里是四条固定调用路径的规格、原创驱动和验证器，不包含音频质量结论。先验数组不是运行记录；结果须以单独的完整验证报告为准。

## 文件

- `src/probe.c`：原生 C 驱动，只使用公开 API。
- `fixtures/oracle.json`：独立固定输入、调用表和预期。
- `fixtures/source-identity.json`：固定上游身份与运行库来源限制。
- `run_probe.py`：一次构建/执行、有限捕获和独立复验，无下载、安装或重试逻辑。
- `FREEZE.json`：实现审查完成后才生成的输入身份清单；缺少它不能运行。
- `.local/`：仅本地使用，**不随公开包发布**。包含上游构建输入、隔离执行目录、二进制和原始诊断。

## 准备本地公开头文件

从 libsndfile/libsamplerate 的固定提交 `c96f5e3de9c4488f4e6c97f59f5245f22fda22f7` 取回原始字节，保留版权及完整许可：

- [include/samplerate.h](https://raw.githubusercontent.com/libsndfile/libsamplerate/c96f5e3de9c4488f4e6c97f59f5245f22fda22f7/include/samplerate.h) → `.local/upstream/samplerate.h`，Git blob `a3d5ae1aa0859c41a33371dc1c3b3f65f63cb417`。
- [COPYING](https://raw.githubusercontent.com/libsndfile/libsamplerate/c96f5e3de9c4488f4e6c97f59f5245f22fda22f7/COPYING) → `.local/upstream/COPYING`，Git blob `9f82626e6371ceeb76f8d2c9968748ec1584e10f`。

Git blob 身份是对 `blob <字节数>\0` 加文件原字节计算 SHA-1；运行器自动核对，不能用平台换行后的文本替代。它还核对经审查冻结的 SHA-256。取回在运行前完成，运行时不联网。

运行器需要支持 `resource`、POSIX 进程组、`O_NOFOLLOW` 和 `Path.is_relative_to` 的 Python 3.9+，现有 C11 编译器及版本化 libsamplerate 运行库。缺能力或版本不符就停止，不自动安装或改用别的加载路径。

## 冻结与执行

先审查协议、两份实现、两个 JSON 夹具与上述上游身份。通过后，再创建 `FREEZE.json`，其顶层必须恰为 `schema_version:1`、`protocol_id:"resampler-stream-linear-v1"`、`files`。files 必须恰好含以下相对文件到小写 SHA-256 的映射：

`PROTOCOL.md`、`README.md`、`src/probe.c`、`run_probe.py`、`fixtures/oracle.json`、`fixtures/source-identity.json`、`.local/upstream/samplerate.h`、`.local/upstream/COPYING`。

清单本身不代替执行批准。批准后，从包目录运行 `python3 run_probe.py --output results/observed.json`。目标必须是未存在的新文件。报告状态为 `passed`、原生正常退出、无超限且独立复验通过，才算本次有限实验通过。缺失、`incomplete`、`failed`、无最终摘要或非零退出都不能当成功。

输出中的十六进制浮点字符串保留实际数值；完整 40 项 arena 使失败时仍能检查输入、scratch 与保护区。异常版本内容不向公开输出转发，因此 `reported_version:null` 不能用来判断版本函数是否返回 NULL。运行器的独立复验是另一份代码对同一次捕获的检查，不是独立真人实验或第二次原生运行。

执行目录、输入副本、二进制和原始诊断有意保留在 `.local/runs/` 供私下核查，不自动清理；运行器的清理要求针对进程组的终止/回收。不要直接发布整个目录、原始编译/加载诊断或本机二进制。发表前只选明确允许的原创包文件、冻结清单和已审技术报告；任何输入修订必须重新审查，不能套用旧结果。
