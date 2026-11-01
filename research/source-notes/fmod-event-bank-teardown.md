# FMOD 事件结束与 bank 卸载：来源范围

2026-11-01 读取；补充[交互音乐状态交接契约](../../solutions/audio/music-state-transition-contract.md)的生命周期部分。依据 FMOD Engine User Manual **2.04.00**，页脚标记 **2026-09-29**；这是可变网页的版本／日期标记，不认证软件发布日期、固定实现或安装版本。

## 原始资料与定位

- [Studio::EventInstance](https://www.fmod.com/docs/2.04/api/studio-api-eventinstance.html)：release（当次文本 1039–1064）、stop（1788 起）、FMOD_STUDIO_STOP_MODE（2206–2209）、callback types（1951–1968）。用于区分停止政策、释放标记与通知类型，不把销毁通知解释成自然结束原因。
- [Studio::Bank](https://www.fmod.com/docs/2.04/api/studio-api-bank.html)：unload（716–743）、unloadSampleData（744–768）。用于核对整体卸载与样本引用计数的不同作用域；后者不是 bank 持有票据。
- [Studio API Guide](https://www.fmod.com/docs/2.04/api/studio-guide.html)：§13.4（107–112）、§13.7–13.8（142–157）、§13.11（258–269）。用于命令服务、资源层次与回调线程边界；未将仅适用于部分通知的 deferred 配置泛化。

三页属于同一厂商文档体系，不是三种独立实现验证。行号属于当次文本视图，优先用方法及章节名定位。既有音乐文章的旧来源日期、历史 Wwise 案例、假端口模型与虚拟化观察合同保持各自范围。

## 原创部分与未验证项

场景退出的“保尾部／优先回收”分叉，是组合文档语义提出的原创未执行资源政策，不是厂商现成管理器或已复现的截断事故。结束记录应带项目身份和所选退出政策；延迟处理记录不保证原 SDK 句柄仍有效。没有规定所有销毁路径的通知顺序，也没有把任何中间件状态升级为听觉完成证明。

本文只讨论普通 Studio 事件与所需 bank 的持有责任。未运行 SDK、播放或录音，没有设备时延、尾音完整性、内存节省量或卸载耗时测量。跨 bank 图、程序员声音、完整总线／混响保护及 `LOAD_MEMORY_POINT` 用户内存释放协议不纳入结论。来源发现中 Studio::System 页面访问未成功，未用该页填补这些未知；不转载源码、音频、图像或完整文档。
