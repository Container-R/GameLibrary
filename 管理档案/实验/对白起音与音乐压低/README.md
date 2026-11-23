# 复现：对白起音与音乐压低

- [检测窗](native_detector.py)：在临时目录用 Python 3 和 FFmpeg 7.1.5 运行；与 [实测结果](native_detector.observed.txt) 比对。输入是分析用的等能载波，不供试听。四列窗口依次为第一开头、正文、随后的停顿、第二开头。
- [合成干声和音乐的三版对照](mix/README.md)：用原生滤镜生成 WAV，保持同一干轨。记录音乐输出/输入能量、测试窗和样本峰值；未做听审。
- [计划请求的所有权](ownership_check.mjs)及[输出](ownership.observed.json)：Node 24.22.3 测早取消、重叠及旧代回调。时间是示意刻度，未模拟设备和音频回调。
- [停顿余量](gap_budget.mjs)及[输出](gap_budget.observed.json)：线性 dB 斜坡，指定 160 ms 回升和 60 ms 预压，比较三个不同停顿；只算时间预算，不验证听感。

[返回正文](../../../GameLibrary/声音与音乐/音频制作/混音/对白起音时，怎样测音乐压低的时序和深度.md)
