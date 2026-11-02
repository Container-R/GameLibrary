# EnTT continuous_loader v2：执行前差异闭合

2026-11-02。**接受此版本的有限代码/纯合成检查；是否执行仍由主编另行授权。** 本轮没有编译器调用、C++ 原生执行、真实进程组信号或网络操作。初次 `CODE-REVIEW.md` 与 v1 历史保留，不把此前代码问题称为原生失败。

## 精确最终绑定

- INPUT-MANIFEST.json：`10385e60a4d6a4123d21bf272cd25c315463329ed9e8660e5f8faee044dddcd7`
- PROTOCOL-v2.md：`c62d8678facd1b7baf0f68732d2f1e40e9a96cb2b7465082989e3648002ed1c7`
- fixture.cpp：`5bc3b3ad0ffdc2d22e6c11083ce92c60dccbaf1be149a3745c165ce62fa0463f`
- runner.py：`a6a14a9c4bdcb7a4860791c9e6c1b9e6785f7904467ab3f0d6cc6c2bed3d22d6`
- checker.py：`788f72e5e978b90a14047822cd28d023e49c7495d75119cc856525a8cc78d732`
- independent-oracle.json：`90169423b365a0a3a553462caff0be05ebb6672de6f58758959b9a5c139497cf`
- test_runner_cleanup.py：`a8688a905875362c3a5243f75c2dfa3c45e777f95fbc793ae0c14af6f6e7e86c`

实际完整重读小型 runner、fixture、10方法测试、v2修改记录与协议差分；对照 history/v1 的真实文件，而不只依赖作者提供的 diff。9项清单输入逐一哈希通过；官方单头大小及 Git blob 再核相符。checker、oracle、官方单头、LICENSE 与 v1 逐字不变。以 AST 提取 BUILD/RUN 字面 argv 与 v1 比较，完全相同；未调用这些命令。

## 三处闭合

1. **组清理**：所有等待、退出码/诊断拒绝、长度/读取拒绝均位于同一清理边界。已创建组的清理不再读 poll；组信号与等待 leader 是两个各自捕获错误的步骤，首个业务错误不被清理错误覆盖。成功路径也先清理，清理失败则拒绝。有限 wait 不等于观察到所有后代都退出，协议已正确保留该边界。
2. **阶段停止**：emit 先取得实际 map/contains/valid/free_list 等值，打印并 flush 真实观察，再检查相应阶段。loaded 必须通过完整检查后才 destroy；destroyed 必须通过后才第二次 get。initial/source/seed 是原实际句柄，不用预期常量伪造输出。新增检查与四阶段表一致，optional 的解引用均在存在前提后进行；成功8行 schema、原 archive 与官方调用顺序保持。此结论为源码控制流核对，未通过 C++ 故障注入验证。
3. **正式回执发布**：只在 pending 文件写入并正常关闭后，才于同目录改名为正式 receipt.json。写入/close/改名失败不会将 pending 当正式结果；main 将失败返回且保留原首错，若此前无首错则记录回执写入失败。局部 content_check 不是整体 PASS；整体状态仍要求两副本内容一致、复制输入/产物及原输入/manifest 后检成功。该机制不声称断电持久性、恶意并发目录防护或完整文件系统事务。

## 本轮真实纯测试

实际执行以下四条命令，没有调用 runner.main：

```text
python -B research-drafts/entt-loader-native/test_runner_cleanup.py
python -B -O research-drafts/entt-loader-native/test_runner_cleanup.py
python -B research-drafts/entt-loader-native/independent-consumer-check.py
python -B -O research-drafts/entt-loader-native/independent-consumer-check.py
```

- 作者测试每模式10方法全部通过：7个 Popen/killpg mock 覆盖已退出 leader、非零退出、诊断拒绝、超时、清理失败和首错保留；3个纯临时文件测试覆盖可解析 PASS 前缀后写入失败、close失败、正常发布。已先完整读测试，确认不会发送真实信号或启动编译/原生子进程。
- 独立消费者每模式同一1合成正例与25反例通过，涵盖8行/schema/重复键/类型/位分解/字面及跨阶段关系等。脚本的旧显示计数常量8已改为实际清单项数，因此报告9项，未改变测试输入或候选文件。首次运行时已遍历并核对9项，只是旧摘要显示8，不能将摘要常量当实际核对数量。
- 额外独立纯反例：mock `os.replace` 抛错，确认正式 receipt.json 不存在而 pending 保留。未修改候选 runner；这个反例不是原生失败。

普通和优化模式消费相同合成案例，不是两套原生覆盖；上述结果不证明 EnTT 实际输出，更不预先宣称两次原生重复成功。执行条件、场景、官方源、警告即停门槛和时间预算未扩展。没有 stage 或远端写入。
