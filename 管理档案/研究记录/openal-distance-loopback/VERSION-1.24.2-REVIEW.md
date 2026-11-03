# 1.24.2来源复审摘要

公开安全衍生摘要，非原报告字节。原报告SHA为72f60cf45e47493fb64430a5d7ece698608e8463a94c051e11af526a3777ea35；此摘要有自己的文件身份，不能替代原报告字节验算。

官方[1.24.2 release](https://github.com/kcat/openal-soft/releases/tag/1.24.2)对应提交 [b621b5fce739525418f36e0474a46f9e1cab5e64](https://github.com/kcat/openal-soft/commit/b621b5fce739525418f36e0474a46f9e1cab5e64)。实际读提交身份及九文件，与此前1.24.3固定提交dc7d7054a5b4f3bec1dc23a42fd616a0847af948比较。

alconfig.cpp、backends/loopback.cpp、backends/null.cpp、alext.h、mixer_c.cpp五文件完整同字节。alc.cpp、panning.cpp、alu.cpp、voice.cpp存在差异，已读完整差分及相关上下文，不能说全库相同。变化包括EAX诊断与默认设备名称、UHJ近场、48tap重采样选择、交错输出/PCM拷贝及ADPCM代码。本能力门不使用这些其它场景。

逐项重读1.24.2配置链、backend限制、loopback创建/格式检查、完整属性处理、mono返回与实际HRTF/limiter getter，支持重新冻结无渲染能力门。配置与float显式dither边界并未因版本更换消失。距离因子和标量平滑相关分支也核对，但没有因此取得渲染观察或安装二进制认证。

旧[停止结果](capability/run-author-1/result.json)保持原样；新[能力结果](capability-1.24.2/run-author-1/result.json)由独立冻结输入产生，不把旧状态回填为通过。源码比较副本与上游全库不随本包发布，固定来源可按上述commit访问。

返回[能力包说明](README.md)。
