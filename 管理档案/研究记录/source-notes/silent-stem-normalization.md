# 静音 stem 与结束输入：来源与有限取证范围

对应拟议 `SOL-SFX-002`。2026-11-01 读取 FFmpeg 官方仓库比较提交 `3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587`；不把标签或源码提交视为本机程序来源认证。

| 原始材料 | 回查定位 |
|---|---|
| [filters.texi](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/doc/filters.texi) | `amix` 的 weights/normalize/duration/dropout_transition；`asetnsamples` 的 n/p |
| [af_amix.c](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/af_amix.c) | `calculate_scales`、`output_frame`、`activate`；活跃输入与其内部 FIFO |
| [avfilter.c](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/avfilter.c) | `ff_inlink_acknowledge_status`、`ff_inlink_consume_samples`；链接队列与结束状态 |
| [af_asetnsamples.c](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/libavfilter/af_asetnsamples.c) | `activate`；固定块与禁用末块补零 |

主研究者与独立审查者实际读固定原文。网页抓取遇到缓存未命中或超时后，使用授权 GitHub 连接器读取同一原始仓库文件；没有规避权限或把滚动文档当成固定版本。归档仅保留原创夹具、日志、来源定位和简短推导，不转载上游完整源码。

作者 记录别名 `历史执行记录-01` 与独立复跑 记录别名 `历史执行记录-02` 各一次版本查询、三次离线混音。两者全部输出字节符合提前冻结的三配置预期；没有改变样本边界、排除窗口或容差。协议 `04beb14e…`、最终源码清单 `e830cfff…` 和独立字面预期 `a904ecc7…` 的完整摘要见[实验归档](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/experiments/ffmpeg-silent-stem/README.md)。版本查询为本地自报，不反证或认证固定源码对应关系。

本地文件摘要只描述被记录的程序与选定库文件，不认证全部加载依赖。原始正零与半幅常数是数值取证输入，不是玩家音频；未进行听音、响度评估、设备播放或中间件集成。已有假端口音乐调度与 PCM/Opus 帧数研究不因本条增加而取得新的运行结论。

> 公开衍生说明：本次仅省略安装位置、安装指纹或执行记录标识，并调整现址/固定历史链接；技术观察、失败、计数与原有证据范围保留。正文中的“本次”及身份相等陈述均属于原记录时点，本轮未重新检验，未运行旧实验，原始摘要声明不改写为新字节。文中描述性记录别名不是可执行目录名。
