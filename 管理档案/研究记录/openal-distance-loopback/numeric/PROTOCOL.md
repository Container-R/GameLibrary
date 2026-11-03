# OpenAL loopback 距离衰减：五个静态配置的待审数值协议

2026-11-03。**准备实现已写，未导入/运行夹具、未加载音频库或执行数值实验。**OpenAL Soft 1.24.2 固定来源复审已完成；独立数值协议审查为有限条件性接受，本版补明确停止顺序。新版能力门已完成下述实际观察；本目录的实现、协议和独立预期仍须预审，再另行请求数值执行。既有 capability 文件及其清单保持不变。

## 已知能力观察与尚未跨过的门

实际读取 `capability/run-author-1/result.json`：唯一一次能力调用正常清理并结束，结果是 `SOURCE_VERSION_REVIEW_REQUIRED`，自报 `1.1 ALSOFT 1.24.2` / `OpenAL Soft`。loopback、HRTF、output limiter 扩展和格式查询得到支持；源、buffer、render 调用均为零。它在版本门停止，**未执行后续实际格式/HRTF/limiter getter**，不能把请求属性当成已核实际值。输入与清单后检通过。能力运行不是五配置数值运行，也不是五次尝试。

本草案以已完成的 VERSION-1.24.2-REVIEW.md 限定目标源码版本：b621b5fce739525418f36e0474a46f9e1cab5e64，九文件比较及有关路径范围以该记录为准，不扩张为整个库等价或安装二进制认证。本数值实现仍未获执行批准。仍使用同一driver全部AL/ALC入口、显式loopback而非真实播放设备。不得通过安装、改backend、枚举设备或运行原播放示例补足能力。


随后实际全文读回 `capability-1.24.2/run-author-1/result.json`（SHA256 d5a8217a18c3de05d64c373760d23debea26ebfbde38fbb12175230cecfc2528）：新能力门 SUPPORTED，20项错误检查成功，实际48000/mono/float、HRTF=false、limiter=false、HRTF状态0，清理成功，source/buffer/render仍全0。两次能力运行是两个不同冻结版本门，均不计为数值case。

已全文读取 NUMERIC-DEFAULTS-REVIEW.md（d3e1db9eae436b6f6b2bcba698cc9adddffa962b3f357613aa76b8aa618b2061）。本实现选择最小路径：依赖固定1.24.2新source默认Direct单位增益、AirAbsorptionFactor=0、空Send及Loopback不建立Playback默认slot；不调用EFX/EAX，不做direct/aux filter getter。这些是固定源码支持而不是实际getter观察。普通source/listener属性仍显式设置并回读。同率还须pitch1、零速度、新source正常起播与无seek；不承诺最终逐帧等于输入。

## 固定输入与五配置

每个case使用独立新loopback设备、新context、新buffer及新source。单一静止listener和source，固定48000Hz、mono、float输出。PCM源为48个有符号16位整数：前24个为+1024，后24个为−1024；采样率48000，格式 `AL_FORMAT_MONO16`，循环播放。这是原创技术测试波形，不是音乐、素材或听觉实验。每case从新source的初始样本位置开始，不能在播放途中改距离复用同一个source。

| 固定顺序/ID | 距离模型 | reference distance | max distance | source距离 | 规范纸面距离因子 |
|---|---|---:|---:|---:|---:|
| 1 / inverse-reference | AL_INVERSE_DISTANCE_CLAMPED | 1 | 10 | 1 | 1 |
| 2 / inverse-max | AL_INVERSE_DISTANCE_CLAMPED | 1 | 10 | 10 | 0.1 |
| 3 / inverse-beyond | AL_INVERSE_DISTANCE_CLAMPED | 1 | 10 | 20 | 0.1 |
| 4 / inverse-short-max | AL_INVERSE_DISTANCE_CLAMPED | 1 | 5 | 20 | 0.2 |
| 5 / linear-max | AL_LINEAR_DISTANCE_CLAMPED | 1 | 10 | 10 | 0 |

距离使用同一任意世界单位，不擅称API单位必为米。listener位置及速度均(0,0,0)，朝向forward(0,0,−1)、up(0,1,0)；source位置(0,0,−d)，速度及direction均(0,0,0)，非relative。source与listener gain均1，source pitch=1、rolloff=1、min_gain=0、max_gain=1、cone内外角均360、outer_gain=1、looping=true。不添加效果或滤波，不使用多声道源、source独立距离模型扩展、移动或修改中的参数。静止双方避免速度项变化，不将此扩张为Doppler测试。

本表只是OpenAL规范条件，不是FMOD/CRI或真实设备结果。

## 每case的设置、回读与调用边界

