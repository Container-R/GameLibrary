# EnTT 更新通知三条件：独立执行前审查

2026-11-03。**当前冻结版暂不接受执行，须修复下列三项运行器身份/收尾问题后重新冻结。** 这是执行前静态与纯mock发现，不是EnTT原生失败。未编译、运行fixture或启动真实子进程，未发送真实信号。

## 审查绑定与完整范围

INPUT-MANIFEST.json SHA256：`4b04b18d370dab64541d7da4498a0a32c36b44343476427c1a08006f2f16296a`。

全文读取PROTOCOL、fixture、checker、expected、runner、UPSTREAM-SOURCE及SOURCE-REVIEW，核对清单全部七项文件摘要一致，并完整读取LICENSE。固定上游版本、提交链的独立联网认证复用既有SOURCE-REVIEW，不声称本次重新读取远端标签。本次另在本地固定单头实际读取publish、scoped_connection析构、mixin patch、registry patch及on_update相应段；不声称全文审计3MB头。

- PROTOCOL：`b64e4c0409a7ec97c5013525f31287ec9104a079f2b8242997140ddce652cf58`
- fixture：`b4d008eaf70b147eccfbbd9a82a89ded3ccf0f52674b5abd338ab787deb8eeaa`
- checker：`a6b86571f0e3e3f996616a0794a327fa74119a3a9c1e766ab5d570b81f4f5709`
- expected：`7c69434efd6576b5710524306946a7525cd536592a065f1bd1c91171f3ff61c2`
- runner：`4169f042b20698f1db21da0713f1bfb0850acf0a1597b4802e50dc8d44795436`
- source/LICENSE：`cc00abca23253f78ed25c87b9839ca38fea424c135f5d9f0c5aa7bb5903f1329`
- source/entt.hpp：`31be51708c7325ecb7877182fa9ee68a20fb2121ce6bcd6c1687506f0fb1c8b5`

## 三个必要修订

1. **组收尾尚未确认。** stop_group发送TERM/KILL后只wait leader；leader已退出不等于进程组已消失。纯mock显示现函数在信号调用不报错、leader wait返回0时直接返回空错误，完全没有组存在性查询。补有总期限的组消失确认；仍存在、权限或其他异常必须阻止PASS。此检查不是沙箱或所有系统写入审计。
2. **复制的消费者在即时身份检查前执行。** 构建/执行后直接import复制checker，最终hash后检太晚。纯mock在模拟native阶段追加无害Python标记写入：该标记确实在导入时执行，随后才因copied input changed拒绝。没有错误PASS，但不能把事后拒绝说成阻止未冻结代码执行。应在import前核复制checker及其固定依赖身份；保持最终后检。
3. **manifest自身不做后检。** 模拟build只把临时副本来源目录的INPUT-MANIFEST改为`{}`，七项输入字节不变，当前runner仍生成pass。应保存开始时manifest原始身份并在结束时再次比对；不能仅重新使用可变清单内容认可自身。本反例仅改临时复制目录，不碰作者原清单。

作者需保留本版与反例后最小修正。无需改变三条件、fixture或字面预期，也不扩线程、异常回调或额外EnTT场景。

## 已成立的有限机制与拒绝门

三支各自新建registry、实体与Speed=3，初始化后才订阅。observer先于scoped_connection创建，后者先析构断开，再销毁observer和registry；只监听update，不混构造/销毁。回调真实读取字段、记录seen并刷新cache。每支打印实际字段、初始化布尔值与真实回调向量，然后flush、检查；首次异常结束程序，不继续下一支。case2独立从3开始，不是case1恢复。首次有效性失败没有结果行可冒充成功。

字面表为直接写1→字段1/回调0/缓存3，patch1→1/1/[1]/1，patch3→3/1/[3]/3。checker严格递归类型比较，不允许bool冒int或float冒int；oracle由硬编码摘要约束。仅consumer_only，不把三行匹配等同整次接受。

运行器拒已有输出目录及其符号链接祖先，五个阶段目录由空env显式提供，启动前核对应路径、空目录、非symlink。固定编译argv，build60秒/native10秒，构建失败或诊断不继续原生。正常返回亦走组清理，但第1项仍待修。pending关闭再replace发布receipt，打印PASS在这之后；receipt写失败不能当成功。没有无条件重试或覆盖旧结果。

## 实际纯测试

保存 `independent/test_preexec.py`，普通模式7方法全部完成：

- 独立字面三行正例；bool、float类型、缺行、额外行、重复key、NaN、非空stderr、坏oracle拒绝。
- mocked启动失败、清理错误、日志写失败拒绝。
- 上述三项缺口的可重复纯mock见证。它们在测试意义上“通过”表示成功证实缺口，不是接受实现。
- mocked receipt.pending写失败时没有正式receipt PASS。

另以`-O`只运行消费者正反例那1方法，完成；未把整套runner在-O下运行，因为它按协议主动拒绝优化模式。两模式不是更多原生覆盖。输出分别在 `independent/pure.stdout`、`pure.stderr`、`consumer-optimized.stdout`、`consumer-optimized.stderr`。合成mock所打印的PASS只属于临时模拟路径，绝非原生观察。

所有Popen、信号以及模拟整次运行的command均替换为mock；只有普通文件复制、读取与临时文件写入。无compiler/native调用。尚不能据任何合成结果声明三条件在实际库中运行通过。
