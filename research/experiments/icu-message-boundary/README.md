# ICU MessageFormat：能解析不等于翻译正确，伪本地化不能盲改语法

## 实际执行范围

2026-10-31，本机Linux x86_64 / Python3.12.14 / ICU版本函数返回76.1.0.0。四个隔离子进程只运行脚本内白名单pattern，locale=en，数值为1.0/2.0，C API可变参数明确为一个double。没有任意文本包装器、通用解析器、自动保留语法的伪本地化算法或Unity集成。

```
python run.py
```

不需安装。入口调用本机`/lib/x86_64-linux-gnu/libicuuc.so.76`和`libicui18n.so.76`，记录解析后的真实路径及icuuc/icui18n/icudata三个文件SHA-256。`source-pin.json`保存官方release-76-1标签解析到`8eca245c7484ac6cc179e3e5f7c1ea7680810f39`的来源元数据；版本号吻合不证明本地发行包就是该commit的认证构建。

## 原创输入与实测结果

| case | pattern | open状态 | n=1输出 | n=2输出 |
|---|---|---|---|---|
| baseline | `{0, plural, one {One key} other {Many keys}}` | 0 U_ZERO_ERROR | One key | Many keys |
| naive | `{0, plúrál, óné {Óné kéy} óthér {Mány kéys}}` | 65799 U_PATTERN_SYNTAX_ERROR | 未调用format | 未调用format |
| literal_only | `{0, plural, one {Óné kéy} other {Mány kéys}}` | 0 U_ZERO_ERROR | Óné kéy | Mány kéys |
| swapped | `{0, plural, one {Many keys} other {One key}}` | 0 U_ZERO_ERROR | Many keys | One key |

naive由ASCII元音逐个替换得到，故破坏了plural等语法文本。literal_only是**人工构造控制文本**，不是算法自动区分了语法和正文。swapped也是故意构造的语义错误：ICU正确执行了提供的分支，但这些文案违背本例“1对应One key、2对应Many keys”的预设合同。解析器没有负责证明翻译含义正确。

### 两个不能省略的真实诊断

1. naive的open失败却返回非空handle。实际parse_line=0、parse_offset=1、pre_context=`{`、post_context=`0, plúrál, óné `。代码依据status>0拒绝格式化，finally关闭非空handle；**非空地址不能代替成功状态**。这些字段是解析器报告的上下文，不宣称offset精确指向被改坏的某个字母。
2. 三个合法case的第一次format（n=1）都返回`-127 U_USING_DEFAULT_WARNING`，输出正确；第二次（n=2）为0。ICU成功判据允许负警告，但警告不等于不存在。原始状态全部保留，本实验未确定默认回退涉及哪个资源或建立跨locale警告规律；不把输出相同当作所有资源解析路径都已验证。

## 这能补上什么证据

- 原始字符串中语法与可见文字共享同一载体；逐字处理整个载体可能令实际ICU parser拒绝。
- 人为保持语法的文本对照可解析并走one/other分支；这是有限正控制，不是通用transformer正确性证明。
- 语法成功与输出存在仍不足以验证译文语义。这里用明确的错误分支文案证明这一逻辑边界，不假装开展过真实翻译审校。

对项目的建议是把**格式语法验证、参数绑定/分支样例、语义审校、界面呈现检查**分开记录。这个分层为原创工程建议；本次只执行前两者中的四个微型case，并有一个预设语义负例。没有字体、RTL、文本扩展布局、读屏、真实玩家或真实LQA证据。只测en和1/2，不能代表其他语言、分数、offset、嵌套或所有plural类别。

## ABI与失败边界

准确原始来源及签名调查在`proposal.md`。运行时使用UTF-16 uint16数组，不使用Linux wchar_t；输入长度按code units。返回handle以opaque c_void_p处理。UParseError大小与offset在本机检查，status用4字节C int。umsg_format固定四参数声明argtypes，可变部分只允许一个c_double；不存在参数索引缺口、命名参数或动态类型选择。

输出容量256个UTF-16 units，检查状态、返回长度及未截断条件后才解码；不对截断输出判成功。每次调用status重置0，保留实际警告。open错误不走format，所有非空handle均关闭。子进程异常/超时与正常进程返回的解析错误是不同证据；naive是预期解析错误，不是程序崩溃。

`run.py`拒绝-O；先移除旧summary，每case保存stdout/stderr/命令与退出码，再校验单一RESULT_JSON和精确输出。出错不留下新的PASS summary。当前正常四case结果见`results/summary.json`和各case.json；这些记录不以网页示例替代库执行。

## 版本化来源

- [ICU76.1 umsg.h](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/i18n/unicode/umsg.h)：open/close/format签名与数值参数。
- [ICU76.1 umsg.cpp](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/i18n/umsg.cpp)：umsg_vformat按类型读取varargs；[msgfmt.cpp](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/i18n/msgfmt.cpp)plural映射kDouble。
- [ICU76.1 utypes.h](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/common/unicode/utypes.h)：成功/失败和警告判据。
- [Python ctypes：Calling variadic functions](https://docs.python.org/3.12/library/ctypes.html#calling-variadic-functions)：固定参数声明与变参类型。

访问2026-10-31；公开released ICU文档页面当时已为79，所以本夹具使用76.1标签接口调查，不将79网页当成76源码。代码是原创有限实验，未复制上游实现片段或安装头文件。

## Runner证据完整性加固

原runner在-O拒绝时保留旧summary；有限负例实际发现此问题，原源码/四case结果保存在historical-runner-v1/。新版先删除旧summary再拒绝-O，并在超时分支保留部分stdout/stderr及命令/timeout元数据。四个真实ICUcase已以新版runner重新通过；并非复用旧hash的结果。独立的六个runner拒绝路径属于流程证据，不是ICU功能测试。

## 集成审查补充

固定公开源码 `umsg.cpp` 的 226–261 行显示：构造 MessageFormat 后，函数可以返回非空对象，即使构造过程已经设置解析错误。这与本机观察相符；头文件的简短返回说明不能取代错误状态检查。426 行的 kDouble 路径使用 double 可变参数。此处是源代码比较，不是对本机二进制来源的认证。

库文件摘要记录的是检查过的三个路径。脚本显式加载 icuuc 与 icui18n；没有证明所有实际依赖映射或数据解析来源均被封闭，也未认证 icudata 依赖闭包。集成者在 2026-10-31 15:43 UTC 检查当前环境，ICU_DATA、LD_PRELOAD、LD_LIBRARY_PATH 均未设置；这不是历史各子进程的环境快照，不能据此解释 -127 警告原因。

独立复跑见 [审查记录](review/README.md)，四个新子进程另存原始日志。集成者再次运行保存日志的独立检查器，不宣称第三轮 ICU 执行。可从此目录执行 `python3 review/check_raw.py review/results` 复核保存输出；断言式独立检查器与主 runner 均拒绝 -O。

新版 runner 的拒绝与超时输出保全见 [六个负例](runner-negative/README.md)。历史 v1 来源与结果独立保留，不与当前来源摘要混比。

## 公开归档取舍

保留当前作者/独立复核的四例完整原始输出、当前六项 runner 负例的原始结果、旧 runner 源码/摘要及优化拒绝后残留旧 PASS 的原始证据。旧四例的重复运行输出、中间负例输出和由冻结 harness 可重新生成的每例代码副本未重复发布；原始草稿记录未被改写。historical-runner-v1 中的摘要是历史执行记录，不表示这里包含其全部逐例原始日志。
