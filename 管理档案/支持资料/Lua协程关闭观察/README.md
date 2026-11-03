# Lua 5.4.8 协程关闭：三个有限观察

[返回读者说明](../协程已经dead，为什么关闭时还能调用收尾方法.md) · [返回 Lua 正文](../../../GameLibrary/引擎与工具/运行时系统/异步资源/Lua%205.4%20协程暂停后，资源为什么还没有关闭.md)

三个原创分支比较暂停后正常恢复、暂停后显式关闭，以及普通恢复出错后再关闭。表对象只记录事件，不代表游戏资源。完整返回数量、状态、关闭次数及错误标记身份均由断言检查；七行字面预期在 runner 中预先固定。

## 复现输入

保留本目录下 fixture 的 case.lua、PROTOCOL.md、runner.py 和 manifest.json 原字节。另从[Lua 官方](https://www.lua.org/ftp/lua-5.4.8.tar.gz)取得源码归档，将文件名保持为 lua-5.4.8.tar.gz，放入同一个 fixture 目录。归档不随此公开包分发。

归档为2025-05-21发布的5.4.8，374332字节，SHA256 为 `4f18ddae154e793e46eeab727c59ef1c0c0c2b744e7b94219710d76f530629ae`。runner 在复制前后核摘要，只提取明确白名单的普通源码/头文件；不运行发行包 Makefile，不安装到系统。来源和许可见 [SOURCE.json](SOURCE.json)。

在自己的工作副本中，具备 Python3、C 编译器和标准数学库后，从 fixture 目录执行：

```sh
python3 runner.py --run-name reproduction-1
```

仅适用于此处有限 POSIX 构建方式。每次使用全新名字，既有目录会被拒绝；编译120秒、运行5秒。没有软件时停止，不自动安装。解释器以 `-E` 启动，环境不继承 Lua 初始化配置。环境目录和进程组处理不是安全沙箱。

## 冻结协议与实际结果分开

- 主轮：[七行输出](observations/main-1/output.txt)、[原始回执](observations/main-1/result.json)。
- 独立轮：[七行输出](observations/independent-1/output.txt)、[原始回执](observations/independent-1/result.json)。
- 固定输入：[协议](fixture/PROTOCOL.md)、[Lua 夹具](fixture/case.lua)、[运行器](fixture/runner.py)、[输入摘要](fixture/manifest.json)。

协议和 manifest 保留“准备、尚未执行”状态，表示它们在执行前冻结，不因后来运行而修改输入。实际结果另附。已核两轮在同一宿主、由不同操作者分别在新目录独立编译运行；每轮同样三个分支、七个记录阶段。复核者已知主轮结果，不是盲测、跨平台或不同算法复现。两轮输出及回执逐字相同，输出 SHA256 为 `60044656693589b171bde180a0eff17f3de0f77260ff59f2154ef41c4d98c436`；构建和运行退出均为零，运行 stderr 为空。

构建 stderr 非空，两轮均有链接阶段针对 `os_tmpname` 所引用 `tmpnam` 的安全警告。独立诊断审读确认没有其它诊断，且本夹具不调用该接口，因此不阻断这三个有限观察；这不是对临时文件接口安全性或整个解释器的认证。原始诊断仅留本地，公开说明只保留类别和影响范围。原回执中的 `compile_diagnostics_require_review=true` 与 `publication_review_required=true` 保持原值，由后续[独立诊断审读](DIAGNOSTIC-REVIEW.md)闭合，不回写历史输入或回执。不能把 runner 的 passed 字段单独当作发表许可。

这不是错误注入全集、GC/线程/宿主资源测试，也没有测试超时清理路径。原 Lua 正文的宿主资源示意仍未执行。公开包不包含源码归档、构建二进制、环境目录、原始日志或机器指纹。
