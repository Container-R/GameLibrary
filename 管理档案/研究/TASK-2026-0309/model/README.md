# 候选惯性到同步行为调用：原创验证夹具

TASK-2026-0309 的局部模型补强；不是正式文章，也没有远端修改。

## 文件与重放

- [protocol.md](protocol.md)：首次运行前写定的合同、输入和验收预期。
- [behavior_fixture.py](behavior_fixture.py)：只依赖 Python 标准库的原创源码。
- [results.json](results.json)：真实运行输出，包含全部 64 个 tick、资格与分数快照、调用顺序、占用、计数及附加断言结果。
- [README.md](README.md)：运行记录与可读逐步轨迹。

在本目录执行：`python3 behavior_fixture.py > results.json`。首次执行退出码 0，全部协议断言通过，没有经历失败后改写预期。
使用 Python 3 标准库即可复跑；未据此宣称已在其他平台测试。

## 结果与解释

小分差反转在 100ms 保留 A，没有再次 start；大分差反转在 200ms 按 stop A → start B → update B 顺序执行。241ms 失效不对齐检查时钟，250ms 才检查并同步释放。300ms 候选为空。351ms A 恢复，但直到 400ms 普通评分才以合法零分重新开始，这是同一候选的新一次执行。
人工 update 每次只推进一个工作计数；恢复后的执行设置门槛为 3。420ms 和 620ms 的 update 达到门槛，分别在 430ms 与 630ms 下次检查发现完成并 stop。它既不是游戏收益，也不是寻路进度。
500ms B 资格通过但注入 start 失败；本轮不重试，510–590ms 也不补位，600ms 的新评分才开始成功。另有独立失败切换用例覆盖旧 A 已运行时 stop A → start B 失败，且不在同一轮重新启动 A。
整个主轨迹 start 尝试 5 次、成功 4 次、stop 4 次、update 31 次；最终两个目标均释放，current=None。每次 tick 都断言占用与 current 一致。A 已由自身占用时 start 资格为假（occupied），continue 资格为真（owned_by_self）；100ms 普通评分确实使用 continue。
等分检查保留当前 A；无当前、字典倒序输入同分候选时仍按稳定键选 A。复用分数反例中，类型奖励六次比较都换目标，具体候选奖励零次；大幅反转即使使用候选奖励仍六次都换。后两项是纯评分补充，不额外声称测得 start 次数。

## 完整逐步轨迹

下表不省略 tick。评分列只在普通评分时刻出现，资格的详细原因与基础分/奖励见 JSON。`uN` 为本次执行的人工工作计数，`rN` 为执行编号。

