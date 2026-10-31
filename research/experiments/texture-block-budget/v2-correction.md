# Texture runner v2：独立偏移验收与导入前失效化

2026-10-31。此目录是新增修正源与结果；`../texture-block-budget/` 原始源码、结果、文章草稿与第一次独立审查均未改写。此前负向审查证据保存在 `../texture-runner-negative/`。

## 原版确实存在什么问题

1. 原runner先import Pillow/model再删除旧summary。若依赖或model导入失败，旧PASS仍留存；不是本次重新生成PASS，但消费者若忽略进程失败容易误读旧文件。
2. 原runner验证尺寸/字节数，却没有验证数值表的 `payload_offset`。将模型改成 `offset - 127` 的合成突变体能通过作者runner；独立原始证据checker会拒绝。固定DDS本身偏移和实际解码正确，不代表作者runner对所有输出字段覆盖充分。

## 两处修正与范围

- `ROOT/OUT`准备和旧summary删除以及`-O`拒绝，移到非stdlib Pillow/model导入之前。对标准库导入、权限失败或进程任意时刻终止，不宣称普适原子报告协议。
- 每个数值案例用**独立字面期望表**中的块数×格式块bytes累计期望offset；检查每一级模型返回的payload_offset。没有用模型返回size来推导自身offset的期望值。另对返回的blocks_x/blocks_y使用独立期望逻辑尺寸的ceil/4核对，避免只验证总size而遗漏输出字段；不声称通用schema健壮性。

模型本身未改；仍仅14个数值案例、6个输入拒绝、6个真实Pillow单mip wrapper解码、1个截断拒绝。并非新增GPU或BC7解码证据。完整公式、来源和格式边界参见原版实验说明；发布时整合者应保留原版为明确历史而非把v1结果配给v2源码。

## 实际最终运行

```sh
python research-drafts/texture-runner-v2/run.py > research-drafts/texture-runner-v2/run-output.txt 2> research-drafts/texture-runner-v2/run-stderr.txt
```

实际退出0，完整有限fixture PASS。Pillow的getdata弃用警告仍保存于stderr。`results/summary.json`记录此次新runner SHA、实际版本及模块hash；base64与二进制制品保留。DDS仍为1792bytes，SHA `1e8f263dbf5aafe04b26626ba7b17ef9ec455337d2f8fed3ddcdbcf145e2f20f`；内容未因runner验收增强而改变。

冻结源码：
- model.py `cea6af8ac132485f7492ee60ab1019daaf9f690257bafc62d989fcfdc5697544`
- run.py `1ca81455b9ef0605a01b7dbfff15454a3294c16bfe335e5f964919ba251b7cef`

最初只含offset修正的17fe版本及实际PASS保存在historical-offset-only；增加每轴块数字段检查后重新全量执行，当前结果对应1ca81455版本。只读checker的拒绝不会删除其输入summary，这不是重新发布PASS，与runner生成结果的清理职责不同。

最终1ca81455源码的独立完整复跑及原始证据oracle已通过；12项有限负向检查均按预期拒绝，7项runner拒绝均清除旧summary（包括依赖/model导入失败及offset、blocks_x/y突变）。只读checker不负责删除输入。审查记录在 `../deep-qa/texture-runner-v2-final/REVIEW.md`，负向日志在 `../texture-runner-negative-v2-final/`；不是GPU验证或通用fuzzing。

Public layout: current files are v2, historical-v1 retains original evidence; negative-v1/negative-v2 and review/ contain selected raw records. Historical draft directory names above describe actual execution locations. Redundant offset-only intermediate is retained locally but not included in this public selection.
