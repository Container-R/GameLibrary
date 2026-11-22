# 复现：MF2 译文分支验收

Node v24.22.3，依赖锁定到 messageformat 4.1.0。运行：

```sh
npm ci --ignore-scripts --no-audit --no-fund
node branch.mjs | diff -u observed.ndjson -
```

前九例对照选择器顺序、变体行序、全星兜底和运行时诊断；最后两例对照实际译文选中分支里的缺参，以及没有全星兜底时构造模板抛错。数据和分支标签是合成的，并非现有游戏文案。试验性日期函数只作为无选择能力的对照，未在其他 MF2 运行时验证诊断名称。

[返回正文](../../../GameLibrary/本地化与无障碍/本地化制作/数字与消息格式/译文保留了所有参数，为什么游戏仍选错提示.md)
