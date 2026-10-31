# PCM音乐主体端点交接：实际FFmpeg离线提取

2026-10-31。原创marker素材，不是音乐试听或中间件运行。实现前已冻结 [contract.md](contract.md)。实际运行exit0：正确区间和故意错一帧区间均由已安装FFmpeg执行，逐字节验证decoded PCM，另外ffprobe核对帧时基/声道/位深；不是只看duration小数。

## 一份素材，两种实际裁剪

48kHz stereo PCM16。一个sample frame包含L/R各一个16-bit分量，所以4bytes/frame；96539frames文件内容有193078声道分量。四分音符123BPM、4/4一小节理想帧数3840000/41，项目nearest half-up政策取93659frames，不声称FMOD或DAW也用此政策。

|范围|半开frame区间|frame数|PCMbytes|
|---|---|---:|---:|
|前置|[0,480)|480|1920|
|主体|[480,94139)|93659|374636|
|尾部|[94139,96539)|2400|9600|
|全文件PCM|[0,96539)|96539|386156|

正确actualfilter：`atrim=start_sample=480:end_sample=94139,asetpts=PTS-STARTPTS`，得到93659frames，首帧(1234,-2345)、末帧(3456,-4567)，全部PCM与独立literal oracle一致。

故意把inclusive末帧数字94138传给exclusive end_sample：得到93658frames，少4bytes，末帧变成普通主体(100,-100)。这是实际离线工具结果。没有调用FMOD；FMOD2.04端点inclusive映射仅来源支持，即主体的候选参数480..94138，而不是480..94139。API范围、loopmode、流缓冲限制仍应在实际接入时验证。

## 来源与执行身份

- [固定FFmpeg源doc/filters.texi 3773起atrim节](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/doc/filters.texi#L3773-L3822)：n7.1.5经GitHub插件解析到commit3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587（2026-06-19）。end_sample定义首个丢弃sample；_sample计数与时间戳参数不同；atrim不重置时间戳，故另用asetpts。不是假定输入timestamps普遍可靠。
- [FMOD2.04 Sound::setLoopPoints](https://www.fmod.com/docs/2.04/api/core-api-sound.html#setlooppoints)：inclusive端点和loopmode/range说明；[TIMEUNIT](https://www.fmod.com/docs/2.04/api/core-api-common.html#fmod_timeunit)：PCM与PCMBYTES单位区分。来源访问2026-10-31，无FMOD SDK执行。
- 实际/usr/bin/ffmpeg和ffprobe自报7.1.5-0+deb13u1，版本完整输出、二进制SHA在summary及独立version日志。官方tag不是本地Debian发行二进制来源认证；未假定二者字节/源码完全对应。Python3.12.14。

## 复验与封装

`python run.py > run-output.txt 2> run-stderr.txt`

运行只读本地工具，写本目录results。建议复制到新目录再跑，勿覆写归档作者结果。当前run-stderr为空，FFmpeg自己的stderr正常输出保存于各case-stderr.txt；每个子进程命令、exit和stdout/stderr单独保留。工具timeout10秒，非0立即阻断PASS；先删旧summary再做优化模式拒绝及子进程执行。不是通用原子receipt或系统故障证明。

results/source.wav、correct.wav、offbyone.wav为本地原始二进制；**文本发布只需对应.wav.gz.base64**，每份编码低于100KB。gzip mtime=0，严格base64解码再gzip解压可恢复原始WAV，原始/编码文件大小与SHA在summary。只解包到新临时目录，并核对SHA；不是用重新生成替代原始字节。FFmpeg输出header可含不同metadata，验收比较PCM而不是强求整WAV与生成器一致。

summary包含run.py/contract.mdhash、tool身份、制品hash、两条实际结果；stdout单个RESULT_JSON。未用assert验收。原始PCM是人工低幅整数marker，不播放、不衡量听感。当前两次实际filter行为不证明sample-rate转换、压缩格式gapless、click不可听、声卡延迟、FMOD调度或音乐转场自然。93659整数帧不等于精确分数拍长，不能推出无限重复都与理想123BPM网格无误差。
