# ICU locale 分支覆盖：来源与运行证据分层

访问于 2026-10-31；目标是补充现有伪本地化文章，不建立新的语言支持认证。

## 固定原始来源

比较源码固定为 ICU release-76-1 commit `8eca245c7484ac6cc179e3e5f7c1ea7680810f39`：

- [cardinal plural 数据](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/data/misc/plurals.txt)：`locales` 中 en→set3、ar→set37，不能误用后面的 ordinal 映射。六个有限整数对应的类别在执行前由这些规则推导，不从观察结果反写期望。
- [MessageFormat 的 plural 路径](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/i18n/msgfmt.cpp#L1134-L1148)与[PluralFormat 的回退约定](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/i18n/unicode/plurfmt.h#L106-L118)：缺选中 keyword 的正文时使用 other。只删除 few 而保留 other，不应被描述成故意制造语法错误。
- [默认格式化与 DecimalQuantity](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/i18n/msgfmt.cpp#L1952-L1996)、[英文 decimal pattern](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/data/locales/en.txt#L11-L23)：默认标准小数格式的可选小数位，不是 Python/C double 自带的词法尾零信息。无数字子格式的 ASCII 标记不要求实际输出阿拉伯数字或文本。
- [C API](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/i18n/unicode/umsg.h#L506-L526)：仅复用固定单个 positional double 的变参边界，显式 UChar、int32、pointer 与返回类型，不接受任意模式或参数列表。
- [该源码树 supplemental data](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/data/misc/supplementalData.txt#L2179)声明 CLDR 46。这说明比较源码的数据关系，不能仅据本机文件名、版本函数或三个文件摘要认证实际完整资源/依赖来源。

完整阅读定位及源预测表保留在夹具 source-gate.md。不存在通过图片、二手摘要或动态运行结果猜写规则的步骤。

## 观察范围与检查器范围

冻结输入是0、1、2、3、11、100；三个配置为 en 完整模式、ar 完整模式、ar 仅删 few。每个成功配置最多一次版本查询、一次打开、六次格式化、一次关闭，即九个 ICU 导出函数调用；CDLL 加载事件单列。没有调用 u_errorName，也不把运行环境所有底层系统调用纳入这个功能计数。

本地已检查 uc/i18n/data 三个库的字节身份不是所有动态依赖的认证。最小环境和五个新建可写目录只是缩小可描述范围，不是沙箱。旧四例 ICU 夹具保持原始文件与既有范围，新的 locale 证据不能回写成旧实验当时已测。

新检查器的初始草稿在原生执行前发现 bool/int 混淆、事件流全局顺序及异常后的进程计数表述问题；原稿与纯 Python 反例保留，修正没有改变预先冻结的 marker 表。它们是执行前审查历史，不是 ICU 功能失败。静态哈希/字段一致性不认证运行真实性，也不批准翻译质量。

## 实际观察回执

作者 batch `2f4f411a-b9d7-485e-b837-8d5d1ed5cfe0`；独立 batch `51693796-d462-4068-8d93-cf96d488eb99`。各三个子进程、27 次 ICU 函数调用（18 次格式化），实际 attempt/returned 成对记录。输出与冻结三列 marker 表一致：ar 完整 pattern 输入3为 FEW，仅删除 few 后同输入为 OTHER；en 的0/1/2/3/11/100为 OTHER/ONE/OTHER/OTHER/OTHER/OTHER。

每个进程打开状态0，输入0的首次格式化警告-127，其余格式化状态0；不使用旧运行警告当新证据，也不推断警告原因。六个子进程退出0、stderr空、无超时；已检查源码与三库身份前后一致。单独优化启动拒绝 batch `9a6956ee-98c7-4c91-b1cb-08a3299a25b9` 退出1、原生子进程0；该检查额外源码摘要只在运行后观察，未声称前后采集或陈旧 PASS 注入。

[夹具说明](../experiments/icu-plural-locale/README.md)与[独立复验](../experiments/icu-plural-locale/review/NATIVE-REVIEW.md)保存实际命令、原始载荷和逐调用数量。总计六个子进程/54次ICU调用不代表新增六种 locale；只有三个有限配置。原文的真实翻译、字体、RTL、布局和游戏集成验收仍未执行。
