# 回滚表现对账：复现实验

[返回正文](../../../GameLibrary/网络与在线服务/实时同步/回滚与表现/网络回滚重算了几帧，接触音为什么播了两次.md)

- `check_replay_suffix.py`：回放整数小游戏，从第 1 帧后的快照重算第 2–5 帧。对比每步即播、完全抑制、在追赶后对账，保留回滚范围外仍有效的火把，不重复落地、撤销旧光束、补发新拾取及光效。
- `check_reconcile.py`：输入已经协调的完整记录，检查事件键、对象世代、载荷、过时预测瞬态、晚到确认、未来时钟和重复消费。Presenter 只服务一局，因此示例的键省略对局 ID；实际跨局复用应重建表示层记录或把对局纳入键。已消费集合不回收，只代表可重复的小型输入。

```sh
set -e
python3 -B check_replay_suffix.py >/tmp/gl-rollback-suffix.json
cmp /tmp/gl-rollback-suffix.json replay-observed.json
python3 -B check_reconcile.py >/tmp/gl-rollback-present.json
cmp /tmp/gl-rollback-present.json observed.json
```

无真实网络、音频混音或游戏角色输入，不能据此评价可感受的延迟、音量、跨进程崩溃或跨服务确认一致性。
