# Detour 首次构建诊断：独立只读审查

2026-11-01。结论：**可将这一份精确、已审的上游诊断纳入新的有限构建门槛，再经代码审查和主编单独授权决定下一次尝试。** 不自动重试、不修改上游、不更换或压制编译旗标。首次失败仍为失败，本报告不是原生结果或 C++ 可移植性证明。

## 实际证据

只读 `execution/attempt-001/receipt.json`、`build.stderr`，并重新阅读固定 `DetourNavMesh.h` 281–316 的完整 dtMeshTile 定义，以及 `DetourNavMesh.cpp` 180–285 的构造、析构和初始化流程。没有编译、调用 fixture 或执行任何环境探针。

- receipt 只有一项进程记录：build，尝试已开始、returncode=0；整体 status=fail、stage=build。没有 native 阶段调用记录，因此是 **1 次构建、0 次 fixture 启动、0 次确认的 findPath 查询**，不是两项路径用例失败。
- stderr 只有一条 warning，另有上下文与声明位置 note；并不是把 note 另计成第二条警告。具体是 `DetourNavMesh.cpp:243` 对 dtMeshTile 数组清零触发 `-Wclass-memaccess`，说明该类型没有 trivial copy-assignment。没有 fixture 警告。
- 实际重算 stderr SHA256 为 `d887b09f1c4f304b009fbfbcf61834c5d71dd80a44d8cc1cdb7f9978952f0bd5`，与 receipt 绑定一致。此摘要标识该精确诊断文本，不是编译器二进制身份。
- receipt 的 source_before、source_after、copied_after 三组均为 23 项且逐项相同。此处是实际比较保留 receipt 中的身份记录，没有声称重新执行整个构建。

## 这条警告与固定输入的关系

不能按“不相关未调用单元”排除：fixture 的单 tile `init(data,size,DT_TILE_FREE_DATA)` 会调用 `init(params)`；其两项分配成功后，正常路径就执行该 memset。maxTiles=1 只缩小作用范围，不消除诊断。

固定头文件里的 dtMeshTile 由整数和指针字段组成，没有类类型资源成员、虚函数或用户定义析构；它在 private 区声明了复制构造与复制赋值。源码采用分配一块 tile 存储、清零、再设置 salt/free-list 的初始化方式；随后 addTile 填充 tile 数据指针和属性。警告针对类的复制赋值性质与字节级写入，不是在说本次传入三 quad 数组长度有误，也不是编译器报告已发生一次路径越界。

这支持把它视为**固定上游实现中已识别且实际可达的构建诊断**，而不是无条件忽略所有 class-memaccess。另一方面，“成员只是指针/整数”不能证明任意 C++ 实现上清零对象均正确；本审查不证明全零指针表示、所有对象生命周期规则、任意 allocator/ABI、任何版本或优化配置的可移植安全，也不把未运行的 setup 断言当作已经通过。

允许继续的理由仅是：用未改固定实现、原编译参数与有限合法输入进行一次受控经验观察，保留这条已知诊断，而非先把上游改成另一种实现再声称验证原版。若组织要求“所有被测源码均无此类标准/移植性疑问”，该目标仍未满足，应保持停止；本单元原目标是该固定实现的输出容量行为，不是标准符合性认证。

## 新门槛必须怎样限定

1. 旧 attempt-001、旧清单、原 runner/protocol 和失败状态原样保留，不将旧 receipt 改成通过。
2. 单独保存经审的诊断原字节和说明，写入新候选身份清单及复制前后核验；核验受信任诊断文件本身的固定 SHA。不得仅信任一个可以随意编辑的 allowlist 文本。
3. 构建仍必须 returncode=0、stdout 为空；stderr 只可为空，或与上述整份已审诊断逐字节一致。任意新增 warning、fixture 诊断、一字变化或非零退出均停止，不能只按 warning 类别、文件名或子串放行。
4. 不改 fixture、两行 oracle、上游 16 文件、七编译单元列表及旗标。新协议只说明这一例外；不能泛化为以后警告均接受。
5. 使用全新 attempt 目录。先审新 runner/诊断消费函数/绑定与纯合成拒绝用例，包括受信任文件被改、原 stderr 被改/追加、非零 build、缺文件、旧目录不覆盖；随后主编才可另行批准一次尝试。
6. 若下一次进入 native，仍须通过真实 setup、两行输出、整体 receipt 及身份后检。当前零查询不会因更改构建门槛变成任何原生成功。

初始化失败的 flush 与立即进程退出约束保持不变；本轮未注入 OOM，也没有新增生产环境修复建议。

## 官方诊断说明交叉核查

另独立打开并实际读 [GCC 14.2《C++ Dialect Options》-Wclass-memaccess](https://gcc.gnu.org/onlinedocs/gcc-14.2.0/gcc/C_002b_002b-Dialect-Options.html#index-Wclass-memaccess) 段（网页行 572–578）：该警告覆盖原始内存写可能绕过非平凡/已删除构造或复制赋值、破坏封装等情况；其 std::string 反例不是 dtMeshTile 的同义证明，也不能反向推出本例完全安全。文档提及的 cast 抑制方式不用于本实验。此阅读只帮助解释诊断，不认证本机构建器版本或升级经验观察的适用范围。
