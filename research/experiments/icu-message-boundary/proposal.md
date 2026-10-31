# ICU MessageFormat与伪本地化：有限C API实验闸门

2026-10-31。当前只核对原始接口、动态符号并调用固定签名版本函数；尚未解析或格式化测试pattern。无安装、依赖下载、引擎执行或Unity SmartFormat等价主张。

## 可用能力与身份

Linux x86_64，Python3.12.14；`u_getVersion_76(uint8_t[4])`实际返回`[76,1,0,0]`。nm已见umsg_open_76/umsg_format_76/umsg_close_76和u_errorName_76/u_getVersion_76。

| 真实文件 | SHA-256 |
|---|---|
| /usr/lib/x86_64-linux-gnu/libicuuc.so.76.1 | a8e433e81075732faf255b17d4a25ce28632e41fef1a75e727ee7f4ed73ab151 |
| /usr/lib/x86_64-linux-gnu/libicui18n.so.76.1 | 596132c352dc25d1e8a1f91e2c5790262ed02376d27afc14b545a1952341b3fc |
| /usr/lib/x86_64-linux-gnu/libicudata.so.76.1 | a04b2b906193fa1e40f968a3d16d7d6c844a1fafbdd5bce6e9f67b01c124ff24 |

版本函数不证明二进制与远程标签源码逐字对应；保留路径、内容hash及实际输出即可支持本机范围。Node内置ICU78.3不是本实验库，且不以Intl替代MessageFormat。

## 版本化原始来源

官方在线released API文档目前标题为ICU4C79，不能拿它冒充76。以下通过GitHub插件读取Unicode官方release-76-1文件；只阅读，未下载头文件编译：

- [umsg.h](https://github.com/unicode-org/icu/blob/release-76-1/icu4c/source/i18n/unicode/umsg.h)，umsg_open/close约389–416行、format约506–527行：明确接口与数字参数约定。
- [umsg.cpp](https://github.com/unicode-org/icu/blob/release-76-1/icu4c/source/i18n/umsg.cpp)，umsg_vformat约389行起：按参数类型从varargs取值，kDouble分支取double。
- [msgfmt.cpp](https://github.com/unicode-org/icu/blob/release-76-1/icu4c/source/i18n/msgfmt.cpp)，1662–1665行：plural/selectordinal/choice映射kDouble。此定位用于证明当前仅plural参数的类型，不推广混合格式。
- [parseerr.h](https://github.com/unicode-org/icu/blob/release-76-1/icu4c/source/common/unicode/parseerr.h)：两个int32_t的line/offset，两个长度16的UChar上下文字段；并非所有解析器都会填写每个字段。
- [uversion.h](https://github.com/unicode-org/icu/blob/release-76-1/icu4c/source/common/unicode/uversion.h)：u_getVersion使用4个uint8_t。
- [utypes.h](https://github.com/unicode-org/icu/blob/release-76-1/icu4c/source/common/unicode/utypes.h)：UErrorCode及u_errorName；成功包含非正值，负数警告不能一律当解析失败。
- [umachine.h](https://github.com/unicode-org/icu/blob/release-76-1/icu4c/source/common/unicode/umachine.h)：UChar的UTF-16类型定义；本机不应用32位wchar_t数组冒充。
- [Python3.12 ctypes官方文档](https://docs.python.org/3.12/library/ctypes.html#calling-variadic-functions)：固定参数应声明argtypes，变参显式传其C类型。本实验仅覆盖本机ABI，不作跨平台包装承诺。

## 有限ABI方案

`UMessageFormat*`作为不解引用的opaque地址，用c_void_p接收/传递（不因typedef名称再次错误解引用）。

| 函数 | 固定签名与Python对应 |
|---|---|
| umsg_open | (UChar*,int32_t,char*,UParseError*,UErrorCode*)→opaque pointer；显式restype=c_void_p |
| umsg_format | (opaque,UChar*,int32_t,UErrorCode*,...)→int32_t；argtypes仅固定四项，额外一个c_double |
| umsg_close | (opaque)→void；finally关闭非空handle |
| u_getVersion | (uint8_t*)→void，分配4元素 |
| u_errorName | (UErrorCode)→const char*，用c_char_p读取 |

本机将UErrorCode按C enum对应c_int，检查sizeof(c_int)==4；int32_t用c_int32，UChar用c_uint16。parse结构字段为int32,int32,uint16[16],uint16[16]，检查大小72与字段偏移0/4/8/40。UTF-16编码按本机字节序，长度计code units而非Python字符数；输入保持存活，输出严格按返回长度解码，不用wchar_t或盲读NUL。

**只接受脚本内四个固定pattern白名单**，全部仅位置参数0、plural、无integer覆盖、无缺口、无字符串/日期/嵌套/命名参数。不要把本实验包装成任意文本的通用API；类型与数量不匹配可能使varargs读取错误内存。无效pattern只open，失败后不得format。有效pattern仅传有限数值1.0/2.0，各为c_double。

输出采用固定充足buffer（例如256个UTF-16 code units），检查返回长度非负且小于capacity，检查状态与实际errorName。若超界/溢出，不解析截断输出、不自动增加范围，报告后停止。状态每次重置0；警告保留原值与名字，不隐藏也不等同失败。失败pattern的parse字段仅按实际值归档，不臆造其精确含义。

## 四个预先声明的候选

locale固定en。以下均为原创微型文本，不取自真实游戏：

1. 基线：`{0, plural, one {One key} other {Many keys}}`。
2. 朴素整串变换：对基线所有ASCII元音进行一对一重音替换（包括plural/one/other等语法部分），原串/映射/结果全部归档。预期open失败，但错误具体code/offset待实测，不能先宣称必为某错误。
3. 人工仅改文字对照：`{0, plural, one {Óné kéy} other {Mány kéys}}`。不是自动解析器或语法保留算法；只是人为准备的控制文本。
4. 语义负例：`{0, plural, one {Many keys} other {One key}}`。预期可解析格式化，但违背本例对单数/复数文案的预设语义合同。无需真实译者或玩家数据来发现这项人为交换，却不能据此证明任何真实语言的译文质量。

基线与人工对照应在1/2两输入分别输出相应分支文字；负例应输出相反含义。解析成功、分支可达和语义正确是不同验收层。仅此en与整数样例不能覆盖CLDR所有语言/小数规则，更不代表排版、RTL、字体、Unity、真实伪本地化管线或LQA。

## 证据与停止条件

一份固定入口执行四pattern，或按case子进程隔离；父编排器保存原始stdout/stderr、解析JSON、版本和三库hash、源hash、确切pattern/locale/数值、每次open及format状态与返回长度/输出。无成功摘要残留，非零退出/异常即停止；独立复核通过前不把实测提升为成熟结论。任何签名/类型条件不满足即退回source-only，不安装开发包或替换库。

目前结论仅为此有限调用路径具备足够明确的接口依据；需父代理批准后才运行格式化。探测并未测试任一pattern。
