# EnTT Link 消费器保留句柄修正：独立闭合

2026-11-02。**接受此次最小修复的代码审查。** 旧接受初稿及撤回原字节保留；本结论仅绑定下列新版本，不把旧消费者改称已经通过这些反例。尚未授权或执行C++、native、runner入口或真实信号。

## 最终身份

- INPUT-MANIFEST：`7af256d00360edbed9722d80196503548afada426016060312f42f96ef1faf38`，14输入。
- checker：`21dffbb35f6ae3365c8d8c14b581f6e36e566da449464446ff484a3cc05a2a2e`
- runner：`1d7a61cb4f0e2a89350b5939c0ab4da23171f7cd5e461cf43a90466e97f3bd69`
- independent-oracle：`92f2fe2c5dbfe5e3fa3a8a281b171e2bbde033bdcea0257ea86658f9d32eeb15`
- PROTOCOL-REVIEW-v2：`5aeb287381c86ecbb5c81ce95546d95cb8056b06d3b0a36e796c8efd7333fa68`
- fixture未变：`a0ef9f35226c791bfb8917541737faabfcedd35a578bb07462739995e8eb7e57`

## 实际差异与历史完整性

完整读RESERVED-HANDLE-FIX、新独立协议澄清、新测试及实际文件差分。独立对history/rejected-v1内原manifest `bb6af91bca415c50ae4921e5744f33f389d01369d330537dd047bf1e8a2e1ede` 的全部13项重算，全部匹配，包含原oracle `3bb0f324154852cf070c0e92778f8481bc7c2aed6a4d27a25858c6c970558d03`，没有新版oracle混入旧身份。当前14项也全部匹配。

checker仅新增对R/H/S/B/L的保留index/version拒绝。因先前handle函数已限制范围，这与index<0xfffff、version<0xfff等价。prepared两个map仍按规范全一null哨兵接受，没有把live约束错误应用到未映射值。跨阶段稳定关系保证其他阶段同一live身份也受约束。runner仅在原允许集合中增加PROTOCOL-REVIEW-v2，不改五键准备、进程/目录清理、首错、编译argv或正式receipt发布。

fixture、协议/schema、原协议审查、helper、两个生命周期测试及源/license共9项与rejected-v1逐字一致。oracle的解析后差分只有新增live_handle类型约束、相同约束的invariant和clarification；其余token/阶段/关系、成功行数和原生条件没有改变。

原CODE-REVIEW初稿 `fa1b5fc73a0345cd759acb9431add78c3fef3dce62b232e487f08daa6a8d809a` 与带撤回的报告 `f2f90927c06e2cd7e592771a9958168e7f71afa5934889b700442de683ae2493` 均核对保留。此前false accept是实际纯消费者检查缺陷，非原生失败；21方法曾通过的事实不替代本次补齐。

## 本轮独立执行的纯检查

普通与-O分别执行作者全部测试，每模式23方法通过：18生命周期方法、5消费者方法。命令为：

```text
python -B -m unittest discover -s research-drafts/entt-component-reference-native -p 'test_*.py'
python -B -O -m unittest discover -s research-drafts/entt-component-reference-native -p 'test_*.py'
```

另独立构造一套五个互异合成角色值R/H/S/B/L=17/18/16/19/20，按语义字段重填全部token和阶段，不直接复用作者新增递归替换函数。逐角色替换为保留索引值0x000fffff及保留版本值0xfff00000，重算最终valid集合关系和equals_seed，共10个一致性负例。**同一10输入在保留的旧checker+旧oracle上全部被接受，而在新checker+新oracle上全部以准确错误 `live_reserved_handle` 拒绝。** 不是靠另一个字段不一致偶然失败。

再把五个合法角色都设为非零且非保留的版本2、保留prepared真实null，独立正例接受。证明本修复没有把所有合法值锁成版本0。上述独立挑战普通/-O各执行一次；两模式是同组输入重复，不增加native覆盖。原语义/编码拒绝及描述性valid真/假正例仍在作者套件通过。

## 接受边界

保留值检查只是报告为live身份的必要条件，不是registry.valid的完整替代或任意伪造输出的真实性证明。来源/目标归属、组件未转换、实际getter、输入身份和执行结果仍必须分别核查。当前仍为1个普通Link条件，11行，最多2新构建/2新native的未来预算；没有把旧无组件结果算入。

本审者此次未启动compiler、native或runner.main。可供主编与另一独立消费者审查结论合并后决定新执行授权；本报告本身不触发执行。没有作者文件、stage或远端修改。
