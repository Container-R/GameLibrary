# 显示换帧间隔与连续超标：来源核对

2026-11-25 核对。[复现与原始输出](../实验/显示换帧间隔与连续超标/README.md)。

- [PresentMon Console Application](https://github.com/GameTechDev/PresentMon/blob/main/README-ConsoleApplication.md#csv-columns)：`MsBetweenPresents` 属提交间隔；`MsBetweenDisplayChange` 定义指向在当前显示之前的上一帧；`DisplayedTime` 是本行帧的显示时间，未显示时可为 NA。查看选项、版本及可用标识；不假定单个导出会同时含所有列。
- [Android Frame Pacing](https://developer.android.com/games/sdk/frame-pacing/#how-it-works)：没有新缓冲时可复用上一内容；正确的 30 Hz 节奏是产品目标与显示节奏的配合，不把 60 Hz 的每个刷新都要求为新帧。
- [Perfetto FrameTimeline](https://perfetto.dev/docs/data-sources/frametimeline#janks-explained)：预期及实际的应用和合成工作，时间线样例和帧 token 作为继续排查的入口。不能把合成记录归因到其中某类。
- 600 间隔统计、六行裁剪和刻意 30 fps 触发数量均为本库合成试件的实际脚本输出，非上述作者采集样本。
