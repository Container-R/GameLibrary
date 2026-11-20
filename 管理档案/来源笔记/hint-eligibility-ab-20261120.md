# 新手帮助卡随机试验：来源与比较口径

- Microsoft Experimentation Platform, [Patterns of Trustworthy Experimentation: Pre-Experiment Stage](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-pre-experiment-stage/)，Set Up Counterfactual Logging。Bing 天气答案的原始团队材料说明，对照中也标记某次请求如果进入处理变体会显示天气答案。本文只借用对称记录，不把效果外推到游戏提示。
- [Patterns of Trustworthy Experimentation: Post-Experiment Stage](https://www.microsoft.com/en-us/research/articles/patterns-of-trustworthy-experimentation-post-experiment-stage/)，触发分析、SRM、补集检查及总体尺度的差别。资格组样本数和补集近似 A/A 是诊断，不证明两边同质。单人二元完成率的分层加权不是事件比值的一般公式。
- [构造试件](../实验/新手提示的共同资格/README.md) 实跑。首例 A/B 全量 830/1000 对 855/1000，资格 20/100 对 45/100，A 全量与 B 真实展示的误差值 −26.75 个百分点；A 资格与 B 真实展示也不对称，+36.25。晚触发例的每组触发人数完全相同，但触发组 +60、补集 −60、总体 0。二例均为合成算术反例，不报告任何真实试验效果或置信区间。
- 观测输出 SHA256：`19858b130ff6261eab15a2ff41341adcfd2d7f4947a6b6bcacc83991c11c41bd`。
