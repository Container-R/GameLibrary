# 独立工具的历史身份与当前复查入口

这里的README及两份清单保留原字节。README开篇“尚未消费”是准备时态，后来的真实离线消费见[INDEPENDENT-REVIEW](INDEPENDENT-REVIEW.md)，包括其第二操作者字节绑定追加；本说明不修改受清单绑定的README。

INPUT-SHA256.json绑定当前四输入。根SHA256.json是旧代清单，适用pre-adaptation中的对应六文件，不应拿它核当前已修checker；该旧目录也保留原清单。旧17项数值/JSON测试和旧6项stream测试属于旧工具，新6项属于布尔close结果修订后的工具；没有声称重新运行17项。

实际技术流现统一位于[observations.jsonl](../numeric/observations.jsonl)，主/独立两轮原字节相等，故只存一份；两份result分别保留。离线命令可在本目录按README使用 `python3 -B check_numeric.py ../numeric/observations.jsonl`，只消费文件而不加载音频库。不要把执行此命令与运行numeric/runner.py混淆，后者会实际渲染。此包整合阶段没有再执行任一命令。

INDEPENDENT-REVIEW里的原run名指历史来源，不是要求附整个运行目录；原始输出在上述唯一文件，回执见[主轮](../numeric/run-author-1/result.json)和[独立轮](../numeric/run-review-1/result.json)。INDEPENDENT-EXIT未复制；实际离线退出0由已审报告记述，不伪造一个新外部回执。

返回[包说明](../README.md)。
