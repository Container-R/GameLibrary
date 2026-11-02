# EnTT v3 五键环境准备：独立执行前代码审查

2026-11-02。**接受本轮冻结代码的有限执行前审查；尚未执行v3，仍须主编另行授权。** v2遗漏当时规范要求的四个环境键，是当时流程不符合；本报告不撤销这一事实，也不改旧输入、输出或原生次数。

## 精确绑定与阅读

INPUT-MANIFEST.json SHA256：`a2d2d8ac37ca11278e737434549c90ee86f5d94047d8ce2f94ea036f28665b20`。

- PROTOCOL-v3.md：`1ead0f47acd33b85dfac79dd759cae9cd5f33b66d89bcaa4bba0d857f56760db`
- runner.py：`9054b515ae12a6f69253ec2f47c1ecc20c7e1c11b22a6c06c4e88c33a3ff3021`
- isolation.py：`bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970`
- fixture.cpp：`5bc3b3ad0ffdc2d22e6c11083ce92c60dccbaf1be149a3745c165ce62fa0463f`
- independent-oracle.json：`90169423b365a0a3a553462caff0be05ebb6672de6f58758959b9a5c139497cf`
- test_environment.py：`de45ba889d901ad84d2fdf3b1803240831dd830a59c1841fdf78f8fc4650f703`

完整读新协议、runner/helper、新8方法及作者交接；原10方法先前完整审过，本轮验证其字节完全相同并重新执行。fixture、checker、oracle、原协议审查、原清理测试及两个官方来源，共7项与v2逐字相同，复用已完成的完整源审，不假称新原生核验。11项输入摘要实核一致。helper与当前 `管理档案/工具/evidence/isolation.py` 逐字一致；BUILD/RUN的AST字面值与v2相同。

## 代码判定

每次 build/native 都经同一个 process 入口，分别新建 environment-build/environment-native。mkdir成功后才记拥有根；已有目录或符号链接拒绝，owned=false不会进入删除。prepare从干净PATH/locale字典构造五键；Popen实际使用返回的env，不是另建一个遗漏键的字典。打开输出文件后紧邻Popen再次validate，检查每个键精确匹配该根的绝对子目录且实际目录存在、非符号链接。根的各级组件也检查符号链接；没有先resolve掩盖链接。

根准备失败的部分子目录由拥有者清理；清理异常只另记FAILED，不覆盖已有首错。未创建进程时不进行组操作。进程启动后沿用v2不依赖poll的组清理：组信号与leader回收分别记录；已知组清理失败保留环境根。成功进程路径若环境删除失败，改为失败而非返回成功。原输入/复制输入/产物前后核验及pending正常关闭后发布正式receipt的门槛未取消，首错不会进入下一副本。

这里的根拥有关系基于调用者新建目录这一前提，helper本身不证明所有权。验证只是该时刻的检查，不能消除并发替换竞态；组信号成功加leader回收不等于观察到所有脱离组的后代终止。五键不是沙箱，也不限制所有可写位置或网络权限。协议已明确这些边界，不能把有限环境准备称为完整隔离证明。

## 独立实际纯测试

```text
python -B -m unittest discover -s research-drafts/entt-loader-native-v3 -p 'test_*.py'
python -B -O -m unittest discover -s research-drafts/entt-loader-native-v3 -p 'test_*.py'
python -B research-drafts/entt-loader-native-v3/independent_environment_tests.py
python -B -O research-drafts/entt-loader-native-v3/independent_environment_tests.py
```

- 原10+新8，共18方法，普通/-O各通过。
- 另独立5方法，普通/-O各通过。其中第一方法对两个phase×五键×四种改动（删键、改相对值、删目录、换符号链接）共40个子例逐一确认Popen和killpg均未调用，且自己创建的环境根被删除。
- 其余独立方法核：build/native两次mock启动实际传五键、均为已存在绝对目录且两阶段路径不同；成功进程后的环境删除失败必须拒绝；launch错误加清理错误保留首错且不发组信号；预先存在的phase符号链接及其目标内容不得删除。

所有Popen和killpg都被mock，临时目录只是合成文件系统输入。没有编译器、原生fixture或真实信号。上述普通/-O是同一组输入重复，不能换算成新增原生场景。独立测试脚本不加入作者已冻结执行输入清单，避免悄改此次输入。

## 执行前结论

未发现需再修的实质阻塞。允许主编基于此审查另行决定是否启动预注册预算：最多2次新构建、2次新native，120秒/10秒门槛、相同四阶段和8行输出，首错停止。当前本审查的实际构建数/native数均为0；v3未来结果必须单独记录，不改标v2为五键合规。无stage/远端更改。
