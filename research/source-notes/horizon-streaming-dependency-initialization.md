# Horizon 流送依赖与初始化：来源范围

2026-11-01。对应 [CASE-ENGINE-002](../../case-studies/engine/horizon-streaming-dependency-initialization.md)。本记录提供定位，不重复历史机制摘要。

- [Guerrilla 原始发布页](https://www.guerrilla-games.com/read/Streaming-the-World-of-Horizon-Zero-Dawn)：页面日期2023-03-21；讲者介绍使用 Jan-Jaap。没有据此确认原演讲日期或补出完整署名。
- [官方直接链接 PDF](https://d3d3g8mu99pzk9.cloudfront.net/AstridHuntjens/Streaming%20the%20world%20of%20Horizon%20Zero%20Dawn.pdf)：107页，SHA-256 `e7865c1c3f2ac165a745156406f42f5a5eb38c15b9f1b8b51aea0b0b17e18647`。这是取得的公开文档身份，不是游戏实现版本或二进制认证。

## 实际读取范围

物理页1、8、16–20、29、49文字；主审另直接查看物理页1、18、19图像。页18的依赖顺序和页19的文件完成/初始化工作须共同理解，不推出全图读取完毕才能初始化。无环前提不提供循环处理算法。没有依图重建完整线程亲和性、调度优先级或图形布局。

原演讲日期仍未知。发现阶段的后续演讲搜索片段提示过2017，但其PDF直接访问受阻，未将摘要升级为证据；也未把2023网页日期当作原会期。PowerPoint入口未取得可读内容。没有绕过访问限制。

## 原创贡献与未验证部分

A→B→S、D→S 图和接收表由本库构造，箭头定义为消费者到初始化前置依赖，不是来源图复刻或实际 Horizon 轨迹。它没有固定任意 I/O 完成次序，没有提供取消、失败恢复、并发初始化或动态依赖的通用实现。来源事实仅在案例短段中概括，其余是明确未执行的工程分析。

没有引擎、调度模型、SDK、设备或生产性能测试；未读取关联运行归档，不转移 Godot 或 Unity 的证据。没有复制幻灯片、截图、PPT、PDF全文或游戏资产。对未来版本、其他引擎及平台的适用性须另核对。
