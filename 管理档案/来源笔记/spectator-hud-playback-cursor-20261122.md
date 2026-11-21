# 观战比分与画面同步：来源及验证

| 主张 | 证据定位 | 结论边界 |
| --- | --- | --- |
| 媒体定位、数据准备和合成是不同阶段 | WHATWG [HTML Media: currentTime](https://html.spec.whatwg.org/multipage/media.html#dom-media-currenttime) 与 [Seeking](https://html.spec.whatwg.org/multipage/media.html#seeking)，seek 算法步骤 11–17；[WICG requestVideoFrameCallback](https://wicg.github.io/video-rvfc/)，VideoFrameCallbackMetadata、视频合成时序。 | mediaTime 是视频帧 PTS，可能在部分直播/WebRTC 中为零；回调不是物理显示确认，不能推出游戏 tick。分段同源锚点、版本和更新规则为本文设计。 |
| 引擎回放可以按基线、检查点与后续增量恢复 | Epic [Using the Replay System](https://dev.epicgames.com/documentation/en-us/unreal-engine/using-the-replay-system-in-unreal-engine) 的控制表；[DemoNetDriver and Streamers](https://dev.epicgames.com/documentation/en-us/unreal-engine/demonetdriver-and-streamers-in-unreal-engine?lang=en-US) 的世界重建段；[GotoTimeInSeconds 5.5](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/Engine/Engine/UDemoNetDriver/GotoTimeInSeconds?application_version=5.5) 的委托。 | 这不是实际跑过的 Unreal 工程；检查点摘要不证明本文自定义的计分覆盖、保密和 Web 合成。 |
| 收到未来数据不会自动补齐过去，确认静默需要完整的覆盖承诺 | [Node 合成对照](../实验/观战比分与画面同步/README.md) prefix。 | 严格与暂定是项目策略；仅验证指定合成批次与结果。 |
| 状态修正与提示重播可分离，最新跳转代号可拒绝旧响应 | 同一说明页 cursor。 | 模拟应用层，不证明引擎或浏览器的回调顺序，也不测实际画面和 HUD 同帧。 |

调阅日期：2026-11-21。
