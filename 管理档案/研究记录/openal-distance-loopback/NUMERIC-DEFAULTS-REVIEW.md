# 数值输入默认条件：公开来源摘要

此文为公开安全衍生摘要，不是原NUMERIC-DEFAULTS-REVIEW的相同字节。原报告SHA d3e1db9eae436b6f6b2bcba698cc9adddffa962b3f357613aa76b8aa618b2061；协议引用这个身份时指原审查记录，不是本摘要。这里没有新增音频执行证据。

固定OpenAL Soft1.24.2提交b621b5fce739525418f36e0474a46f9e1cab5e64。实际读取al/source.h:62–129与al/source.cpp:3731–3746：新source的Direct三增益为1，AirAbsorptionFactor为0，Send槽为空。有限fixture不调用EFX/EAX变更，这些是固定源码默认前提，不冒称filter getter实际观察。

不能仅凭没有主动绑定效果就推广所有设备无效果：source.cpp:172–185会补入context默认slot。但alc/context.cpp:159–177仅在DeviceType::Playback建立该默认slot，显式Loopback不建立；在新context且无效果调用的范围内，默认reverb不会由此注入。alc/alu.cpp:1516–1537将空slot的send buffer设空。

AL_DIRECT_FILTER与AL_AUXILIARY_SEND_FILTER查询在所读source.cpp:2493–2499不提供有效getter，不应编造回读。空气吸收可读，默认0令距离附加HF吸收不生效；本fixture选择新source默认依赖，不为证明这一点扩展效果矩阵。

普通MONO16的FmtShort转换为float(sample)/32768。同采样率并不足以保证直接copy：alc/alu.cpp:1732–1775还涉及pitch和速度Doppler；core/voice.cpp:950–959要求步长恰一且分数位置0。新source正常起播、无seek、pitch1及零速度是本有限条件。之后仍有声像、增益和平滑等处理，不能据此把最终每帧当原PCM乘纸面因子。float输出转换不排除更早的输出dither；系统配置未全排除。

原源：[source构造](https://github.com/kcat/openal-soft/blob/b621b5fce739525418f36e0474a46f9e1cab5e64/al/source.cpp#L3731-L3746)、[context默认slot](https://github.com/kcat/openal-soft/blob/b621b5fce739525418f36e0474a46f9e1cab5e64/alc/context.cpp#L159-L177)、[直接copy条件](https://github.com/kcat/openal-soft/blob/b621b5fce739525418f36e0474a46f9e1cab5e64/core/voice.cpp#L950-L959)。

参见[数值素材收录说明](numeric/PACKAGE-NOTES.md)和[能力部分说明](README.md)。
