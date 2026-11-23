# 游戏地图标注布局：复现材料

测试环境：Python 3.12、Pillow 13.0.0、FreeType 2.14.3、RAQM 0.11.0、Noto Sans CJK SC Regular 18 px（TTC 的第 2 号字面，从 0 起）。不附字体文件；使用系统安装的 Noto Sans CJK 或用参数提供路径与字面索引。

```sh
python3 place_labels.py --font /usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc --index 2 --out ./repro
```

读取原始 [放置记录](observed.json) 与 [实验画面](comparison.png)。运行使用 400×130 像素视口，整框碰撞尺寸为 28 px 高，字形包围盒和排版推进取能覆盖的一侧来计算宽度，再加左右 6 px 内边距。样本「当前任务：北门」外框 138 px、「West Watchtower」158 px、「Porte des Étoiles」151 px。对照图不代表识别率或产品美术验收。

- A0 中任务未激活；A1、A2 激活后，比对上帧可见优先与本帧类别优先，任务为 0/2 对 2/2。
- B0–B3 两侧都合法，比较每帧按图标过中心线选边与保留合法旧锚点，目标标签换边为 3 对 0。
- B4 检查旧右锚点超界后改用左侧；B5 离开视口，不保留占位；B6 重新进入时重新选出右侧。另有变更候选集合和输入数据逆序的断言。布局循环逐帧重建占用；脚本逐帧断言保留标签均在视口内且两两不重叠。

试件只做单行左右锚点和所列轨迹；不模拟 MapLibre，在阿拉伯文、回退字体、旋转或控制器操作路径上的可读性需另测。

[返回正文](../../../GameLibrary/界面与体验/界面编程/画布与布局/游戏地图缩放中的任务标注优先级与锚点.md)
