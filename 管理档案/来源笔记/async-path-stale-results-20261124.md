# 异步寻路结果何时还能交给 NPC：来源记录

| 主张 | 依据 | 范围 |
| --- | --- | --- |
| 异步查询返回 ID，已处理的失败也调用结果委托 | Epic Games，[Unreal Engine 5.8：FindPathAsync](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/NavigationSystem/UNavigationSystemV1/FindPathAsync?application_version=5.8)，Description、Parameters，2026-11-24 | 不推导每份取消请求都回调，也不规定结果排序或回调线程。 |
| 取消接口以 ID 从待处理队列移除请求 | Epic Games，[Unreal Engine 5.8：UNavigationSystemV1](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/NavigationSystem/UNavigationSystemV1?application_version=5.8)，公开函数 AbortAsyncFindPathRequest，2026-11-24 | 签名 void；其说明没有承诺撤销每个后续阶段或应用队列中的命令。正文不声称复现了 UE 的竞态。 |
| 路径对象有起点、部分路径与当前状态；可选配置忽略常规失效 | Epic Games，[Unreal Engine 5.8：FNavigationPath](https://dev.epicgames.com/documentation/unreal-engine/API/Runtime/NavigationSystem/FNavigationPath?application_version=5.8)，GetStartLocation、IsPartial、IsUpToDate、SetIgnoreInvalidation，2026-11-24 | 忽略失效时可能仍保留当前标记。单个标记不是位置接入、角色权限或目标可操作的保证。 |
| 写入权限与几何可用性是不同判断，旧结果不得改变路线或停止当前运动 | 本库[应用层状态对照](../实验/异步寻路结果接纳/README.md) | 人工控制成功/失败与完成顺序，状态与票据由脚本处理。实验独立于引擎调度，不验证几何、取消实现或性能。 |
