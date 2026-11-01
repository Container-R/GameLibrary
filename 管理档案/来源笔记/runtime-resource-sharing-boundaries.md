# 编辑候选资源前，先分清哪些对象仍然共享

离线导入回答的是怎样从源文件与设置生成资源。把资源加载到内存以后，还会遇到另一种问题：工具先准备一份候选配置，打算审核通过再替换活动配置；但刚修改候选，活动配置已经跟着变了。延后替换根引用，并不能撤销通过共享依赖发生的修改。

这份支持说明面向维护资源编辑、预览或候选发布流程的程序与技术美术。先用一张引用图说明检查方法，再限定到Godot 4.6文档和固定源码；不是新的运行实验或完整加载框架。

## 根、容器和元素是三个不同问题

假设根资源A保存一个数组，前两个位置都引用同一个内嵌资源B，第三个位置引用外部资源C：

```text
活动图： A ─→ 数组 [ B,  B,  C ]
                       ╰──╯
                      同一个B

一种有意的候选图：
         D ─→ 新数组 [ B′, B′, C ]
                       ╰──╯
                     同一个B′
```

字母是对象，不是文件名或值快照。这里D与A不同，新数组与旧数组不同，B′与B也不同；但C仍被两图共享。若只给新数组追加元素，旧数组不应因此增长；修改B′不应修改B；修改C则仍可能被活动图看见。这是图关系的推演，不是本次运行结果。

候选内部两个位置仍指向同一个B′，通常不是复制失败：原来两个使用位置就共同使用一个参数，复制时可以保留这个关系。若项目确实要它们独立编辑，那是另一项设计决定，要明确拆成两个对象，而不是把“深复制”自动理解成“每遇到一次引用就造一个对象”。

因此先列出候选准备修改的内容：仅数组结构、B的字段，还是也包括C。只读检查未必需要复制所有依赖；需要修改C时，上图就还不够隔离。检查时应同时看活对象关系和字段值：值相同不能证明是同一对象，根不同也不能证明依赖独立。

## Godot：重新加载与复制已有对象不是同一种选择

对于重新加载，Godot 4.6的普通 `CACHE_MODE_IGNORE` 不重用根及内嵌子资源缓存，但外部依赖仍按REUSE处理；`CACHE_MODE_IGNORE_DEEP` 才把忽略策略传播到外部依赖。固定文本加载器也分别设置这两个加载参数。[1][2] 所以“我没有复用根缓存”不足以回答C是否仍共享。

对于已有内存图，固定Resource实现先决定容器及子资源复制范围，再用重映射表复用已经生成的资源副本。普通深复制选择内部资源；扩大为ALL会把外部资源也纳入选择范围，但仍要遵守属性标志（flags）、脚本处理和构造要求，不能等同任意可达状态的完整快照。[3][4]

以图中普通STORAGE（标记为可存储的属性）数组属性、内嵌B和外部C为前提，排查时可按以下关系理解；不包括自定义属性行为：

| 选择 | 数组 | B | C |
|---|---|---|---|
| `duplicate(false)` | 与原图共享 | 共享 | 共享 |
| `duplicate(true)` | 复制 | 复制，两个位置仍共用一个B′ | 仍共享 |
| `duplicate_deep(Resource.DEEP_DUPLICATE_ALL)` | 复制 | 复制并保留内部别名 | 也复制 |

表格是指定前提下的源码解释，不是通用对象隔离承诺。实现只遍历STORAGE属性；脚本依赖与可变配置载荷不能混为一谈，特殊复制flags及用户代码也需另核对。内部资源的路径分类不是 `resource_local_to_scene` 场景实例化政策。本说明不创建场景，不处理循环容器，也不保证瞬态状态、信号、GPU或线程都随之隔离。[4]

## 还要确认：这次请求真的建立了新的加载任务吗

即使选对加载模式，同路径请求也可能在真正创建新的加载任务之前就被合并。固定Godot源码的用户请求登记以传入路径查找：若已有token，增加用户计数并直接返回，先于创建任务、写入本次 `cache_mode` 的分支。取得结果时再减计数，归零后移除该登记。[5]

因此，在相同路径的旧用户请求尚未收取完时，第二次请求返回OK，并不说明新模式建立了独立任务。给应用字典使用 `(path, mode)` 两个不同key，也不会改变底层按路径复用登记的规则。这里限定的是所读固定实现与相同传入路径，不外推路径别名、所有版本或所有加载器。

一种项目策略是明确拒绝冲突要求；另一种是由单一协调者管理请求，收取完旧请求后再发新请求，并明确每位调用方拿到什么。后一种还必须处理失败与生命周期，本文没有实现或验证协调器。共享结果分发只能用于事先接受共享的调用方，不能用来假装满足独立可写候选的要求。

请求登记结束，也不等于已经持有的资源引用随之失效。反过来，过早调用 `load_threaded_get` 可能阻塞；按文档先观察加载状态，再取结果，不能从首次查询已完成推断同步执行或不卡顿。[1]

## 与旧观察的关系

旧研究分别用简单原生资源观察过外部依赖共享、相反模式的同路径请求以及 `[B,B,C]` 复制关系。这些是不同的有限输入与流程，不能拼成任意资源图的整体验证。本说明只重新核对公开文档和源码，未重跑、未读取运行附件；历史观察及其失败诊断仍留在固定旧支持：[候选依赖](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/solutions/engine/asset-import-intent-contract.md#5-运行时补充候选根不同不等于可变依赖已隔离)、[同路径请求](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/solutions/engine/asset-import-intent-contract.md#6-第二次请求返回ok不等于新的加载策略已经生效)与[复制图内部别名](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/solutions/engine/asset-import-intent-contract.md#7-已加载的图再复制隔离原对象不代表拆散副本内部的别名)。所读固定源码与当时被测程序的精确对应并未由此建立。

实际选择时，先确定哪些修改不能泄漏到活动图、哪些副本内部共享应保留，再核对具体加载/复制入口是否兑现这一要求。不要把全量深复制当默认修复：它可能扩大复制成本，却仍不能替代对属性和用户代码的检查。

## 公开来源

2026-11-01重新读取。以下代码均固定于Godot官方提交 `35e80b3a8822a9df9be390814b62f44c0a9c69e8`；不把提交与某个安装程序自动认作同一实现。

1. Godot 4.6，[ResourceLoader](https://docs.godotengine.org/en/4.6/classes/class_resourceloader.html)：CacheMode及load_threaded_get/status说明。
2. Godot，[resource_format_text.cpp，1432–1453行](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/resources/resource_format_text.cpp#L1432-L1453)：普通与DEEP模式的外部依赖参数。
3. Godot 4.6，[Resource](https://docs.godotengine.org/en/4.6/classes/class_resource.html#class-resource-method-duplicate)：duplicate、duplicate_deep与DeepDuplicateMode；包含属性flags、必需构造参数及资源重复引用的限制。
4. Godot，[resource.cpp](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource.cpp#L268-L423)：`_duplicate_recursive`、`_duplicate`的范围、重映射与STORAGE遍历；另读508–552行左右的公开duplicate入口，确认默认INTERNAL与显式深复制模式。
5. Godot，[resource_loader.cpp，516–625行](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp#L516-L625)及[791–801行](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/core/io/resource_loader.cpp#L791-L801)：用户token提前复用、任务模式保存与收取计数。

---

[返回资产导入正文](../../GameLibrary/技术美术/环境管线/资产导入/换一台电脑后如何保持资产导入结果一致.md)
