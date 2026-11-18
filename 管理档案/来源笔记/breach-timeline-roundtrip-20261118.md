# 技能时间轴迁移：参考和验证范围

- Sean Boocock（QC Games），2019-01-10，[Unlocking Breach’s combat with Unreal Engine](https://www.unrealengine.com/tech-blog/unlocking-breach-s-combat-with-unreal-engine?lang=en-US)。A Gameline For All Seasons 写到 Unreal Slate 的拖动、重定时和预览，以及预测开始与服务端拒绝后的校正；Asking the Right Questions 写到条件选择任务集合；Feel the Burn 写到原生数值函数、范围效果和即时效果。未说明跨引擎迁移格式、成本或工程实测。
- Daniel Lema，[Making combat visually authorable](https://mindstudios.dev/ufe/case-studies/authoring-system/)。Implemented 段说明已交付 Unity 商业编辑器有碰撞轨道、帧控制及动画预览；后续 Fighter Studio 是单独原型，效率与错误率均为建议测量，不是实际对比。
- [本地 Node.js 合成试件](../实验/技能时间轴往返/README.md)验证有限 JSON 往返。地面原 6/6，改后 7/8，空中仍 8/8。向下取整改为 7/7；同名但实现错误得到 18；两个基准上下文应为 14、19；删除规则或未绑定资源键拒绝。没有实际资产或两个引擎参与。
