# 本地化配音与过场时间轴：来源

| 主张 | 一手资料与定位 | 边界 |
| --- | --- | --- |
| 同段本地化演出由多个不同长度的片段驱动，允许个别语言校订 | Piotr Tomsinski（CD PROJEKT RED），[Behind the Scenes of Cinematic Dialogues in The Witcher 3: Wild Hunt](https://media.gdcvault.com/gdc2016/Presentations/Piotr_Tomsinski_Behind_the_scenes.pdf#page=142)，GDC 2016，物理页 139–147。第 140–145 页标同段 EN 12 秒、FR 14 秒；142 双条时间轴首条都写 2.19 秒，后续分段有差异，并画出镜头、动画、视线轨。146 涉及重写、补录等引起时长变化；147 允许按语言修正。已查看原稿对应页。 | 印刷标签，不是对演示成片独立逐帧测量；不重印原图、不声称逐语言口型质量，亦不推断全部镜头、道具接触或玩法锚点的行为。 |
| 编辑器估算和导入实长不同；不同事件可按片段而非整个过场安排 | CD PROJEKT RED，[The Witcher 3 REDkit: HOW-TO: Create a scene](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/28770374)，Creating dialogues 的 Approve local VO 步骤后，动画、特效、视线可按 section 百分比，真实音频更新原本估计；[Work with lipsync](https://cdprojektred.atlassian.net/wiki/spaces/W3REDkit/pages/6326845/)，加载提供给该语言的口型和音频。 | REDkit 制作文档不替别的引擎规定实现；图中的固定锚属于本文合成例。 |
| 自由时长、限长、严格总长和画面口型是分开的录制要求 | Side，[Optimizing the Audio Localization Process For Games](https://side.inc/lab/better-loc-next-time-optimizing-the-audio-loc-process)，2023，Types of VO lines、Script formatting。 | 某个典型容差不是行业上限，也不是作品的默认参数。 |
| 在已标出可让时间的片段后，限定预算的单段调度仍可能溢出 | 本文 Node 固定合成输入、运行 JSON 和按同一标线绘制的对照图。 | 比较片段占用与最低等待，不是实际播放、引擎精度或语音可懂度测试。 |

调阅日期：2026-11-22。
