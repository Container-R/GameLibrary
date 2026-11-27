# 复合绑定组回归对照

- [正式正文及 Unity C# 场景试件](../../../GameLibrary/玩法程序/玩法系统/输入接入/Unity%202022.3%20要用新版%20Input%20System%20的修复，能只移植输入包吗？.md)。
- [check_groups.py](check_groups.py) 是一个不依赖 Unity 的组选择模型，只检查哪条根或普通绑定被选中，不做显示字符串、绑定解析、设备、动作或构建验证。

运行：`python3 check_groups.py`。实际输出：

```text
Keyboard: old=['Jump']; new=['Move root', 'Jump']
Pad: old=[]; new=['Pad root', 'Move root']
Other: old=[]; new=[]
```

输入中两个复合根相邻，只有后一个根的部件有 Keyboard 组。如果扫描不在下一条非部件处停止，前一个根也会误入 Keyboard；Other 为空排除无条件放行。Pad 此处应选中两个根，而不是从根内抽出独立子键作为结果。保留普通 Jump 绑定，排除把所有非复合绑定跳过的实现。

Unity 实测仍需执行正文的未改基线、最小补丁和回退检查；这里没有运行 Editor、Player 或真实设备。
