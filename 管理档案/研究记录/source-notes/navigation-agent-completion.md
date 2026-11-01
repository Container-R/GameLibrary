# NavigationAgent3D 路径结束与目标到达：来源说明

读取日期 2026-11-01。关联[现有导航文章](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/solutions/ai/navigation-readiness-and-partial-path.md)与[新增跟随夹具](https://github.com/Container-R/GameLibrary/blob/800d505633df0ceaa0bab8de643b0244ba1a5476/research/experiments/godot-navigation-completion/README.md)。旧查询/半径夹具保持原字节与范围。

## 版本化原始资料

- [Godot 4.6 NavigationAgent3D](https://docs.godotengine.org/en/4.6/classes/class_navigationagent3d.html)，Description、navigation_finished / target_reached signals、get_next_path_position / is_navigation_finished / is_target_reachable / get_final_position methods：完成路径与接近原目标是不同状态；回调内触发更新可能递归。类标记 Experimental。没有从该页面推导本夹具固定坐标或步数。
- [Godot 4.6 Using NavigationAgents](https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationagents.html)，Pathfollowing：移动父节点是应用责任。这里仅以它支持受控 Node3D 驱动的范围，不导入示例中的 CharacterBody 或 RVO 结果。
- 固定比较提交 `35e80b3a8822a9df9be390814b62f44c0a9c69e8` 的 [navigation_agent_3d.cpp 705–765](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/navigation/navigation_agent_3d.cpp#L705-L765)说明目标提交和更新 getter；[799–923](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/navigation/navigation_agent_3d.cpp#L799-L923)提供目标/路径点距离与完成分支；[984–1000](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/3d/navigation/navigation_agent_3d.cpp#L984-L1000)提供状态写入与信号顺序。所读更新路径未提供同帧调用自动无操作的保证。

## 原创实验与推论

两个手工凸区域、两组目标、0.5 单位受控位置赋值、初始几何/就绪门槛、四次更新查询先于全部位置写入，以及从原始事件独立重建的验收规则，均为本研究的有限协议。源码提供预期的分支语义；实际坐标、信号和次数来自档案，不能凭源码代替执行。

把 finish-only 业务接线与保留目标语义的分支进行对比，是原创建议。没有测试真实游戏任务、玩家反馈、物理角色、取消或重规划系统，也不规定部分路径永远不能被产品视为成功。

## 身份与失败记录

当时选定的 Godot 文件安装摘要已从本公开衍生说明省略，版本仍为程序自报。固定公共提交仅作实现比较，构建来源对应仍未认证。前后摘要/命令/原始流绑定支持档案复查，不是执行真实性签名。

协议与代码审查先于原生调用。运行前合成假记录暴露的 consumer/oracle 缺口单独保留，不写成引擎错误；启动保护测试只启动 Python，不启动 Godot。原生失败/超时分支没有因为代码存在就算作已执行。

公开衍生维护说明：本次仅省略安装环境信息，保留原有技术结论、失败与证据限制及已修正的固定历史链接；未运行旧实验，也未重写历史记录。
