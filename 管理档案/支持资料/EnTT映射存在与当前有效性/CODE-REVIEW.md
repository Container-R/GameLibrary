# EnTT continuous_loader 执行前独立代码审查

2026-11-02。结论：**消费者与固定源调用机制在下述范围内通过；执行前仍须修正两处停止/清理边界并重新冻结，当前不接受启动构建或原生执行。** 本报告不是原生结果。

## 精确绑定与实际阅读

审查 INPUT-MANIFEST.json SHA256 `f13aa9f24d308abd90f9430af07abe6ba5c9f3e3aeb93ed18d461a3bf919a772`；8项输入逐一 SHA256 相符。

- PROTOCOL-v1.md：`4ea528e56fe5970c3d45de313e6fdaa5a3cf11471cd5f3b203f6081eab9d329e`
- fixture.cpp：`552f5c5c09d94a182f247d87aee5ee560b216c707864c19c85ffd47769a35f0c`
- runner.py：`d47971ea1e309fa290d84c19a12fc68e118d2b0b1b53958365c0edbd4bd0f1d3`
- checker.py：`788f72e5e978b90a14047822cd28d023e49c7495d75119cc856525a8cc78d732`
- independent-oracle.json：`90169423b365a0a3a553462caff0be05ebb6672de6f58758959b9a5c139497cf`

完整读协议、协议独立审查、夹具、消费者、runner、字面预期及主编来源核查。重新读本地固定官方单头的 snapshot writer（39261–39288）、continuous_loader restore/get/contains/map（39455–39469、39549–39593、39621–39638），registry valid/create/destroy（38125–38186）。单头大小 3,085,766 字节、SHA256 `31be51708c7325ecb7877182fa9ee68a20fb2121ce6bcd6c1687506f0fb1c8b5` 和 Git blob `b3a763a203cb7c2acc467de1dc97920562721989` 实际重算相符；对应此前固定的官方提交 `78213075654a688e9da6bc49f7f873d25c26d12c`。本轮没有重新下载整份源或认证任何编译产物。

## 必须修正

### 1. 已退出父进程不能作为进程组已清理的证据

`process` 的异常分支仅当 `proc.poll() is None` 才清理组；返回码和诊断拒绝又位于该 try 之外。因此存在明确控制流反例：已创建的编译器入口先退出，仍有属于该组的后代；`wait` 返回非零或产出被拒诊断，随后 Stop 不会触发组清理。超时分支中 kill/wait 若失败，而 leader 已结束，外层也可能跳过剩余清理。

最小要求：记录已经创建的组，在拒绝、超时、异常路径清理该拥有的组，不把 leader 的 poll 结果当组存活判断；保留首错，有限等待，组不存在可作为正常清理结束。增加纯 mock 的 leader-exits-first、返回非零、非空诊断和清理异常用例；不需要真实子进程或信号实验。该发现是源控制流审查，不是已观察到残留进程。

### 2. 当前夹具会越过已经不符合协议的阶段继续操作

`emit` 只打印值。`before_load` 若已不符合表仍执行首次 get；`externally_destroyed` 若 map/contains/有效性/活跃数等已偏离仍执行第二次 get。消费者在整个 fixture 返回后才拒绝，不能兑现原生四阶段“首个前提/检查失败停止”的边界。已存在的 loaded 有效且非 seed 前置检查只覆盖部分条件。

最小要求：每阶段先取得并保留真实观察，再显式核该阶段必要字面条件与已知跨阶段关系；不符时输出、flush 并非零终止，不能进入下一阶段。不要将观察改成 oracle 常量，不要改变源调用、输入或成功8行 schema；失败应保留已取得的前缀。这不是增加场景，也不要求注入真实 EnTT 故障。

## 已接受的机制与消费者检查

夹具确实调用官方 snapshot/get、continuous_loader/get/map/contains、registry create/destroy/valid，不是重写加载器模型。归档使用 uint32 与 entity 两个不同重载和 variant 类型；同一 tokens 经两个独立只读游标读取。默认实体 storage 的 free_list 用于此特定实体路径的活跃数，未偷换为 storage.size。来源与 seed 不销毁，第二次加载复用同一 loader；输出包含真实完整标识和分解，而非硬编码分配索引。

独立脚本 `independent-consumer-check.py` 仅构造明确标注的合成 JSON，不调用 runner、编译器、fixture 或任何真实进程管理。执行命令：

```text
python -B research-drafts/entt-loader-native/independent-consumer-check.py
python -B -O research-drafts/entt-loader-native/independent-consumer-check.py
```

每模式同一组：1个合成正例接受、25个反例拒绝；不是两组原生覆盖。反例包括重复 JSON key、bool 冒整数、整数字段冒布尔、错误版本/位分解、越界句柄、缺失 initial、销毁后 map 改变、重载仍旧标识、来源改变、归档来源或消费数错误、重复阶段、缺/额外字段、7/9行、非有限值、缺末尾 LF、CRLF、无效 UTF-8。8项身份及单头 Git blob 也通过。字面 oracle 的值与独立协议表逐项相符；消费者对输入的类型、字段顺序、句柄分解及跨行关系有独立检查，不信 fixture 自报 PASS。

runner 的固定 argv 与协议一致，保留 Werror，环境不继承用户编译标志。fresh 输出路径拒绝复用，每副本构建前核复制输入，后核输入和产物；原输入及 manifest 后检完成后才设置整体 PASS。局部 content_check 明确位于副本中，不代替最终 receipt。首次失败不会进入下一副本。以上代码层优点不抵消前述组清理与阶段停止缺口，也不是实际失败注入或运行保证。

本次实际编译数、原生调用数均为0。未调用 runner，未进行网络或引擎操作；没有 stage/远端更改。应保留当前版本及本报告的初次发现，修订后仅做有限差异闭合，再由主编决定执行授权。
