# 立体声折叠：来源和证据

- FFmpeg [filter manual](https://ffmpeg.org/ffmpeg-filters.html#pan-1)，pan：输出布局、明确增益、'<' 的归一化。并核 [FFmpeg n7.1.2 filters.texi](https://github.com/FFmpeg/FFmpeg/blob/n7.1.2/doc/filters.texi) 对应章节。实际环境版本写入 JSON；不拿仿真重写代替运行。
- Microsoft [Xbox Accessibility Guideline 105](https://learn.microsoft.com/en-us/gaming/accessibility/xbox-accessibility-guidelines/105)，mono 送左和右与 Diablo III 界面示例：可访问目的与实际输出内容。指南没有规定下混电平或软件通道矩阵，亦非对同一设备的实验。
- Unity [Audio Clip](https://docs.unity3d.com/6000.0/Documentation/Manual/class-AudioClip.html)，6000.0，Force To Mono 与 Normalize 可由导入路线改变打包资产。没有调用 Unity 或验证其默认系数，不把旧 Unity 文档变更当成本版实现。
- [实际 FFmpeg](../实验/立体声单声道折叠/README.md) 48 kHz PCM 的合成周期对照，精确的整偶数样本/反相，避免半整数舍入噪声。FFmpeg 跑指定矩阵的结果和理论相符。稳态区间排除延迟起始瞬态，不推断宽带、人耳响度、游戏正式混音或不同设备。可从脚本重生成各文件，仓库输出 JSON 保存各 WAV 摘要。
