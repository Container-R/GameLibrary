# 回滚与表现：来源和证据

- GGPO [Developer Guide，固定提交 7ddadef](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/doc/DeveloperGuide.md)，Game State and Inputs、Separate Updating Game State from Rendering，重算调用多次，实际发声与显示在重算后，音视频系统可与玩法状态解耦。未运行 GGPO 或自己的网络模拟协议。
- Michael Stallone（NetherRealm Studios），[8 Frames in 16ms](https://media.gdcvault.com/gdc2018/presentations/Stallone_Michael_8FramesIn16ms.pdf#page=22)，GDC 2018，原始 PDF 第 22 页 Recreatables：按对象类型检测可复用性，声音／粒子是其中例子。没有复用原图和音频，也不把所讲的复用、快照、性能数据当作本文示例的直接行为。
- [可执行复现](../实验/回滚表现对账/README.md)两套合成证据分开：保存并重算真实小游戏整数状态后缀，比较错误直接播放、全部抑制与最终状态协调；或向 Presenter 喂已协调的效果清单做局部规则检验。都没有运行真实引擎、播放器、跨崩溃、网络权威或分布式状态，没有真人能否察觉声音的测量。
