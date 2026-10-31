# 同路径请求已完成但未收取：第二次cache_mode不是独立承诺

2026-10-31，原创Gradient图、两个实际无头新进程。对照已有外部依赖实验，这里不修改颜色、不重复对象图深浅复制，而检查**第二个调用方的请求参数是否建立独立结果**。

## 先冻结再运行

`contract.json`在实现前写入，SHA256 `f70e399b8aac89c6323ae29b78ebef281f0bf393f8fbe3fe727d700e216d1e50`。运行器固定核对该摘要。只有原创 `gradient.tres`：两个点，offset0/1，红/白。无图片、字体、插件或第三方素材。

各进程先同步REUSE加载并持有活动Gradient。第一threaded请求完成到LOADED后**不get**，再发第二次同路径请求；type_hint相同，use_sub_threads=false。然后status→get1→status→get2→status。所有引用持续保留，两次请求/两次get的计数在实际调用点递增；`CALL_JSON`逐调用记录和最终trace相互核对。

|实际案例|请求模式顺序|两次request返回|R1与R2|R1/R2与活动资源|
|---|---|---|---|---|
|reuse-then-deep|REUSE→IGNORE_DEEP|OK、OK|同一对象|同一对象|
|deep-then-reuse|IGNORE_DEEP→REUSE|OK、OK|同一对象|不同对象|

两例第一请求状态均在首个轮询帧观察为LOADED。第二请求后LOADED；第一次get后仍LOADED；第二次get后INVALID_RESOURCE。原始点色/offset、活动引用和受控输入文件摘要前后未变，已持有的active/R1/R2仍可读取。

**INVALID_RESOURCE在这里表示没有该路径未收取的用户请求登记，不表示所有已取得Resource对象失效。** 没有第三次get，没有尝试取消，也没有释放后观察或泄漏判断。

## 这不是worker竞态实验

第二请求明确发生在首请求已LOADED之后，因此发现不依赖“两个worker同时工作”。首请求是否还在后台运行不是本对照变量；实际微小资源没有IN_PROGRESS样本，也不据此判断线程数或加载性能。

在这两个有限输入中，返回OK不能让第二调用方推断自己的新cache_mode已经创建独立对象。它可能参与的是另一调用方尚未收取完的同路径结果。这与“正确DEEP请求会隔离哪些依赖”是先后两道不同门槛。

## 固定源码解释与身份界限

已实际读取的来源/完整行定位在 `source-gate.md`。官方固定提交 `35e80b3a8822a9df9be390814b62f44c0a9c69e8`：
- `core/io/resource_loader.cpp` 521–538、578–583：复用已有原始路径用户token并递增user_rc，提前返回。
- 601–625：新建任务才存入新的cache_mode，REUSE可直接取缓存。
- 791–801：get递减用户请求计数，至0移除路径登记。

[不可变源码链接](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp#L516-L625)。[Godot4.6公开文档](https://docs.godotengine.org/en/4.6/classes/class_resourceloader.html)说明按路径查询/取得threaded结果，但这些方法段未承诺重复请求各自拥有独立模式。因此不把观察称作违反文档或引擎bug。

本轮重新测得安装文件SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`，banner自报 `4.6.3.stable.official.7d41c59c4`，Engine字典hash `7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3`。与公开35e80b3a提交的精确构建对应尚未认证；源码为语义参照，不伪称已验证执行源码。两例同一字节身份程序，Linux6.18.57 x86_64、Python3.12.14，完整环境在summary。

对象ID按进程内活引用比较，允许有符号非零整数，Python JSON保留整数token精度；不经JavaScript Number做有损转换，不作跨进程/持久化资产身份。

## 对应用broker的原创建议

调用方需要共享、独立候选或不同加载策略时，应由应用明确协调冲突：拒绝不兼容请求、延后到先前请求收取完成，或让单一broker统一拥有请求并分发预先声明的共享结果。具体做法要按项目选定。

仅将应用字典key改成(path,mode)不够：如果仍向按相同路径复用的底层API提交两次，应用的两个key不会自动制造两个独立底层结果。本实验没有实现或验证通用broker，也不把所有引擎的合并规则说成相同。

## 归档与复现

`results/*.stdout.txt`含逐调用记录和RESULT_JSON；`*.json`是解析结果；`*.command.json`、`*.disk.json`、`invocation.json`和`summary.json`记录本轮命令、输入前后摘要、当前调用和源码/二进制身份。作者本轮首次完整运行两进程即通过，没有删去失败试跑。

复制当前 `run.py`、`main.gd`、`project.godot`、`gradient.tres`、`contract.json` 到独立目录，保留历史归档后运行：

```sh
python -B /path/to/copy/run.py
```

默认现有 `/usr/local/bin/godot`，可通过GODOT_BIN指定已安装程序。运行器先清旧summary、写新invocation，再进行-O/参数/引擎检查。两进程均通过才写summary。`engine_spawn_attempts`表示尝试启动次数，不把无法启动的进程描述为已执行；实际成功子进程另有returncode记录。

`check_freshness.py`在临时复制目录播种旧PASS后，实际检查-O与不存在引擎两条拒绝路径：均非零退出、旧summary移除、FAILEDreceipt、0次引擎spawn尝试；原始结果在 `freshness-results/`。这不是额外引擎运行或所有文件系统失败保证。目录不可写、清理本身失败或程序被强杀仍需消费者检查当前退出码与新invocation；不能把旧文件当最新成功。

每个进程20秒timeout、首请求最多600帧轮询；不是全部OS调用可取消保证，没有sleep或人为大型资源延迟。无网络、安装或资产下载。

## 有意不扩张的边界

只测试同一个完全相同路径字符串与两种模式顺序。无路径别名/UID解析对照、不同type_hint、多子线程、失败请求合并、重试/取消、第三次get、连续新请求、并发调用方、GPU、导出包、内存释放、跨构建复现或性能结论。当前状态是有限实测支持，不是API未来版本保证。