1. 总计只起一个数值child，最多五case；在加载前建立并验证专用HOME、TMPDIR/TMP/TEMP和全部已审XDG位置，采用白名单环境、ALSOFT_DRIVERS=null及已审显式追加配置。复用能力门已审隔离规则，但建立新的冻结输入与输出目录，绝不改旧能力夹具或复用其run目录。
2. 同一driver取得核心与扩展入口；扩展、loopback类型、48000/mono/float能力必须重新核。每case的设备须支持HRTF和output limiter，context显式请求HRTF=false、limiter=false。不调用普通open、捕获、枚举或SDL。
3. context设为当前后先读取有限安全技术版本/renderer；必须匹配来源复审后冻结的值，任何变化即停止，不换成另一个库。三输出属性实际回读为48000/mono/float，HRTF与limiter实际getter均false；另记录HRTF状态枚举，不要求只能generic disabled。系统配置完全隔离仍为false。
4. 上传固定PCM前后检查AL错误，buffer回读frequency=48000、bits=16、channels=1、size=96。source绑定该buffer并设置上述全部属性；各自getter实际核对，不仅记录设定值。查询实际global distance model、listener位置/速度/朝向/gain、source buffer绑定、source type为STATIC、source状态INITIAL。只有已通过这些检查才允许play。
5. play后检查AL错误、source状态PLAYING。严格调用三次 `alcRenderSamplesSOFT`：4800帧预热、4800帧分析窗1、4800帧分析窗2。每次render返回后先保存原始字节，再核ALC/AL错误、该段所有binary32样本有限及source仍PLAYING；任何失败保留已获得部分，不执行后续窗或case。每case两分析窗齐后，立即核该case两窗RMS稳定门、对应baseline比值门以及适用的linear近零门，全部通过并清理成功后才允许下case。case1的两窗baseline下界或稳定门失败时，不进入case2。没有静默多渲染、探测稳定时间或重复case。
6. 正常末尾stop并核STOPPED，detach buffer并核绑定0，再删除source和buffer、核错误，解除当前context、destroy context、close loopback。异常路径尽力按有效对象状态清理，首错保留且清理异常另列；任何清理失败阻止全局通过，也不进入下case。对象ID若记录仅是OpenAL技术ID，不是进程ID或地址。删除后不查询失效对象。

完整成功时恰好5次设备/context创建、5个source、5个buffer、5次play、15次render，共72000个mono浮点样本。每case14400帧=300ms，其中100ms预热和两个100ms窗；五case共1.5秒的合成时间，**不是实际墙钟执行时长或性能结果**。source/helper setter/getter实际清单见contract.py的ready_checks与driver.py，独立预审必须核两者对应，不能只因为文本清单吻合就认证ABI。

## 独立于实测的有限数值判据

所有数值是预先选定的工程门槛，不是规范对未知内部处理链给出的误差上界。首个不符即保留FAIL，不通过调整窗口或阈值追结果。停止检查在每次render/每case内即时发生；末尾独立消费者仍从全部已保留字节重新核算，不能用它代替执行时的首失败停止。

- 所有预热和分析样本都必须是有限binary32值。这里要求小端binary32原始输出平台；ABI/字节序不符则停止，不静默改格式。预热保留但不计入下面RMS。
- 每个4800样本分析窗的 RMS 为 `sqrt(fsum(float(x)*float(x))/4800)`，按binary32解码后用Python双精度与稳定求和复算；不是峰值、响度或玩家可听见的判断。对应比值也由这些值计算，不能只采信driver打印的统计。
- baseline为case1两个分别对应的分析窗。每窗RMS必须有限且 **≥0.001**。固定PCM按常见16位归一化的输入量级为0.03125；0.001是提前选定、远离零分母的保守信号门槛，不声称mono混合输出必须等于输入幅度。若实际配置低于此门槛，实验失败而非降低下界。
- 每case两个分析窗RMS的绝对差必须 **≤1e−6**。这只检查两个固定窗，不证明全部未来输出稳定。
- 对每个case、每个窗，除以case1同编号窗RMS；与表中1、0.1、0.1、0.2、0的绝对差必须 **≤0.001**。case1对自身比值为1只是baseline定义，不是额外独立验证。
- case5两个窗还分别要求 RMS **≤1e−6**。相对近零和绝对近零都需满足，不能因为baseline大而接受明显非零输出。
- 不另规定每一帧恰好等于输入PCM乘纸面距离因子。mono混合、渐变和其它处理使该等式不能直接假定；本实验仅观察固定窗的有限关系。不得仅选相位或丢弃失败样本。

## 原始数据与独立复算建议格式

本实现使用UTF-8 JSONL，每条恰有seq、event、case、data，seq从0递增。每个render返回立即输出并flush该段小端float32字节base64、frame_count=4800、byte_count=19200、SHA256。case完整时三段有序合计57600字节；五case共288000字节/72000 floats。不是五份统计值代替原始波形。

