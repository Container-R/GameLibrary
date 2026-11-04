# Ninja 依赖变化有限观察

[返回说明文章](../生成文件已经更新，为什么后续产物仍是旧内容.md)

这份附件保留两张小构建图在初次、无变化、改输入、再无变化时的完整观察。目标是看清 `|` 和 `||` 的区别，不是测试真实游戏资产编译器或 CMake。

## 实际观察范围

2026-11-04，在一套本地 Linux 环境中，从官方 Ninja v1.13.2 固定提交 `3441b633c2fe2c494e958780ba0f4227b1327634` 构建一次工具，再由同一操作者在全新目录中做两次重复。每次重复有两个分隔符不同的图，每个图四阶段，共16次请求 bundle.txt；执行复制和记录的辅助程序（helper）实际产生14次开始及14次完成。16次 Ninja 调用都成功退出。

每次重复，隐式组启动4次 helper（初次2次、改动后2次），order-only组启动3次（初次2次、改动后1次）。改为 B 后，order-only 组 generated.txt 是 B，bundle.txt 仍是 A；随后的无变化调用没有修复它。

工具构建及6次版本查询不计入16次图调用。更早的一次启动因提供了旧的冻结输入标识，被前置检查拒绝，尚未创建执行目录，也没有启动版本查询、编译器或 Ninja。它是准备阶段的检查拒绝，单独保留，不能记作一次失败的原生图观察。

## 包内文件

- [recipe-v1.txt](recipe-v1.txt)、[recipe-v2.txt](recipe-v2.txt)：实际采用的原创16字节输入，分别为 A 和 B，均以换行结尾。
- [fixture_helper.py](fixture_helper.py)：原始 helper 的字节副本。generate 复制 recipe.txt 到 generated.txt，bundle 复制 generated.txt 到 bundle.txt，并记录开始、完成和内容摘要。
- [implicit.ninja](implicit.ninja)、[order_only.ninja](order_only.ninja)：公开阅读用图。两者只差下游的 `|`／`||`，不用 `$in`。
- [observations.json](observations.json)：全部16阶段的实际文件字节、摘要、大小、相对修改时间、进程退出码和 helper 事件。
- [check_observations.py](check_observations.py)：只读取并检查记录，不调用 Ninja、helper、编译器或网络。
- [artifact-manifest.json](artifact-manifest.json)：绑定本目录其余8个文件的大小与SHA256，不包含自身。它用于辨认这份公开材料，不认证执行者或整个工具链。

## 公开图和实际执行图有什么不同

实际执行固定了 Python 解释器和 helper 的机器路径。公开图只将这两个绑定替换为 `python3` 和当前目录的 `fixture_helper.py`，生成／消费关系与其余字节不变。原 helper 字节未修改。**这些可移植图没有重新执行，不能声称附件本身已经在任意机器验证。** 若读者另行运行，应自行选择与检查解释器和 Ninja 环境；`python3` 会采用该环境 PATH 的选择，不等于本次实验的固定解释器。

要读懂方法，可为每个图准备独立空目录，将所选图另存为 `build.ninja`，放入 helper 和作为 `recipe.txt` 的 A，再请求 bundle.txt；随后不改内容再请求一次，只改 recipe.txt 为 B，再请求并做最后一次无变化检查。实际调用固定为 `ninja -j 2 -v bundle.txt`，按一个隐式图、一个 order-only 图的顺序完成一次重复，然后在新目录完成第二次。这里是复现方法说明，不包含自动运行或安装工具的脚本。

实际时间控制是：写入初始 A 后等待2.1秒；改动前等待2.1秒，再写 B，并检查其mtime严格大于该臂两个旧输出；之后再等待2.1秒，确认源文件不在未来，才开始变化后的构建。生成文件应不早于源，下游新输出应不早于生成文件。没有手动设置文件时间。任一时间前提不满足就停止，而不是延长等待、调整时间或删除产物来取得预期结果。

两次重复使用同一个已构建 Ninja，不是独立操作者或跨环境复现。图没有 restat、depfile、dyndep、phony 或缓存；没有测试完整资产转换、任意依赖图、并发写入或性能。

## 怎样检查公开记录

在有 Python 3 的环境中，从本目录执行：

```text
python3 check_observations.py
```

检查器先核对公开文件清单，再检查16阶段的完整顺序、进程退出码、A/B字节与摘要、开始／完成事件、相邻阶段衔接、严格时间关系和不变输出，最后核对两个重复的4/3调用次数。它不读取原始私有日志、不启动任何构建工具，也不能独立证明数据来源。

mtime已按每个图的“初始recipe时间”统一减去同一个基准，记录为 `mtime_offset_ns`。因此保留该图内的间隔、严格大小关系和未变化事实，但去掉绝对时间。不同图的零点不同，不能拿它们比较先后或性能。实际字节用 `bytes_hex` 保存，SHA256和大小可以由这些字节重新计算；不是只保留“通过”标签。

检查器还可接受 `--record` 指定记录副本，用于检查故意改错的记录会不会被拒绝。那只是记录检查器的反例，不是新的 Ninja 运行。不要修改此目录内已绑定的观察数据来做试验。

## 原始来源与许可说明

- [官方 v1.13.2 提交](https://github.com/ninja-build/ninja/commit/3441b633c2fe2c494e958780ba0f4227b1327634)及[构建说明](https://github.com/ninja-build/ninja/blob/3441b633c2fe2c494e958780ba0f4227b1327634/README.md)。本次是从该源码本地构建，不是官方发行二进制的认证。
- [手册 Build dependencies](https://github.com/ninja-build/ninja/blob/3441b633c2fe2c494e958780ba0f4227b1327634/doc/manual.asciidoc#L1090-L1131)、[失效传播实现](https://github.com/ninja-build/ninja/blob/3441b633c2fe2c494e958780ba0f4227b1327634/src/graph.cc#L169-L215)以及[作者的相邻测试](https://github.com/ninja-build/ninja/blob/3441b633c2fe2c494e958780ba0f4227b1327634/src/build_test.cc#L1095-L1210)。作者测试仅阅读，未运行。
- Ninja自身源码采用[Apache 2.0](https://github.com/ninja-build/ninja/blob/3441b633c2fe2c494e958780ba0f4227b1327634/COPYING)，所含第三方组件另遵守各自许可：[emhash说明](https://github.com/ninja-build/ninja/blob/3441b633c2fe2c494e958780ba0f4227b1327634/src/third_party/emhash/README.ninja)和[rapidhash说明](https://github.com/ninja-build/ninja/blob/3441b633c2fe2c494e958780ba0f4227b1327634/src/third_party/rapidhash/README.ninja)分别指明MIT和BSD-2-Clause。此包只包含原创示例／检查器与整理后的观察，不重新分发这些第三方源码或编译产物。
