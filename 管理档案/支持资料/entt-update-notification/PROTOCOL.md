# EnTT 普通字段写入与更新通知：有限观察协议

状态：仅准备，等待独立执行前审查与主编单独授权。未编译、未运行原生、未运行消费者或纯测试。固定来源见本包 UPSTREAM-SOURCE.json 及下列官方源链；独立源码审查结论由配套审查摘要另行绑定。

## 输入与目的

固定 EnTT v3.13.2 commit `78213075654a688e9da6bc49f7f873d25c26d12c` 的官方 single_include/entt/entt.hpp，复用已取得的原样本地头及 LICENSE，准备在包内 source/ 下，不依赖外部研究目录。公开包可不附3MB头，但须按 UPSTREAM-SOURCE.json 从固定官方提交准备并核对身份。独立 SOURCE-REVIEW.md 已闭合三个条件，本协议仍待执行前审查。

- 官方定位：https://github.com/skypjack/entt/blob/78213075654a688e9da6bc49f7f873d25c26d12c/single_include/entt/entt.hpp
- 头 SHA256：`31be51708c7325ecb7877182fa9ee68a20fb2121ce6bcd6c1687506f0fb1c8b5`。
- 普通 `Speed { int value; }`，默认 registry/storage，无自定义setter。
- 每个条件创建独立 registry、有效实体和已有 Speed=3。构造在订阅之前；监听 on_update 后再操作。观察者缓存初始3，回调每次实际读取当前字段、追加读值并更新缓存。
- 仅观察一个同步写入与返回后的状态。不含销毁通知、异常注入、重入、线程、实体映射、定制storage或真实游戏。

## 冻结三条件与字面预期

| case | 操作 | 实际字段预期 | 回调次数 | 回调读值序列 | 缓存 |
|---|---|---:|---:|---|---:|
| 0 | get引用直接赋1 | 1 | 0 | [] | 3 |
| 1 | patch函数赋1 | 1 | 1 | [1] | 1 |
| 2 | patch函数赋3 | 3 | 1 | [3] | 3 |

无通知由真实回调记录为空和计数0共同表述，不打印推测出的回调。第三条件独立从3开始，不是第二条件之后变回3。三个条件均由同一个可执行程序顺序执行；首个检查失败即停止。fixture先输出该条件实际观测并flush，再检查字面预期，不把期望代替观测。初始化失败在该条件操作前停止，没有成功结果可冒充。

输出是严格三行JSON，每行字段恰为case、initial、valid、has_speed、connected_initial、value、callbacks、seen、cache；所有数为整数，seen是整数数组；valid、has_speed、connected_initial为实际初始化布尔观测，均须true。连接bool仅初始化检查，不宣称通用实时连接探测。按case0/1/2顺序。消费者拒绝重复键、非有限数、布尔伪整数、浮点伪整数、额外/缺失字段、行数/顺序/值异常及非空stderr。expected.json为预先字面文件，不从输出生成，其固定摘要在checker中。

## 运行准备与数量

runner.py每次只接受一个尚不存在的输出目录。拒复用及符号链接路径；不删除旧结果。一次尝试最多一个编译进程（60秒）与一个fixture进程（10秒），无自动重试。若后续批准两次，分别在两个新目录复制同一冻结输入；是同操作者同条件重复，不称独立复跑或新增条件。

编译argv固定：`c++ -std=c++17 -O0 -Wall -Wextra -pedantic -Isource fixture.cpp -o fixture`。工作目录为该次新副本。执行argv：`./fixture`。不使用shell，无安装、额外版本探测、网络调用或追踪声称。PATH采用Python os.defpath；只查可执行名称存在，不记录安装路径/指纹。若编译失败或任何stdout/stderr诊断，停在构建，不执行fixture；不自动改flags或上游代码。

每个build/native阶段各有五个独立空目录HOME、TMPDIR、XDG_DATA_HOME、XDG_CONFIG_HOME、XDG_CACHE_HOME，启动前核空且非symlink。环境从空集合建立，仅加PATH、LANG=C、LC_ALL=C及这五键，不继承凭据/配置。五目录不是安全沙箱或禁止所有文件访问/网络的证明。此任务不另加网络追踪。

原始头、LICENSE 与五个自有输入文件由INPUT-MANIFEST绑定；复制后逐字节hash核对，结束再核原输入及副本。manifest本身的冻结摘要由审查报告和执行授权绑定，不以可改清单单独证明身份。

## 失败与接收

超时、启动后异常、非零退出、未审诊断及正常返回收尾均尝试清理拥有的整个进程组，TERM后KILL，再有界wait；不因leader已退出而省略组清理。保留首异常类型、二次清理/写日志错误；不承诺所有存储故障时仍能落盘。不自动继续第二个条件或下一次尝试。

原始stdout/stderr及阶段记录保留本地，不以缺行补造零结果。消费者只证明三行有限观测符合字面预期；整次接受还必须有外部runner退出0、最终receipt.status=pass及前后身份核验成功。receipt先写pending，正常close后再replace为canonical；未发布或写入失败均不是PASS。不声明崩溃持久性。

公开意向字段只含相对argv、源/输入/输出身份、返回值、有限观测和范围；原始构建诊断先审核再决定是否公开，不直接发布内部路径、进程标识或安装二进制指纹。没有运行结果时不能生成成功观察或宣称已验证。

## 解释停止线

只回答普通字段直接写入与显式patch的更新通知差别，以及一次通知是否蕴含数值改变。即使三条件成功，也不证明任意写入被捕获、全量缓存一致、Factorio使用EnTT、线程安全或所有版本契约。源码审查、实现审查和后续执行授权分别完成，不由此协议自动授权运行。


## 执行前 v2 修订

v1 输入清单 `4b04b18d370dab64541d7da4498a0a32c36b44343476427c1a08006f2f16296a` 及自有文件保存在 history/v1。独立纯mock发现三处门槛不足，尚无原生尝试：

1. 清理leader不足以确认组消失。现于TERM/KILL和有界leader wait之后，用killpg(group,0)最多31次检查、间隔0.1秒；未消失或权限/其他异常均拒绝接受。这个有限观测不是任意后代或全系统进程证明。
2. 构建后、原生返回后必须重新检查原输入及全部副本，特别是导入checker前；变化即停，不先执行变更消费者再依靠最终后检。
3. 启动时记录INPUT-MANIFEST原字节摘要，复制后、构建后、导入前和最终检查均要求其未变，receipt绑定前后摘要。仍须外部授权绑定启动清单身份，不能用自报摘要替代审查。

fixture、三行预期与checker不变。仅runner和协议改变，不扩展条件，不授权编译或原生执行。
