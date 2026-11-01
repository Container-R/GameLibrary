# GGPO重放与表现输出：来源定位

补充[客户端预测与权威边界](../../solutions/programming/client-prediction-authority-boundary.md)。读取2026-11-01；仅源码/文档，不运行SDK。

统一固定提交：`7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a`，GitHub commit时间2019-11-07T17:39:58Z。三个文件属于同一作者项目，不构成三个独立厂商交叉验证；未建立任何安装二进制对应关系。

| 原始文件 | 已读定位 |
|---|---|
| [DeveloperGuide.md](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/doc/DeveloperGuide.md) | Game State and Inputs；save/load/free callbacks；frame-delay警示；Separate Updating Game State from Rendering；RNG及external time章节 |
| [ggponet.h](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/include/ggponet.h) | GGPOSessionCallbacks中的save/load/free/advance注释；flags保留字段不能当作确认令牌 |
| [sync.cpp](https://github.com/pond3r/ggpo/blob/7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a/src/lib/ggpo/sync.cpp) | AdjustSimulation、LoadFrame、SaveCurrentFrame，另核对SetLastConfirmedFrame |

指南短闪烁例子在同段混用frames/seconds，本库只采用其定性风险，不自行修正数字后当成规范。文档要求、应用回调责任和代码实际调用路径分开理解；所读路径的推进/保存/恢复回调返回值未构成外部效果投递确认。不能把这项局部检查扩展为全SDK或所有集成的缺失证明。Sync中确有SetLastConfirmedFrame等内部确认帧机制；这里没有把它解释为外部输出或经济事务的确认保证。网页抽取行号与源码视图可能不同，定位采用固定提交、方法和章节名称。

正文五行情形及验收条件为原创未执行建议，不是GGPO公开内部表单或已经验证的事件协调器。原权威服务器模型与P2P回滚语境不同；原有16项模型测试保持原范围。本次未进行安装、编译、网络、音频、渲染或持久交易验证；未复制完整指南、源码或第三方案例图像。
