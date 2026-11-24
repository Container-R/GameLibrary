# 分层配乐的共同播放位置：来源记录

- FMOD Core API 2.04，[ChannelControl::getDSPClock](https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html#channelcontrol_getdspclock) 与 [setDelay](https://www.fmod.com/docs/2.04/api/core-api-channelcontrol.html#channelcontrol_setdelay)。后者的时钟值以直接父 ChannelGroup DSP 时钟的采样位置为准。它指定开始/停止时刻，不设置媒体内游标；本文未执行 FMOD。
- FMOD Core API 2.04，[Channel::setPosition](https://www.fmod.com/docs/2.04/api/core-api-channel.html#channel_setposition)：流重定位、非阻塞就绪及 VBR 位置精度条件。
- FMOD Core API 2.04，[Virtual to Real Transition](https://www.fmod.com/docs/2.04/api/managing-resources-in-the-core-api.html#virtual-to-real-transition)：恢复推进后的时间位置与 FMOD_VIRTUAL_PLAYFROMSTART 例外。不能推断所有引擎的增益零都会继续推进。
- [OpenAL 1.1](https://www.openal.org/documentation/openal-1.1-specification.pdf)，源偏移与一组源的播放调用；[ALC_SOFT_loopback](https://github.com/openalext/openalext/blob/master/ALC_SOFT_loopback.txt)，由调用者索取混音帧。[实际实验](../实验/分层配乐的播放游标/README.md)在 OpenAL Soft 1.24.2 受控采样，不外推至流送、虚拟化与设备端。
- 本库[PCM 循环区间](../../GameLibrary/声音与音乐/音频制作/循环素材/如何标记和检查PCM音乐循环区间.md)与[虚拟化恢复策略](../../GameLibrary/声音与音乐/游戏音效/播放管理/循环声音重新听见时，应该从哪里继续.md)提供相邻素材与生命周期语境。拍点、数据表、时间例和离线夹具为本文原创。
