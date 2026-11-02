# 执行前的两项真实纠错

## writer调用形状

固定 [snapshot.hpp L78–110](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/src/entt/entity/snapshot.hpp#L78-L110) 的 std::apply 调用lambda；lambda内部逗号折叠对每个参数分别调用archive，不是一次archive接收owner和组件。官方 [writer测试 L88–130](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/test/entt/entity/snapshot.cpp#L88-L130) 使用单参数lambda，与此一致。原审查错误在实现前被发现并撤回；最终实现本条件7次单参写和7次单参读。没有运行上游测试来得出这一源码结论。

## 被拒绝的旧消费者

`rejected-consumer/` 仅保留四份原字节：checker.py、独立oracle、旧INPUT-MANIFEST及原独立失败脚本。**不是完整旧native输入包**，也没有旧fixture、runner或上游单头；旧manifest只作为脚本绑定的历史身份，不能拿该目录启动旧原生观察。

原脚本只检查这三份文件摘要、构造合成记录并调用旧checker，无上游源依赖。可从本目录执行：

```text
python3 -B rejected-consumer/independent-consumer-check.py
python3 -B -O rejected-consumer/independent-consumer-check.py
```

预期两次均**非零退出**，不是应该修成绿色的失败：4个合成正例接受，91反例中81个拒绝，另10个保留索引/版本反例被错误接受，stdout列出false_accepts。这是旧缺陷的可复查保留；traceback可能显示复查者自己的工作路径，不应直接当公开日志上传。当前公开整理没有重跑这些命令。

固定 [entity.hpp](https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/src/entt/entity/entity.hpp#L220-L275) 的null比较按索引，保留版本另有语义。修复只对已知活跃R/H/S/B/L排除保留index/version，prepared真实null仍允许；没有锁死全部版本为0。修复后的源与独立脚本在父目录，最终实际输出不含这类伪造活跃值。

这两项都是执行前问题，不是假装发生过的原生失败。公开保留最小可重现材料，不重复分发全部工作草稿或原始环境回执。

[返回本观察说明](../README.md)
