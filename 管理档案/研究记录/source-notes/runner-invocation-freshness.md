# 历史成功摘要不等于本次调用成功

2026-10-31，[六个 Godot 运行器的独立拒绝实验](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/audits/runner-rejection/README.md)实际确认：Python -O 调用均退出 1，未进入引擎调用，却保留预置的历史 PASS 摘要。只复制 Python runner，未运行 Godot，也没有重写任何既有运行源或引擎日志。

这些运行器在优化模式拒绝之后，进入正常路径才删除旧 `results/summary.json`。因此旧文件存在、内容是 PASS、甚至文件时间较新，都不能单独作为某一次调用成功的依据。拒绝本身有效；问题是消费者误认历史产物，而不是程序返回了虚假成功。

消费者必须保存本次调用的命令、源身份、起止时间、退出码与输出引用；非零退出不能被旧摘要覆盖。当前历史摘要没有唯一 invocation ID。需要新执行证据时，在新的隔离副本中运行并保存外部调用回执，将新摘要与该次调用绑定；不要直接覆盖已归档证据。文件一致性校验只说明选定历史文件相互一致，不能证明最近一次尝试成功。

本审计没有验证所有失败分支、并发调用、权限错误、崩溃持久性或上游程序身份。`godot-fixed-step/run.py` 的旧注释关于失败不留旧摘要，只适用于已到达清理点之后；保持原始源哈希，不静默修改历史实验代码。这次历史审计没有实现唯一调用 ID；下述后续增量另行实现并验证，不改写该审计结果。

本说明不宣称六个 Godot runner 已修改；原始源与既有执行记录保持不变。

ICU 夹具的新版 runner 已单独修复优化拒绝前的摘要清理，并测试超时部分输出保留；[有限证据](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/experiments/icu-message-boundary/runner-negative/README.md)不代表六个 Godot runner 也已修改。

## 后续增量：独立调用回执，而非重写旧 runner

[新的 Linux 包装器](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/scripts/evidence/fresh/README.md)只复制注册源文件到外部 UUID 目录，以调用者保存的 expected ID、终态、退出码、源与输出哈希共同判定。六个旧 runner 和 306 个既有文件完全保留。**正常运行适配器仅启用 focus-boundary**；其余五个仅验证早期 `-O` 拒绝路径。

[公开审计](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/audits/fresh-invocation-harness/README.md)区分两次实际正常 focus 调用、十二次分批 `-O` 拒绝、额外合成/单元测试，以及归档迁移后的只读消费。消费者验证一致性，不是执行真实性签名；不保证恶意文件系统、逃离进程组的后代、所有操作系统或崩溃持久性。新增回执不能替代旧实验缺失的二进制身份，也不能证明六种正常运行全已验证。
