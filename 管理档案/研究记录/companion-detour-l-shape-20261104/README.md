# Detour L 形网格：直连受阻不等于无路可走

2026-11-04。这个小实验在同一个导航网格上观察到：**L→C、C→F 两条直连通过，L→F直连受阻，但findPath仍返回完整绕行通路。** 四次调用都返回SUCCESS；只保留成功位，会丢失本例中直连是否受阻的区别。

## 输入与实际结果

使用未修改的Detour v1.6.0固定提交 `6dc1667f580357e8a2154c28b7867bea7e8ad3a7`，直接构造三块单层正方形，没有Recast烘焙。坐标为(x,y,z)，全部y=0：P0覆盖x,z∈[0,1]，P1覆盖x∈[1,2]、z∈[0,1]，P2覆盖x,z∈[1,2]。完整共边连接成P0↔P1↔P2；P0/P2仅角点相接，没有通路链接。

L=(0.25,0,0.5)、C=(1.25,0,0.5)、F=(1.25,0,1.5)，分别在三个polygon严格内部。这是新构造的L形输入，不是支持文章的方形障碍纸面例，更不是游戏实现、地图或参数复原。

| 调用 | 原始状态 | 返回polygon | 记录的t |
|---|---|---|---|
| raycast L→C | 0x40000000 | P0、P1 | 3.4028234663852886e+38 |
| raycast C→F | 0x40000000 | P1、P2 | 3.4028234663852886e+38 |
| raycast L→F | 0x40000000 | P0 | 0.5 |
| findPath L→F | 0x40000000 | P0、P1、P2 | 不适用 |

前两条记录的t等于本次float_max；第三条停在P0边1，记录法线(0,0,-1)。由原始坐标和t=.5算出的交点是(0.75,0,1)，不是另一项查询。每次实际分配三槽，完整槽值见输出；所有状态都没有附加位。

[main输出](observations/main/native.stdout)与[repeat输出](observations/repeat/native.stdout)各2562字节，原字节一致，SHA-256均为 `4367e42182c8cd058cf4b773ea1002575272264c60ce220bf5d5434c4bc26c40`。实际引用4/5/6分别绑定P0/P1/P2，不把这些数字或data_size=496当作跨环境常量。

## 发生了多少次运行

同一操作者、同一环境中的两个全新隔离副本，各构建一次、启动fixture一次；合计2次构建、2次启动、6次raycast和2次findPath。它们不是八种场景、独立操作者复现或跨平台验证。[独立结果审查摘要](RESULT-SUMMARY.md)接受的是这两份有限记录，没有新增原生调用。

[main公开回执](receipts/main.json)与[repeat公开回执](receipts/repeat.json)明确标为原回执的衍生：保留输入/输出绑定、退出状态、调用数和检查结果，将三份相同的27项身份映射折叠为清单绑定与相等性检查。制作公开包没有重跑，native.stdout及validation.json保持原字节；不包含私有运行位置、进程或程序二进制身份。

两次构建退出0、stdout为空，stderr均与[644字节精确诊断](reviewed-build-stderr.txt)一致。该上游class-memaccess警告没有被压制；仅这份完整诊断或空stderr获准，不放行整类警告，也不据此认证C++跨实现安全。

38个纯合成方法在普通Python及`-O`模式各通过。同一集合重复不是76种覆盖，mock过程也不是原生运行。[消费结果](observations/main/validation.json)标为consumer_only，须与实际输出和回执一起看。

## 复现材料

[CODE-MANIFEST](CODE-MANIFEST.json)绑定十个执行输入；运行器另核清单自身及十六个上游文件，共27项身份。本包保留执行时输入字节。[协议](PROTOCOL.md)与[数据契约](SCHEMA.md)中的执行前措辞是冻结历史，不用后来成功倒写它们。

本包不含上游源码或编译程序。[官方固定源地址](SOURCE-URLS.md)逐项对应[SOURCE-MANIFEST](SOURCE-MANIFEST.json)。将取得的文件放到本包 `upstream/` 加清单路径的位置，例如 `upstream/Detour/Source/DetourNavMeshQuery.cpp`，保留原许可。核对SHA-256，并以Git的 `blob <字节数>\0` 前缀加文件原字节计算Git blob SHA-1。[SOURCE-CHECK](SOURCE-CHECK.json)只是执行前身份检查，不是新运行。

自行准备C++工具链和Python，运行器不安装或下载。只读已有观察可用：

```sh
python3 -B consumer.py observations/main/native.stdout
python3 -B consumer.py observations/repeat/native.stdout
```

完整源文件就位后，纯测试为：

```sh
python3 -B -m unittest -v test_consumer test_runner
python3 -B -O -m unittest -v test_consumer test_runner
```

审查当前环境、冻结代码与精确诊断后，才启动有限重复：

```sh
python3 -B runner.py --execute-approved --diagnostic-policy reviewed-exact
```

`--execute-approved`是操作者声明，不替代审查。默认诊断模式为empty-only；上述命令明确选择精确候选，任何新增/改变诊断仍停止。需全新副本且没有execution目录，不覆盖或删除旧回执重试。每次构建限60秒、fixture限10秒，首份失败不启动第二份。七个隔离环境目录和自有进程组检查不是完整安全沙箱或操作系统网络隔离保证。

本次没有身体碰撞、角色移动、台阶、重叠楼层、动态障碍、动画或玩家体验测试，不证明几何最短路或实际抵达。原作经验、纸面示意和本次库调用保持不同证据范围。[材料来源说明](SOURCE-ALLOWANCE.md)只列来源和交付类型，不另复述API。

[返回同伴跟随正文](../../../GameLibrary/游戏人工智能/移动导航/同伴跟随/同伴跟随候选位置的前方连通检查.md)
