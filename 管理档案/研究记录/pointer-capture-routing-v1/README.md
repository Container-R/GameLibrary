# 指针捕获路由：未进入案例的浏览器观察

本包是一次失败尝试的可审查记录，不是通过的浏览器验证。2026-11-03，在执行前独立审查并冻结输入后，使用已有 Playwright 调用 Chromium。输出在 `browser-launch` 阶段记录 `BROWSER_LAUNCH_FAILED`，进程退出码为1；没有取得浏览器版本，三个计划案例均未执行。保留的类别化结果不足以诊断具体失败原因，不将其推定为沙箱拒绝或浏览器行为缺陷。

- [冻结协议](PROTOCOL.md)：三例、预期序列、边界、60秒外部时限和失败条件。
- [原创 HTML](fixture.html)与[runner](runner.cjs)：未改写执行后输入。
- [原始安全 JSON 输出](output.json)：输入 SHA-256 与协议一致；runtime 版本字符串为自报，不是安装二进制身份认证。

复现需要预先已有 Node.js、Playwright 和 Chromium。命令结构为 `timeout --kill-after=5s 60s node runner.cjs <已有Chromium可执行文件>`，分别保存标准输出、标准错误和实际退出码。runner 保持 `chromiumSandbox: true`；失败时不改安全设置，不下载浏览器。此命令说明不声称在其他环境运行成功。原始标准错误是私有诊断通道，不随本包发布；本文只使用已审查的错误类别。首次失败后未进行第二次尝试。

[返回读者说明](../../支持资料/拖动物品时，事件目标为什么不是落点.md)
