# OpenAL loopback 能力门：待独立审查的准备稿

2026-11-03。尚未执行，不是已批准或已通过的协议。本目录只准备能力检查；五个距离增益配置完全不在本次范围。已读取上级 CONFIG-AND-CAPABILITY.md 并合并有限配置要求；仍须独立代码预审及主编批准才允许唯一一次执行。

## 输入与身份

Linux Python ctypes，调用约定为 C ABI。ALCboolean 用单字节 c_byte，ALCenum/int/sizei 用四字节 c_int，设备与上下文为不透明 void 指针，函数入口为同一 CDLL 的 alcGetProcAddress 返回值。程序先核 C int/char 大小。仅加载一个固定 SONAME `libopenal.so.1`，不调用 find_library、不启动额外发现程序、不猜安装路径。动态加载器选择的实际对象尚未取得固定二进制身份；本能力门不能证明它等于源码审查基准 OpenAL Soft 1.24.2。若下一阶段需要本机二进制身份，应另存内部记录，不能添加到公共 JSON。

INPUT-SHA256.json 列 PROTOCOL.md、driver.py、runner.py、isolation.py、alsoft.conf 五输入的 SHA256；它是候选字节清单，不是已经审查接受。执行前和结束后都要一致。启动时保留清单原始字节并计算其 SHA256，公共回执仅记录该技术清单摘要；结束时同时要求清单原始字节不变和五输入摘要不变。外部审查另绑定启动清单摘要。

原源：上级 GATE.md；官方 ALC_SOFT_loopback 扩展原文（https://openal-soft.org/openal-extensions/SOFT_loopback.txt），本次实际全文阅读。固定头/实现身份沿上级来源门；未把本机库认作这些源码构建。

## 有限调用与判据

1. 同一 driver 的 alcIsExtensionPresent(NULL, ALC_SOFT_loopback)。false 保留为 UNSUPPORTED，不换 driver。
2. 三个 loopback 入口均必须非空；只调用打开和格式查询。渲染入口仅核存在，绝不调用或绑定可执行 render 包装。
3. 仅 alcLoopbackOpenDeviceSOFT(NULL)；不得调用 alcOpenDevice、设备枚举、捕获、SDL、source/buffer 创建或任何渲染。没有音频样本、听觉或真实输出设备观察。
4. 设备上依次检查 ALC_SOFT_HRTF 和 ALC_SOFT_output_limiter；缺任一项为 UNSUPPORTED。再核48000Hz/mono/float 格式；false 保留 UNSUPPORTED。context 属性明确三格式项、HRTF=false、limiter=false与0终止。context 成功、make-current 成功后先核技术自报；固定版本相符才查询三格式属性及 HRTF/limiter 实际值，要求完全等于48000/mono/float/false/false。另记录 HRTF_STATUS 整数，不强制只有 generic disabled。
5. 只读取 AL_VERSION 和 AL_RENDERER，不读取设备名称。公共版本仅接受 `1.1` 或 `1.1 ALSOFT 数字.数字.数字`，renderer 仅接受 `OpenAL Soft`。不识别的原字符串不进入公共 JSON，结果为 SOURCE_VERSION_REVIEW_REQUIRED；可解析版本若不精确等于 `1.1 ALSOFT 1.24.2`，同样正常清理后停在 SOURCE_VERSION_REVIEW_REQUIRED，不继续属性认证。这不是自动替代库或继续数值实验的许可。技术自报不是来源认证，不读取 AL_VENDOR。
6. 每个相关 AL/ALC 调用后核错误，保留固定阶段标签/错误码。首次异常不继续能力动作；仍尝试 detach、destroy-context、close-loopback，记录各项清理。成功 close 后不访问已失效设备指针。清理全部成功才允许 SUPPORTED/UNSUPPORTED/SOURCE_VERSION_REVIEW_REQUIRED；能力失败与清理失败不被后续成功覆盖。

SUPPORTED 必须通过严格 JSON、完整固定错误检查顺序、格式值和清理序列消费，不只看最后标签。UNSUPPORTED 是已检查的能力阻断，不是失败后绕过；库加载、入口、上下文或API错误为 FAIL；版本/renderer不符合当前固定源码门单独标为 SOURCE_VERSION_REVIEW_REQUIRED。子进程非零或任何 stderr 阻止接受。首个失败保留预定 failure_reason（Stop固定标签或 wrapper固定原因），清理失败不覆盖首因。公共固定字段 configuration_fully_excluded=false、source_calls=0、buffer_calls=0、render_calls=0。原 stdout/stderr 和异常文本仅内部保留，未审查前不得直接公开；公开 result 只含经类型/字符与字段检查的有限技术值。

## 目录、环境、时间和失败

待批准后的命令形态：`python3 -I -B runner.py fresh-name`。run 名限小写安全字符，目录必须全新，不复用。目录留存，不自动删除失败现场。

复用现有 isolation.py 五目录准备验证，另实际创建 XDG_CONFIG_DIRS、XDG_DATA_DIRS、XDG_STATE_HOME、XDG_RUNTIME_DIR；TMP/TEMP 显式别名本次 TMPDIR。五目录和四额外目录均启动前核精确映射、目录存在且非符号链接，并执行有限创建/删除写探针；上级路径拒绝符号链接，根是绝对路径。白名单环境仅上述键、LANG/LC_ALL=C、ALSOFT_DRIVERS=null、ALSOFT_CONF；不继承宿主 HOME/XDG/LD_PRELOAD 或其他 ALSOFT 值。配置文件内容精确复制输入并核摘要。

