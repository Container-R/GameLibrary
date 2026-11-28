# ink 换行前瞻和宿主动作：原生 C# 复现

对应正文：[ink 对话还没显示下一句，为什么游戏动作已经执行](../../../GameLibrary/叙事设计/运行时叙事/对白推进与游戏交接/ink%20对话还没显示下一句，为什么游戏动作已经执行.md)。

## 环境与执行

已用官方 ink **v1.2.1** 编译器和同一发布包的 `ink-engine-runtime.dll` 在 Linux x64 运行。使用微软 .NET SDK **8.0.428** 的 Roslyn 编译 C# 宿主，不依赖 Unity，也没有使用 inkjs。需要 Bash、官方 SDK 和解压后的 [inklecate_linux.zip](https://github.com/inkle/ink/releases/tag/v1.2.1)。运行：

```bash
bash run.sh /absolute/path/to/dotnet-sdk-8.0.428 /absolute/path/to/inklecate
```

ink 官方发布资产 SHA-256：`1997ff5bca618c90003ecd5fecb286e7468abb955005a2a185042949642f8fb5`。SDK 对照 [微软发布清单](https://builds.dotnet.microsoft.com/dotnet/release-metadata/8.0/releases.json)中相同版本的 Linux x64 文件。脚本写入随机临时目录，直接调用 SDK 中编译器，不从 NuGet 下载依赖。[C# 宿主](Program.cs)、[运行脚本](run.sh)、[原始输出](observed.txt)。

## 对照与边界

1. [permission.ink](permission.ink)：真实 C# 闭包计数模拟宿主写入。只改 `lookaheadSafe`，第一行后宿主计数 1 或 0，故事变量都为 0；第二行后宿主累计 2 或 1，故事变量都为 1。
2. [glue.ink](glue.ink)：查询固定返回北门，无游戏状态变更，调用计数只用于观测。打开前瞻得到一行，关闭得到两行。只将空格移除用于测试内容对照；原始输出保留空格与两段边界。
3. [tagged.ink](tagged.ink)：第一行无标签，第二行派发一次；恢复第一行后的 ink 状态时，第二行再返回相同标签，保留的宿主内存键拒绝重复。只回放 ink 状态不是恢复整个游戏世界，不能据此保证跨进程或整档恢复；真实整档应一起恢复效果和相应去重记录。
4. 产品演出若可取消，额外测试迟到的旧配音完成回调不会提交已取消请求。测试集没有 Unity UI、语音或持久化；这一条是宿主验收建议，不是本次动作计数的实验结果。
