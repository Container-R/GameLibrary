# 透明网格顺序实验

本实验只回答三项可区分的问题：指定版本的 fetch 是否保留原顶点身份序列；cache 是否真实重排面；共用顶点域的多个 draw range 能否独立重排并覆盖同一顶点数组。另以真实离屏 OpenGL 光栅给出交换透明面顺序、fetch 保序的颜色对照。没有进行 GPU 性能测量、引擎集成验证或 overdraw 优化实验。

## 复现

在安装 g++、Python 3、libEGL.so.1、libGL.so.1 且 Mesa 支持 surfaceless EGL 的 Linux 环境运行 `bash run.sh`。不安装依赖，不需要 GPU；脚本将重写同目录结果。原生 C++ 结构测试可单独执行前两条命令：

```sh
g++ -std=c++11 -O2 -Wall -Wextra -Ivendor ordering.cpp vendor/vcacheoptimizer.cpp vendor/vfetchoptimizer.cpp vendor/allocator.cpp -o ordering
./ordering > structure.json
python3 raster.py > raster.json
```

`structure.json` 保存完整输入、输出和身份还原。`raster.json` 保存实际绘制状态及 glReadPixels 返回的像素。`checksums.sha256` 绑定代码版本。所有断言启用，失败使脚本非零退出。

## 固定上游与执行审查

meshoptimizer v0.25，提交 `6daea4695c48338363b08022d2fb15deaef6ac09`。

- [vfetchoptimizer.cpp](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/vfetchoptimizer.cpp)：按输入索引的线性次序，第一次访问顶点时复制其整个记录，然后原位改写相同索引位置。不选择或交换三角形。
- [vcacheoptimizer.cpp](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/vcacheoptimizer.cpp)：构建面邻接，按缓存/活跃面评分选择下一个面，将其三个索引按原面内次序写入下一个输出位置。
- [allocator.cpp](https://github.com/zeux/meshoptimizer/blob/6daea4695c48338363b08022d2fb15deaef6ac09/src/allocator.cpp) 与 header：标准 new/delete 临时内存分配及可替换分配器入口，本实验不调用替换入口。

编译前阅读了上述执行路径、头文件分配器和接口前置条件。这些路径操作传入缓冲区和临时内存，无文件、网络或进程副作用。vendor 保留 MIT 许可证；实验自身代码 CC0。

## 实验 A：原生 fetch 与 cache

输入是 4×4 顶点网格的 18 个唯一三角形，以 `(t*7)%18` 确定性打乱；再加一个未使用顶点。顶点记录存放原始身份 0…16，而不是仅比较输出的整数索引。`identity(output_indices, output_vertices)` 还原每个角点的原始身份。

观察：

- fetch 使用 16 个顶点，删除未引用顶点。顶点存储与索引数字发生变化，54 项身份序列与输入逐项相同，因而每个有序三元组及其序列均未改变。
- cache 输出的面原位置为 `[0,13,6,8,1,12,7,3,14,16,11,9,2,4,15,17,10,5]`。代码逐面查找完整有序三元组，并断言排序后的原面位置列表恰为 0…17，确认输入每面恰出现一次。此输入确实换序；这不声称任意输入都必定换序，也不测量局部性提升。

身份属性仅用于跟踪记录。实际渲染里显式使用数值 vertex ID、primitive ID、外部按 ID 索引的表等，仍需独立处理；本实验不证明此类 shader 在重映射后等价。

## 实验 B：共用顶点域的两个 range

原始 range A=`[4,1,3]`，B=`[1,4,2]`。负对照分别用原始顶点输入调用 fetch，但都输出到同一个共享顶点数组，保留各自重写后的索引。第二次调用覆盖数组后，A 还原成 `[1,4,2]`，已不是 A。此负对照展示一种具体错误实现，不是说独立拥有顶点缓冲的 range 不能各自优化。

正对照将两个 range 的索引按 draw 次序连接后只调用一次 fetch：统一顶点身份表为 `[4,1,3,2]`，索引为 `[0,1,2,1,0,3]`。原 range 边界仍在第 3 项，逐项还原为 `[4,1,3,1,4,2]`。即必须让同一个最终顶点域遵守一份一致映射；也可先统一生成 remap 后分别应用，并不要求物理上永久合并 draw。

## 实验 C：实际离屏光栅

Python 通过 ctypes 调用真实 libEGL/libGL，并未计算或模拟混色公式。绘制实际使用 `glDrawElements(GL_TRIANGLES, 6, GL_UNSIGNED_INT, client_indices)`，`glVertexPointer` 和 `glColorPointer` 指向 28 字节步长的位置 xyz / RGBA 交错 client arrays；不是 glBegin 展开索引。以软件 OpenGL 光栅执行，16×16 单样本。明确创建 GL_RGBA8 纹理附件 FBO，查询其颜色编码为 GL_LINEAR (9729)。不用默认 framebuffer 的不确定颜色格式。

两个覆盖采样点的全屏三角形有不同顶点身份，颜色常量为红 `(1,0,0,0.5)` 与青 `(0,1,1,0.5)`。清除为透明黑。禁用深度测试、深度写入、剔除、抖动、多重采样和 framebuffer sRGB；RGB 使用 SRC_ALPHA、ONE_MINUS_SRC_ALPHA，alpha 使用 ONE、ONE_MINUS_SRC_ALPHA，方程 FUNC_ADD。读取 `(8,8)` 的 RGBA8：

| 提交顺序 | 实际读回 RGBA8 |
| --- | --- |
| 红后青 | `[64,128,128,192]` |
| 青后红 | `[128,64,64,192]` |
| 原生 fetch 后的红后青 | `[64,128,128,192]` |

三次完整 16×16 FBO 均由 glReadPixels 保存为对应 `.rgba`（从底部开始的行序、每像素 RGBA8、共 1024 字节）及 `.png`（上下翻转为显示行序）。PNG 未附颜色配置，只用于查看字节预览，不能把 PNG 的显示色当线性数值证明；数值证据仍是实际 framebuffer 状态与原始读回数据。

第三行实际消费 `ordering.cpp` 生成的 fetch 索引和顶点身份映射，将完整位置、颜色记录按该映射取回。这不是把重排索引直接套在旧顶点数据上。图形输入不同于实验 A 的连通网格；交换两面是显式对照，不声称 cache 对此两面输入产生换序。结论只是在这些固定状态与输入下，面提交顺序变化改变了观测像素，纯 fetch 对照没有改变该像素。8 位量化数值不能当无限精度公式结果。

本次软件光栅结果不是物理 GPU 性能结论，也不能推出复杂场景的可见瑕疵范围、排序正确性或优化收益。

## 调试记录与范围限制

最初使用默认 EGL pbuffer 查询颜色编码时，线性编码断言失败；即使请求 EGL linear colorspace，也未满足该断言。因此最终测试改为显式 GL_RGBA8 FBO，并查询确认 GL_LINEAR 后才读回像素。最终在创建 EGL 前设置 MESA_SHADER_CACHE_DISABLE=true。以上保留实际测试配置和已解决的线性编码问题。

没有调用 overdraw 优化器，没有渲染排序交叉/自相交曲面，没有测量硬件缓存或帧耗时。文章若需要这些主张，必须另外提供来源或实验。
