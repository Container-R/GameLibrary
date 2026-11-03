# 配置与能力边界摘要

公开安全衍生摘要，非原记录字节。固定1.24.3与后续1.24.2的相关配置链已逐项比较，详细版本范围见[版本摘要](VERSION-1.24.2-REVIEW.md)。没有读取本机系统配置内容。

原源[alconfig.cpp](https://github.com/kcat/openal-soft/blob/b621b5fce739525418f36e0474a46f9e1cab5e64/alc/alconfig.cpp#L382-L485)依次积累系统、XDG、用户及程序旁配置，最后再读ALSOFT_CONF。它是追加/覆盖，不是独占配置；设备专属键也可能优先于一般键。空用户目录和受控配置不能证明全部系统配置被排除。

ALSOFT_DRIVERS=null且没有尾逗号，用于限制所读实现的普通backend选择；loopback工厂另外初始化。它不是未知安装库的系统调用追踪证明。代码没有普通设备open、设备枚举或capture，render入口仅核存在。

mono的所读分支在HRTF选择前返回；limiter显式false请求有效，但能力门仍要求实际getter读回。HRTF/limiter关闭不证明全部处理链纯净，float输出也可能受显式dither配置影响。没有公开getter证明这里所有配置项均关闭。

早期设计记录曾提10秒及更多可选技术字符串；真正冻结协议采用15秒通信加最多2秒回收，仅收受限版本/renderer，不读vendor或设备名。原协议与结果分别保留，不能把早期预算当同时生效的另一个要求。仅管理唯一child，不声称整个进程组消失认证。

返回[能力包说明](README.md)。
