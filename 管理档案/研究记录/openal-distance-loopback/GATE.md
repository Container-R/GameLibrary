# 来源门摘要：显式loopback，不是播放设备

公开安全衍生摘要，非原GATE.md字节。初门是在执行之前形成的来源/API条件性GO，不是当时已经观察到设备支持。

实际原源为[ALC_SOFT_loopback扩展](https://openal-soft.org/openal-extensions/SOFT_loopback.txt)全文，以及官方1.24.3固定提交 [dc7d7054a5b4f3bec1dc23a42fd616a0847af948](https://github.com/kcat/openal-soft/tree/dc7d7054a5b4f3bec1dc23a42fd616a0847af948) 的alext.h、alc.cpp loopback入口、loopback backend、距离分支与所选增益平滑代码。来源基线不等于安装库身份。

专用alcLoopbackOpenDeviceSOFT(NULL)并非alcOpenDevice(NULL)。格式需显式频率、声道和样本类型；本能力门只检查入口、48000/mono/float支持、context和实际属性，不调用render。官方alloopback示例还连接SDL播放设备，不能整段拿来执行本门。

第一次遇到版本差异后停止，没有试真实设备fallback。随后[版本复审](VERSION-1.24.2-REVIEW.md)才允许准备新来源基线。当前两次结果见[README](README.md)，初门的暂定数值设计不构成本包数值执行或验收。
