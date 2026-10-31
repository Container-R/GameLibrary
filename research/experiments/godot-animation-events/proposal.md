# Godot 4.6动画跳转与事件交付：来源闸门和单一夹具提案

核对2026-10-31。当前只做文档调查与安装版本查询，未执行动画夹具。公开官方4.6文档与已安装4.6.3不能混写为其他引擎行为。

## 原始来源

- [AnimationPlayer 4.6](https://docs.godotengine.org/en/4.6/classes/class_animationplayer.html)，seek方法（本次文本402–407行）：跳转跨过的事件被略过；update控制立即更新，update_only另行抑制方法/音频/播放轨；跳到末尾不发animation_finished。play（330–336行）说明立即处理可用advance(0)。旧set_method_call_mode/set_process_callback已弃用，应使用继承的Mixer属性。
- [AnimationMixer 4.6](https://docs.godotengine.org/en/4.6/classes/class_animationmixer.html)，AnimationCallbackModeProcess/Method枚举（102–124行）区分手工推进、立即方法和默认延迟批处理；animation_finished（56–60行）注明循环动画不发该信号。本文不把默认延迟队列未冲刷误认作事件丢失。
- 本地/usr/local/bin/godot --version实际返回4.6.3.stable.official.7d41c59c4；这次未隔离查询出现Fontconfig cache警告。正式运行必须和此前夹具一样设置独立可写HOME/XDG目录，保存完整输出，不筛掉错误。此查询不是动画证据。

## 要回答的一个问题

同样抵达动画时间0.75秒，seek与advance是否产生相同的中间方法事件？若并不相同，“表现位置已经追上规则时间”就不足以证明表现轨上的一次命中回调已经被交付。这是窄范围API反例，不是证明动画事件永远不能参与玩法。

## 建议单一夹具、两个隔离进程

原创Animation长度1.0秒、非循环、无混合，无RESET/AnimationTree/音频轨。一个连续float值轨从0到1作为实际采样证据；一个TYPE_METHOD键在0.5秒调用记录函数。对象位于真实SceneTree，方法只写日志和计数，不删除节点、不修改播放器。

统一设置callback_mode_process=MANUAL、callback_mode_method=IMMEDIATE，打印属性实际getter值；play后advance(0)初始化并记录零点。每个策略在独立进程使用同样资源生成代码，避免seek后的内部状态影响另一个策略。

| 策略 | 第一步 | 第二步 | 文档预期，待实际验证 |
|---|---|---|---|
| seek | seek(0.75,true,false) | seek(1.0,true,false) | float值与位置确实更新；跨过0.5方法不补发；第二步不发完成信号 |
| advance | advance(0.75) | advance(0.25) | float值/位置到相同点；0.5方法实际交付一次；到末尾发完成信号 |

结束边界若实际需跨越而非等于1.0，应保留原始结果并先报告，不默默改变测试使其通过。第一步跨越0.5而不落在该键，避免把seek命中目标时刻的行为混进“跳过中间事件”主张。两个策略都用update_only=false，避免通过显式抑制轨道人为制造差别。

## Oracle与归档

- 检查真实回调日志与信号事件，不用请求操作次数代替交付次数。
- 同时校验float目标属性数值、播放位置、动画名/长度、轨道键时刻与方法名，排除坏NodePath/没有播放导致的空计数。
- 第一段advance必须形成正控制：实际调用标记方法；否则seek零次没有解释力。
- 记录两阶段函数调用前后序列、完成信号名；不要求未研究的回调与属性写入内部相对顺序。
- Python编排器保存原始stdout/stderr、进程返回码、源与引擎二进制hash、实际版本、环境隔离说明。拒绝-O，批次先清旧summary，任何失败不留下成功摘要。
- 方法IMMEDIATE已消除默认延迟排队的歧义，但不证明DEFERRED行为、帧率表现或线程安全；本轮不增加延迟变体。

## 有用结论和停止条件

若两策略都确实采到相同属性/位置而交付不同事件，能补上现有固定步战斗文章的一条真实引擎证据：seek式表现追赶不是规则事件重放。由谁补算已跨过的规则事件、是否允许跳过以及命中去重，仍是应用合同，不从这两个回调计数推导碰撞、物理、网络确定性或整套战斗正确性。

本轮止于这两进程、独立复核及原始证据，不建大规模API套件，不声称任何Unity/UE等价语义。实际执行需父代理确认范围；当前没有创建可执行夹具。

## 执行后校正索引

原始预期已被实际运行否定；请勿把上表当成结果。参见README.md与historical-initial/。最终六case保留了seek调用方法及两键B,B对A,B的真实证据，同时公开源码标签与本机自报hash不匹配，未宣称精确源码对应。
