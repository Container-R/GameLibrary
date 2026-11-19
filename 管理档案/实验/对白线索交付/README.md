# 对白线索交付：复现实验

[返回正文](../../../GameLibrary/叙事设计/运行时叙事/情境对白/对话选项为什么知道角色还没弄清的事.md)

两个小例都使用 Python 3 和原创车站数据，无外部依赖。未运行 Ink、商业游戏、实际对白或字幕/配音渲染。

- `check_knowledge_scope.py`：改变世界的站台而不改角色的记录，比较提示；用告示和转述、不同可操控角色及过时选项验证其归属。台词预览不泄露真相，站务员已知发生改动时，只能通过后续实际告知来交付新信息。
- `check_delivery_boundary.py`：预览、聚焦、排队后取消、旧播放回调、未启用渠道、错接收人、读档后旧队列均不交付；相同内容重开使用新实例，按本次演出及其标记、接收人检查实际字幕或声音，重复或存档后重放不再交付。这个存档策略故意舍掉队列，不模拟完整回放。

```sh
python3 -B check_knowledge_scope.py >/tmp/gl-knowledge-scope.json
cmp /tmp/gl-knowledge-scope.json observed.json
python3 -B check_delivery_boundary.py >/tmp/gl-delivery-boundary.json
cmp /tmp/gl-delivery-boundary.json delivery-observed.json
```
