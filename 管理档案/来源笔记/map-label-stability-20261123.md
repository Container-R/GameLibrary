# 游戏地图标注布局：来源记录

访问日期：2026-11-23。

| 主张与正文位置 | 原始资料及定位 | 条件 |
| --- | --- | --- |
| 放置先后与绘制覆盖不是同一个顺序；同层符号可用排序键，文字可依次尝试替代锚点 | MapLibre，[Style Specification，symbol-sort-key](https://maplibre.org/maplibre-style-spec/layers/#symbol-sort-key) 与 [text-variable-anchor](https://maplibre.org/maplibre-style-spec/layers/#text-variable-anchor) | 规范按是否允许重叠描述不同作用；不外推跨样式层、图标与文字的所有策略。 |
| 旧锚点只是重试，当前位置仍参加本轮碰撞 | MapLibre GL JS v5.9.0，[placement.ts 571–617](https://github.com/maplibre/maplibre-gl-js/blob/v5.9.0/src/symbol/placement.ts#L571-L617)、[667–676](https://github.com/maplibre/maplibre-gl-js/blob/v5.9.0/src/symbol/placement.ts#L667-L676)；[pauseable_placement.ts 17–45](https://github.com/maplibre/maplibre-gl-js/blob/v5.9.0/src/style/pauseable_placement.ts#L17-L45) | 优先重试必须仍在候选列；不合格走当前候选，找不到可淡出。跨瓦片排序有条件；本文的业务优先级、稳定 ID 平局和无重叠是项目策略。 |
| 400×130 固定试件能分辨遮挡错误与换边 | [实验代码](../实验/游戏地图标注布局/place_labels.py) 及 [原始放置记录](../实验/游戏地图标注布局/observed.json) | 作者实现、三种策略；字形实测，路径是构造的，不是地图引擎或玩家研究。 |