固定使用三个window事件，part依次warmup/window1/window2，不是单case三个字段。成功顺序为begin、global_ready，每case依次case_begin、ready、playing、三组window/window_checked、case_metrics、cleanup、case_pass，最后success。失败保留api_failure（若有API错误）、case_failure/failure和清理事件，不伪装成成功顺序。输入PCM定义在contract.py与driver.py，global_ready记录实际96字节SHA256；消费者从字面定义独立重建其预期身份。当前只写代码，不运行生成波形或样本文件。

严格消费者须校验JSON类型、重复键、seq/顺序、case参数、样本长度、base64合法性、摘要与实际解码字节；原始数据可以携带NaN/Inf位模式，但解码后必须拒绝，不能把JSON禁NaN误当已检查波形。复算使用全部两窗，独立预期不从作者输出拟合。失败部分保留真实已返回字段，未运行项不填合成零或假成功。技术合成波形不含环境身份；stdout/stderr中未受控的库信息仍须私下审查，不能直接公开整运行目录。

## 有限运行和解释边界

本实现沿用唯一child15秒通信+最多2秒清理观察，保留首因、清理异常、真实退出确认、冻结源码/清单前后字节。本实现必须重新审核这些路径，不以复用名称继承旧故障测试。没有自动第二次尝试；独立复现如需运行须另行明确授权。

ALSOFT_CONF仅追加配置，不能排除系统/可执行目录全部设置。即使HRTF/limiter回读关闭，也没有证明dither、重采样等所有处理均关闭。已知系统dither可能使近零或稳定门槛失败；失败保留，不能改backend、扩大容差、延长预热或切换素材继续追通过。

若最终全部通过，结论也仅为该实际环境、该driver自报版本、这些已回读条件下的五个静态离线输出关系。不是配置独立性、二进制源码认证、真实设备/可听感、资源释放策略或所有OpenAL实现的保证。若来源门无法允许本有限解释，停在source-only即可。

## 原源与阅读边界

- OpenAL1.1规范§3.3–3.5.1：距离模型及增益处理顺序，沿此前实际读取范围，不声称全文规范审查。https://www.openal.org/documentation/openal-1.1-specification.pdf
- ALC_SOFT_loopback原文全文：同driver、指定格式、sample frames、显式渲染。https://openal-soft.org/openal-extensions/SOFT_loopback.txt
- HRTF/limiter扩展的请求与实际状态段，及上级CONFIG-AND-CAPABILITY的固定1.24.3来源记录；后续 VERSION-1.24.2-REVIEW.md 已完成固定1.24.2九文件有限比较（报告SHA256 72f60cf45e47493fb64430a5d7ece698608e8463a94c051e11af526a3777ea35）。不把1.24.3阅读自动迁移成1.24.2全库证明。默认滤波/吸收补读已完成，采用本协议开头的有限默认依赖；不把它写成实际filter getter保证。

## 实现与待审身份

INPUT-SHA256.json绑定本协议、driver.py、contract.py、consumer.py、runner.py、isolation.py、alsoft.conf七文件。runner启动保存清单原字节/摘要并核七输入，结束再次核清单字节及七输入；公共result仅有源输入清单摘要、数值摘要和安全技术状态。原stdout.bin/stderr.bin与异常文本保留private目录，不能原样公开整个run目录。缺少正式result不算通过。

runner由已审 capability-1.24.2/runner.py派生，保持15+2秒、唯一child、新run名、完整白名单和预建可写目录、首因/清理分离。差分见RUNNER-DERIVATION.diff；旧能力目录不改。consumer.py纯Python解析完整JSONL与全部原样本，不加载音频库；driver在每case立即调用同一作者数值门停止，另有独立者不导入这些模块的复算器，不能以作者消费者冒称独立验证。

命令形态仅供将来批准后使用：`python3 -I -B runner.py fresh-name`。当前没有实际数值执行，不授权自动尝试。

## 静态预审后的失败证据修订

初候选清单404533a650269cd65e69c216498dc8c463bab2479c7194a303ac0bb4f5d28a40未运行，保存在history/pre-partial-evidence。只补失败证据：case_failure带partial_actual，包含已取得的安全格式/source/listener/buffer字段，不补未执行字段；buffer绑定、play后的状态、每窗状态及清理STOPPED/解除绑定等已经取得但未进入ready的值记failure_values。清理失败时cleanup也保留对应实值。普通成功事件结构与消费者不变。

浮点getter若返回NaN/Inf，失败证据使用明确nonfinite_float标签（nan/positive_infinity/negative_infinity），不伪造0，也不让allow_nan=False阻断保留失败与清理。未知版本/renderer原字符串仍不进入公开字段。该修订来自静态发现，不声称已运行注入测试或观测实际API失败。
