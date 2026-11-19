# 手工地形分块验收：来源与范围

核读日期：2026-11-19 UTC。

## 开发者公开资料

Jeff Lydell，80.lv，2017-09-15，The Creation of Homeworld: Deserts of Kharak，Level Creation。
https://80.lv/articles/the-creation-of-homeworld-deserts-of-kharak
支持简单布局试玩、概念覆盖、手工高模、Chunker分块及布景光照的制作分工。没有给出Chunker实现或性能测量。

BBI团队，Fists of Heaven，A Deserts of Kharak Round Table: Part 2，手工地图问答中Yggy King和Mike Kuzel的回答。
https://www.fistsofheaven.com/deserts-of-kharak-blackbird-round-table-interview-part2/
支持该项目原型用Unity Terrain、团队当时对沙脊效果的判断，以及极端缩放的制作约束；不推出高度图的一般能力上限。

Yossarian King，GDC2017，The Great Divide: Unique Visuals and Deterministic Gameplay in Homeworld: Deserts of Kharak。
https://media.gdcvault.com/gdc2017/Presentations/King_Yossarian_TheGreatDivide.pdf
第12—14页展示远方平面、外围渐变细节与分块游玩区；第40—46页展示二维规则高度、脊线与射击遮挡。读取相关页文字，实际渲染查看第14、44页。不从示意图推测碰撞、导航或分块算法。没有观看演讲视频，未转载原图。

## 本文新增方法和执行

剖面、投影、偏差指标、射击区间与高度阈值都是原创教学构造。实际运行Python及matplotlib生成六面板PNG和数值JSON；作者查看图片。40/10像素每米为正交缩放，不是实际游戏透视相机参数。脚本对峰位与接缝值断言，对规则脊线交叉结果断言；高度反例是单点阈值比较。材料见[实验说明](../实验/地形分块边界/README.md)。

没有三维地形、遮挡、法线、材质、真实LOD、引擎性能或人眼阈值测试。生产验收步骤为作者建议，不归给BBI。来源原图与下载讲义不随本次文章再分发。
