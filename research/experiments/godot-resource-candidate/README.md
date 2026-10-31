# 新根资源不等于独立候选：threaded load 的外部依赖所有权

2026-10-31，实际运行两个最终无头进程。目标是为已有资产交接文章补运行时对象图边界，不是导入sidecar/UID重测，也不是线程竞争或引擎缺陷报告。

## 冻结合同及最小资产

先于代码保存的 `contract.json` SHA256：`267f450ad57c6a802346d0b9c7ac9d79e240871a64a2e6566f62e3810f6bd941`。

原创 `candidate.tres` 是GradientTexture1D，外部依赖 `gradient.tres` 是两个端点的Gradient，红→白；无图片、字体、插件或第三方素材。只读点颜色/对象身份，不采样生成纹理，不验证GPU显示。

每个新进程先以REUSE加载并持有活动根和Gradient，再对同一路径发起一次threaded请求（`use_sub_threads=false`），逐帧查询状态，LOADED后get一次。随后只把候选Gradient的点0改成蓝，不将候选赋给活动根，不修改磁盘文件。分别使用IGNORE、IGNORE_DEEP，互不共享进程缓存或未收取的请求token。

## 最终实际观察

|模式|活动根/候选根|活动Gradient/候选Gradient|只改候选后活动点0|候选点0|
|---|---|---|---|---|
|IGNORE|不同对象|同一对象|蓝|蓝|
|IGNORE_DEEP|不同对象|不同对象|红|蓝|

前后活动根及两层对象ID均保持；活动根未被替换。每例的四个受控输入文件摘要前后相同。活动根中读到的Gradient颜色与单独保留的Gradient引用一致。

两例实际状态序列均为 `[3]`（LOADED）：首个观察帧已完成，没有观察到IN_PROGRESS。这不证明加载同步执行，也不提供延迟、加速比或不卡顿保证。所有内容修改在加载完成后的主线程；没有并发修改同一Resource。

结论限定于这个图：**候选根不同不是可变依赖独立的充分条件；仅延后发布根对象，不能隔离此前对共享依赖的修改。** 深度忽略是此图的有效对照，不是所有资源/插件/全局单例的通用隔离保证。只读候选审核可能根本不需要深复制；应用应按实际修改范围决定所有权与成本。

## 来源链及程序身份

`source-gate.md`保留实际读取路径、不可变源码链接与访问范围。核心依据是Godot4.6 ResourceLoader CacheMode说明；固定官方提交 `35e80b3a8822a9df9be390814b62f44c0a9c69e8` 的 `doc/classes/ResourceLoader.xml`、文本加载器1432–1453及外部加载517–519，可见IGNORE的外部依赖模式为REUSE，而IGNORE_DEEP继续传播深度模式。`core/io/resource_loader.cpp` 的用户token复用分支促使本实验限制为每进程一个同路径请求。

本轮实际二进制SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`；程序banner自报 `4.6.3.stable.official.7d41c59c4`，Engine字典hash为 `7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3`。公共35e80b3a源码与它的精确构建对应仍未建立；official字样不是本库认证。版本和哈希是本轮重新读取，不从旧记录回填。

Linux6.18.57 x86_64、Python3.12.14；全部实际版本字典、命令、源码摘要及输入前后清单在 `results/`。身份应只在**单进程活对象之间**比较；不同进程可出现相同数字，不意味着跨进程对象相同；这些数字也不能作为持久化资产ID或跨会话存档身份。

## 必须保留的初始失败

`historical-initial/`保存最初runner、GDScript、原始stdout/stderr和失败receipt。该次只启动IGNORE一个引擎进程，颜色/别名观察已出现，但Python判据错误要求instance ID为正；实际GDScript输出为非零负整数，故拒绝，未生成成功summary。

修正仅将身份有效性判据改为整数且非零，并继续检查同一活对象的相等/不等与前后稳定；另收紧版本家族检查为4.6.3。没有修改资源图、预期颜色、GDScript或冻结合同。最终重新跑完整两进程。因此作者实际总启动数是**初始失败1次 + 最终2次**，不能写成从未失败的两次测试，也不能把负ID推断成内存损坏。Python JSON解析保留整数精度；这些ID超过JavaScript安全整数范围，不应经有损数字转换后再比较。

## 重现与新鲜性

先复制当前 `run.py`、`main.gd`、`project.godot`、两个tres、`contract.json` 到独立目录，再运行：

```sh
python -B /path/to/copy/run.py
```

默认使用 `/usr/local/bin/godot`，可由GODOT_BIN指定现有引擎；不安装新程序。结果写复制目录的results，旧归档应先保留。运行器先删除旧summary并写新invocation，再拒绝-O/非法参数或检查引擎；最后只有两个案例全部通过才写成功summary。读取方必须同时检查当前进程退出状态、当前invocation与summary对应，不能仅看文件存在。

`check_freshness.py`已在临时复制目录播种旧PASS，分别调用-O与不存在的引擎路径：两例都非零退出、删除旧summary、写FAILED invocation，记录0个引擎进程。原始结果在 `freshness-results/`。这两项不是额外引擎运行，也不是所有文件系统故障的新鲜性证明。若结果目录不可写、清理自身失败或进程被终止，不能保证完成receipt更新。

每引擎进程20秒外部timeout，GDScript最多600帧轮询；这些是实验预算，不是对所有OS调用可取消的保证。无强制sleep，没有制造大资产来要求必须观察到加载中。stdout与stderr、非零返回、初始失败均保留，未删错误以冒充成功。

## 未测边界

无导出包、GPU、实际场景替换、取消请求、并发同路径请求、多子线程、REPLACE模式、任意资源图、跨构建复现、内存释放或线程安全证明。source-backed范围不因两次运行自动升级为普适verified。独立重复验收另行记录，不把作者重跑当独立来源。