| ms | 检查结果 | 评分/决策 | 调用顺序 | tick 后 current |
| --- | --- | --- | --- | --- |
| 0 | 无当前 | start_from_none | start mine:A r1 → update mine:A r1 u1 | mine:A |
| 10 | 可继续 | 未评分 | update mine:A r1 u2 | mine:A |
| 20 | 可继续 | 未评分 | update mine:A r1 u3 | mine:A |
| 30 | 可继续 | 未评分 | update mine:A r1 u4 | mine:A |
| 40 | 可继续 | 未评分 | update mine:A r1 u5 | mine:A |
| 50 | 可继续 | 未评分 | update mine:A r1 u6 | mine:A |
| 60 | 可继续 | 未评分 | update mine:A r1 u7 | mine:A |
| 70 | 可继续 | 未评分 | update mine:A r1 u8 | mine:A |
| 80 | 可继续 | 未评分 | update mine:A r1 u9 | mine:A |
| 90 | 可继续 | 未评分 | update mine:A r1 u10 | mine:A |
| 100 | 可继续 | retain | update mine:A r1 u11 | mine:A |
| 110 | 可继续 | 未评分 | update mine:A r1 u12 | mine:A |
| 120 | 可继续 | 未评分 | update mine:A r1 u13 | mine:A |
| 130 | 可继续 | 未评分 | update mine:A r1 u14 | mine:A |
| 140 | 可继续 | 未评分 | update mine:A r1 u15 | mine:A |
| 150 | 可继续 | 未评分 | update mine:A r1 u16 | mine:A |
| 160 | 可继续 | 未评分 | update mine:A r1 u17 | mine:A |
| 170 | 可继续 | 未评分 | update mine:A r1 u18 | mine:A |
| 180 | 可继续 | 未评分 | update mine:A r1 u19 | mine:A |
| 190 | 可继续 | 未评分 | update mine:A r1 u20 | mine:A |
| 200 | 可继续 | switch | stop mine:A r1 (better_candidate) → start mine:B r2 → update mine:B r2 u1 | mine:B |
| 210 | 可继续 | 未评分 | update mine:B r2 u2 | mine:B |
| 220 | 可继续 | 未评分 | update mine:B r2 u3 | mine:B |
| 230 | 可继续 | 未评分 | update mine:B r2 u4 | mine:B |
| 240 | 可继续 | 未评分 | update mine:B r2 u5 | mine:B |
| 250 | 失效 | 未评分 | stop mine:B r2 (invalid) | None |
| 260 | 无当前 | 未评分 | 无 | None |
| 270 | 无当前 | 未评分 | 无 | None |
| 280 | 无当前 | 未评分 | 无 | None |
| 290 | 无当前 | 未评分 | 无 | None |
| 300 | 无当前 | empty | 无 | None |
| 310 | 无当前 | 未评分 | 无 | None |
| 320 | 无当前 | 未评分 | 无 | None |
| 330 | 无当前 | 未评分 | 无 | None |
| 340 | 无当前 | 未评分 | 无 | None |
| 350 | 无当前 | 未评分 | 无 | None |
| 360 | 无当前 | 未评分 | 无 | None |
| 370 | 无当前 | 未评分 | 无 | None |
| 380 | 无当前 | 未评分 | 无 | None |
| 390 | 无当前 | 未评分 | 无 | None |
| 400 | 无当前 | start_from_none | start mine:A r3 → update mine:A r3 u1 | mine:A |
| 410 | 可继续 | 未评分 | update mine:A r3 u2 | mine:A |
| 420 | 可继续 | 未评分 | update mine:A r3 u3 | mine:A |
| 430 | 已完成 | 未评分 | stop mine:A r3 (completed) | None |
| 440 | 无当前 | 未评分 | 无 | None |
| 450 | 无当前 | 未评分 | 无 | None |
| 460 | 无当前 | 未评分 | 无 | None |
| 470 | 无当前 | 未评分 | 无 | None |
| 480 | 无当前 | 未评分 | 无 | None |
| 490 | 无当前 | 未评分 | 无 | None |
| 500 | 无当前 | start_failed_remain_none | start_failed mine:B (injected_failure) | None |
| 510 | 无当前 | 未评分 | 无 | None |
| 520 | 无当前 | 未评分 | 无 | None |
| 530 | 无当前 | 未评分 | 无 | None |
| 540 | 无当前 | 未评分 | 无 | None |
| 550 | 无当前 | 未评分 | 无 | None |
| 560 | 无当前 | 未评分 | 无 | None |
| 570 | 无当前 | 未评分 | 无 | None |
| 580 | 无当前 | 未评分 | 无 | None |
| 590 | 无当前 | 未评分 | 无 | None |
| 600 | 无当前 | start_from_none | start mine:B r4 → update mine:B r4 u1 | mine:B |
| 610 | 可继续 | 未评分 | update mine:B r4 u2 | mine:B |
| 620 | 可继续 | 未评分 | update mine:B r4 u3 | mine:B |
| 630 | 已完成 | 未评分 | stop mine:B r4 (completed) | None |

世界事件不属于 tick：241ms A/B 不可用；351ms A 恢复；451ms A 不可用、B 恢复。模型规定这些事实立即可见，但只在 tick 采样。

## 边界与没有证明的事

这是单角色、单所有者、同步 stop、失败 start 无副作用、无目标 ID 复用的确定性模型。start/stop 是实际被调用的本地 Python 方法，实际占用/释放的是模型字典，不是游戏对象资源。恢复沿用同一对象身份，执行编号只用于记录新的一次 start。
未实现真实感知、寻路、动画、物理、异步完成、部分效果回滚、异常恢复、多角色争用、性能测量或最低持续时间保证。失效到清除的 9ms 完全来自给定时钟与即时可见输入，不可推广为引擎停止延迟或预算建议。
所有评分与资格在普通评分轮读取同一逻辑时刻的人工世界；非普通评分轮没有使用历史分数选替代项。没有声称资格检查廉价，也没有以较少 start 推断游戏收益或体验提升。
夹具不归属于外部论文作者；h=50 和调度参数均是验收输入，不是推荐值。本包不改写原六组模型的历史结果，本次只复用两项反例。

运行中失败分支未注入；本夹具只测试执行完成、继续资格失效和开始失败，不覆盖运行中失败的处理。
