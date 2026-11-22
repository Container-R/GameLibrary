# 短对白综合响度：证据

- [ITU-R BS.1770-5 (2023)](https://www.itu.int/dms_pubrec/itu-r/rec/bs/R-REC-BS.1770-5-202311-I%21%21PDF-E.pdf)，Annex 1 式 (3) 至 (7)：完整 400 ms 块、75% 重叠、两道门限及能量平均；Annex 2 区分采样峰值和滤波估计的真峰值。
- [FFmpeg 7.1 ebur128 源码](https://ffmpeg.org/doxygen/7.1/f__ebur128_8c_source.html)，ABS_THRES 定义及 integrated_loudness 初始化、400ms 窗及 100ms 更新。短文件显示的 −70.0 绑定本试件与版本，不泛化到其他仪表。
- [实跑证据](../实验/短对白响度门控/README.md)，FFmpeg 7.1.5-0+deb13u1。合成正弦控制时长、留白和幅度来区分测量改变与电平改变，不比较真人表演、听感或运行时混音。增益须在目标素材与总线上另行复测。

调阅日期：2026-11-23（北京时间）。
