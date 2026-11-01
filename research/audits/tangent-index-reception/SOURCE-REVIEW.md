# 切线面角输出与重索引：独立来源及手推审查

2026-11-01。**接受以下精确稿件，无实质修改要求。** 本次独立重新读取固定原始来源，并完整读取最终说明及作者记录；审查者曾参与相邻切线变换主题，故不宣称完全没有主题历史接触。本审查未调用生成器或执行数值模型。

## 绑定的交付

- `note.md` SHA-256：`216eff076d5570c94433fcc0fdacdfe0605a779b9b4476fa8ba2c9d9eca9d937`。
- `AUTHOR.json` SHA-256：`fc75bfbce60cc40726e0b887ed80cff1bbfd914b4f868e3b71bb46ed328677af`。
- 拟发布位置：`research/source-notes/tangent-corner-output-and-reindexing.md`。

## 实际独立来源读取

1. MikkTSpace 固定 `3e895b49d05ea07e4c2133156cfa94369e19e409`：[头文件64–107](https://github.com/mmikk/MikkTSpace/blob/3e895b49d05ea07e4c2133156cfa94369e19e409/mikktspace.h#L64-L107)，[输出401–413](https://github.com/mmikk/MikkTSpace/blob/3e895b49d05ea07e4c2133156cfa94369e19e409/mikktspace.c#L401-L413)，[定向965–1007](https://github.com/mmikk/MikkTSpace/blob/3e895b49d05ea07e4c2133156cfa94369e19e409/mikktspace.c#L965-L1007)，[分组1144–1179](https://github.com/mmikk/MikkTSpace/blob/3e895b49d05ea07e4c2133156cfa94369e19e409/mikktspace.c#L1144-L1179)。接口区分面号/角点；输出不能未经检查按旧索引平均覆盖。普通非退化分支的UV定向区别与稿件一致，不借此证明整个算法。
2. Khronos glTF 固定 `59ecbdba704206bb656965ab4e202881806066f1`：[规范1800–1840](https://github.com/KhronosGroup/glTF/blob/59ecbdba704206bb656965ab4e202881806066f1/specification/2.0/Specification.adoc#L1800-L1840)。缺切线且有法线纹理的适用前提、符号与副切线关系正确；稿件没有把该条件扩成所有资产必须存切线或引擎行为认证。

## 原创手推与映射核对

- 几何边向量：F0 的 X×Y 为 +Z；F1 的 D×X 也为 +Z。两面UV行列式分别 +1、−1，几何绕序与UV定向没有混淆。
- 映射 `(u,v,0)` 与 `(u,−v,0)` 的导数分别给出相同 +X 切向、相反 Y 副切向。固定 N=+Z 后，w 分别 +1、−1。结论是理想参数化所需标架，不是实际回调字节。
- 六记录表保持 F0 的 O/X/Y 与 F1 的 O/D/X 角点次序；新索引 `(0,1,2)`、`(3,4,5)` 的位置及旧属性对应正确。旧0对应新0/3、旧1对应新1/5，体现一对多，而不是声称所有网格都需全展开。
- 接收程序明确允许旧索引作为输入读取方式，拒绝的是未经验证的输出共享。完整最终属性等价是再次合并的前提，w相同不是充分条件；其他属性和量化策略的未验证范围也被保留。

本稿不从推导预报像素、接缝或真实导出器缺陷，不把已有字节／变换证据移用为生成器执行证据。此次仅来源、数学及表格对应审查，无资产生成、渲染、运行归档读取或远端更改。

## 最终措辞修订闭合（2026-11-01）

**最终接受** `note.md` SHA-256 `76c1f632fed1b78f4dd70c19534d12c88f4aee2bacdeed3cc02aafd17de03da8` 与 `AUTHOR.json` SHA-256 `7946e204cd18093ad82fcf11d51ecd2f5806a7e01f0e70c39d04f987dfe07141`，取代上方初版交付绑定；初版审查历史保留。

独立读取修订句与作者记录，并作文本逆替换，恢复初版 SHA-256 `216eff076d5570c94433fcc0fdacdfe0605a779b9b4476fa8ba2c9d9eca9d937`。唯一正文变化将“限定于”改成“针对该情形，规定使用默认算法”，准确表达规范条款的适用前提，不暗示禁止其他情形生成切线。其余几何、六记录映射及执行边界未变，无新增实质问题。作者记录同步最终全文与正文哈希；其中 awaiting independent review 是提交时状态，本节记录最终接受状态。
