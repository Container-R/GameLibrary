# 五静态配置：独立离线数值校验器

仅为本任务原始JSONL做离线复算，不加载OpenAL，不导入作者driver、runner、contract或consumer。尚未消费真实数值输出，也不是执行许可。

## 准备依据与独立范围

实际读取当前PROTOCOL-DRAFT、NUMERICAL-PROTOCOL-REVIEW，先自行写出固定五配置和数值核心，随后与实现作者通过消息约定schema，仅读其contract.py/consumer.py文本核字段与事件顺序，未导入执行。没有从实际结果拟合阈值或预期。

reference=rolloff=1，先clamp距离，再用inverse的 reference/(reference+(d-reference)) 或linear的1-(d-reference)/(maximum-reference)，推导五因子1/.1/.1/.2/0。基准下限.001、窗间差1e-6、比值绝对差.001、linear绝对上限1e-6均来自预先约定，不是规范误差上界。

逐段严格base64和摘要、19200字节、小端4800个binary32解码；预热也检查有限性但不参与统计。两个分析窗全部样本独立fsum平方求和再开方，对应除以case1同编号窗口。作者统计不参与预期生成，只在最后与独立复算精确比较。

JSONL要求无重复键、非有限JSON常量、缺失/错序事件或额外尾事件；seq从0，固定五case和三窗，布尔值不替代整数。核begin核心配置、关键实际距离/格式字段、自报版本、零错误检查条目、播放状态与成功/清理门。

**范围不等于完整执行审计：**本工具不认证完整getter检查名单、全部属性、实际调用是否发生、原始清理实现、输入冻结或环境隔离。ready等非数值区允许额外字段。完整API证据仍须实现预审与回执审查。某个带缺省证明字段的合成流能过本数值工具，不代表它能过作者的完整执行消费者。实际部分失败流会被拒绝为不完整数值证据，不删除或重写它。

## 实际纯合成自测

selftest.py：独立构造常量binary32数组，仅供校验分支。正常合成输入及13种数据拒绝分支、3种JSON拒绝分支通过，共17项。包括坏长度/base64、NaN/Inf、错case、错比值、缺窗/缺case、摘要错误、bool帧数、弱基准、窗不稳、linear非零。

stream_selftest.py：手工构造最小合成JSONL，检查完整流及缺窗、错case、清理失败、伪造统计、尾事件五个拒绝分支，共6项。合成ready使用明确synthetic-only检查名，故不声称模拟了完整API调用记录。

两次纯Python自测均在各自新建0700根下预先建立HOME、XDG_CACHE/CONFIG/DATA/STATE/RUNTIME和TMP/TEMP目录，白名单环境、禁字节缓存后执行；只产生本目录两份安全结果摘要，没有保存合成原始流。未创建音频设备、加载音频库、渲染、播放或记录声卡输出。没有安装软件或探测本机版本/配置。绝对私有目录不写入报告。

运行方式（须在批准的隔离外层下使用）：`python3 -B check_numeric.py 原始输出.jsonl`。返回PASS仅表示上述离线证据满足有限数值门；失败返回固定类别，不将输入路径或异常原文打印为公开记录。

schema仍来自实现草案，最终冻结发生字段变动时须精确复核适配，不静默兼容猜测。

## 最终schema适配历史

最终作者输入清单为f6675bf6958660964b74a5d6f677379e417243ad781657cd06e9984120a41271，contract为23ff73b231818c2d58a279ffd8bc6e8ca4e6319b84f3efe312d62c8a44427c0b，consumer为72ecf479dcaa39de35e8c9288566d896ab974ed83fe2896303c9b2c9e05cda84。只读发现close_loopback返回布尔ok而非ALC error，本工具旧版会错误拒绝；旧checker、fixture及17+6结果和清单已原样保存在pre-adaptation。

经主编明确授权，最小修订仅独立checker的cleanup检查和合成stream fixture：前8项按原零错误，最后一项要求close_loopback/ok=true。阈值、五因子、原始解码和RMS未改。新独占0700/白名单HOME/XDG/TMP外层中实际重跑6项stream合成检查通过，记录STREAM-SELFTEST-FINAL；原17项没有重跑，不称覆盖新版全部代码。该次仍未加载OpenAL。新清单INPUT-SHA256绑定将用于消费的独立代码，实际原始流消费另记，不把合成PASS当音频观察。