ALSOFT_CONF 是追加的显式配置，不是禁用系统配置。系统与可执行目录配置读取仍可能发生；本准备稿不声称全配置隔离或零硬件系统调用。ALSOFT_DRIVERS=null 用来限制普通 backend 选择，不把它当作对实际未知版本的完备保证。CONFIG-AND-CAPABILITY 的源码读取结论已合并；其10秒是早期候选预算，本实现选15秒通信加最多2秒回收，以本协议为准。其 vendor 原字符串和可选 ALC major/minor 不采集，不增加本能力目标之外的查询。该记录提案不设置 ALSOFT_CONF，本实现保留显式最后追加的 drivers=null 文件，并明确它不能屏蔽系统配置。

唯一子进程以 -I -B、无 stdin、独立 session、固定 cwd 和白名单 env 启动；正常通信最多15秒。超时先固定首因 child_timeout，再独立尝试 kill 和最多2秒 communicate；kill 抛异常不覆盖首因，也不跳过有界回收观察，cleanup_failure 单列异常标签。没有盲重试。其它通信异常也只收尾该唯一 child，最多再2秒回收。不能确认退出则 termination_confirmed=false 并 FAIL，保留全部目录。不宣称整个进程组已验证。driver 不创建后代。没有重试、安装、真实设备 fallback 或第二轮探索。

所有输入后检和子进程退出/清理检查通过才写最终 SUPPORTED/UNSUPPORTED/SOURCE_VERSION_REVIEW_REQUIRED；先写 result.pending 再 replace。准备或存储故障可使正式回执缺失，缺失绝不当通过。公共结果不写绝对路径、PID、主机身份、已安装二进制摘要。受控配置文件和源输入摘要不是安装指纹。

## 当前待审点

- 对未知本机版本，系统/可执行目录配置与 backend 初始化的限制是否足以批准这一次 loopback 能力检查，已有配置来源记录，但仍须独立代码审查与执行批准。
- SONAME 加载对象尚未运行确认；自报格式刻意保守，不识别就停。
- 本次只准备代码，没有 import、编译、运行 driver/runner 或测试 OpenAL。即使能力通过，也不能预先证明后续数值实验、渲染输出或真实设备行为。

## 本次补读范围

官方 SOFT_output_limiter.txt 全文68行，核0x199A及false请求/状态getter；SOFT_HRTF.txt 的请求提示、枚举、HRTF mixing与状态查询相关段（不是所有末尾错误分支），核0x1992/0x1993及请求不等于实际状态。未运行库或读取本机配置。原配置记录保留，不覆盖其历史提案；差异见原 capability/CONFIG-MERGE-NOTES.md；该记录保留为历史，不是本次新输入。

## 1.24.2 再冻结的来源依据与旧结果保留

本目录是新的无渲染能力候选；不是覆盖旧版本门。实际全文读取上级 VERSION-1.24.2-REVIEW.md 与既有 capability/run-author-1/result.json。旧运行清单为 1e782e8eaf49dbd1867261357545ca68daed4fe7c2abd31e11bc32c4d8fab996，旧结果 SHA256 cc821923acdf3223f29e0ff013709ad6c92ae8a490d428e7e1c7779c67452f3c，自报1.1 ALSOFT 1.24.2并正常结束 SOURCE_VERSION_REVIEW_REQUIRED。它没有执行实际格式、HRTF与limiter getter，三类source/buffer/render调用仍为零。旧状态不回填、不称通过。

来源审者已将官方1.24.2提交 b621b5fce739525418f36e0474a46f9e1cab5e64 与既有1.24.3固定源比较九文件。alconfig.cpp、loopback.cpp、null.cpp、alext.h、mixer_c.cpp五文件完整同字节；alc.cpp、panning.cpp、alu.cpp、voice.cpp四文件存在真实差异，审者读完整差分及相关上下文。配置读取/backend限制、loopback ABI、显式false属性与实际getter、mono分支的有关控制流得到有限闭合；EAX/默认设备名称、UHJ近场、48tap、交错拷贝及ADPCM等差异不能抹为全库相同。具体Git blob身份与逐项范围以该版本复审记录为准。本准备作者读取的是该独立报告，不将审者九文件原源范围冒称自己的重新逐文件阅读。

据此，driver和runner只将精确期望自报由1.24.3变为1.24.2，其余行为不变；helper与配置文件完全相同。来源基线变化不等于安装二进制认证。若此次技术自报仍不匹配，照旧停门，不试第三个版本。

ALSOFT_CONF仍为追加配置，configuration_fully_excluded仍为false；HRTF/limiter关闭不证明dither或全部处理链清洁。系统与可执行目录配置没有实际读取审计。本次只准备重新冻结，不运行；15秒+最多2秒预算、唯一loopback/context、无source/buffer/render限制不变。数值PROTOCOL-DRAFT.md仍是另一份未实施草案，不能随本能力门获准执行。
