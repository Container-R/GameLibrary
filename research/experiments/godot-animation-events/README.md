# AnimationPlayer seek不是区间事件重放

## 实际结果与范围

2026-10-31，在本机Godot自报`4.6.3.stable.official.7d41c59c4`、Linux headless、MANUAL更新与IMMEDIATE方法模式下运行六个新进程。源码与二进制SHA-256在`results/summary.json`。所有方法只记录合成标签，不代表真实伤害、碰撞、规则步或玩家行为。

| case | 方法键 | 操作 | 实际标签顺序 | 完成信号数 |
|---|---|---|---|---:|
| seek_cross | 0.5:single | seek0.75，再seek1.0；update=true/update_only=false | single,single | 0 |
| advance_cross | 0.5:single | advance0.75，再advance0.25 | single | 1 |
| seek_exact | 0.5:single | seek0.5，update_only=false | single | 0 |
| seek_exact_update_only | 0.5:single | seek0.5，update_only=true | 空 | 0 |
| seek_two_cross | 0.25:A，0.6:B | seek0.75，再seek1.0 | B,B | 0 |
| advance_two_cross | 0.25:A，0.6:B | advance0.75，再advance0.25 | A,B | 1 |

各case真实float属性与播放位置在第一阶段为0.75（cross）或0.5（exact）；cross第二阶段为1.0。初始化为0。advance正控制排除了坏方法路径使seek空计数的假通过。`update_only`两case只改变该参数；它们不是“seek跨越中间事件”的同一问题。

**结论应是seek与advance不是等价的事件交付操作，不能说seek绝不会调用方法。** 在这台二进制里，两个键的seek选择B且后一次再次调用B；advance交付A,B。故表现位置相同不保证区间事件相同或恰好一次。规则事件是否补算、丢弃或去重仍需应用明确制定，不由播放器属性值替代。

## 原假设失败保留

`proposal.md`是执行前提案，不是最终结论。原先预期seek跨过0.5不会调用方法，实际出现调用，`historical-initial/run.py`在first event outcome处失败并未产生summary。其源码与原始seek日志保留；随后其他三个策略的诊断输出也保留在该目录。未把这一失败称作引擎bug。

查询官方标签代码后先做过一次四 case 修正，再增加两个有标签的方法键区分选择与遍历。公开归档保留初始失败与最终六例；中间四例过程副本未重复发布。当前六case是明确修正后的观察性回归合同，不是原假设被验证。历史目录中runner仅为归档，不应当作当前入口运行。

## 来源对应存在未解决差异

[Godot4.6 AnimationPlayer seek文档](https://docs.godotengine.org/en/4.6/classes/class_animationplayer.html#class-animationplayer-method-seek)说明略过中间事件、update_only抑制方法等轨、到末尾seek不发完成信号。[AnimationMixer文档](https://docs.godotengine.org/en/4.6/classes/class_animationmixer.html)定义MANUAL/IMMEDIATE/DEFERRED模式及非循环完成信号；本夹具没有测试默认延迟队列。

通过公开GitHub插件核对，`4.6.3-stable`标签的commit是`35e80b3a8822a9df9be390814b62f44c0a9c69e8`。其[animation_mixer.cpp TYPE_METHOD分支](https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/animation/animation_mixer.cpp#L1650-L1677)把seek的键选择和非seek的区间遍历分开，外部seek使用名为FIND_MODE_NEAREST的模式。这里不把枚举名翻译成未经验证的“数学距离最近”。

但安装二进制`Engine.get_version_info()`自报完整hash为`7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3`，公开GitHub对该commit查询返回422 No commit found。**不能宣称标签源码就是本机二进制的精确构建源码。** 代码仅作独立的实现语义参照；本机结论依赖归档二进制hash和实际回调/属性日志。自报字符串中的official不是本研究独立认证过的构建身份。版本身份对应仍待核实，不能把本次测试写成所有官方4.6.3发行物已经验证。

## 运行与证据

```
python run.py
```

入口使用`/usr/local/bin/godot`，无需安装/下载资源。每个版本查询和运行设独立临时可写HOME/XDG目录；保存各case命令、原始stdout/stderr、单一`RESULT_JSON=`载荷及解析JSON。校验器先拒绝Python -O；正常路径随后移除旧summary。异常不生成本次PASS摘要，但优化模式拒绝可能保留历史PASS摘要。原始输出不截掉错误，非空stderr令本次接受失败。

源码清单为main.gd/main.tscn/project.godot/run.py，README不参与运行hash；历史源与当前源分开。`results/summary.json`记录六次实际运行、版本、Python/平台和hash。单个case有CONFIG、TRACE、SIGNAL文本与结构载荷，独立审查可核对请求与实际回调，而非只相信PASS字样。

本次不覆盖循环、倒播、混合、AnimationTree、DEFERRED、帧率/物理/联网确定性、真实战斗或其他引擎。IMMEDIATE是有意控制变量，不是建议生产中总把默认DEFERRED改掉；回调修改/删除节点等风险未测试。独立复跑若用同一台二进制，仍只是同构建重复证据，不是跨版本或跨平台保证。

## 统一身份说明与独立复核

[共享构建来源说明](../../source-notes/godot-runtime-provenance.md)保留自报版本、可执行文件摘要与公开标签不能自动对应的限制。[独立审查](review/README.md)在独立目录重复六个进程，再用另一判据读取原始回调轨迹；同摘要二进制的重复观察不认证官方发行来源。

**调用新鲜度：** [历史摘要与本次退出状态必须分开](../../source-notes/runner-invocation-freshness.md)。早期拒绝可能保留旧成功文件，不能只读 PASS 判断最新调用。
