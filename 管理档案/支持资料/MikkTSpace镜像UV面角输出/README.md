# MikkTSpace 镜像UV观察：复现材料索引

完整接收和重索引方法见[正式文章](../../../GameLibrary/技术美术/环境管线/模型导入/接收MikkTSpace面角切线后，怎样重建顶点与索引.md)。本目录保留一个双三角形输入的历史材料，不承担另一篇技术方法正文。

## 输入、来源与复现入口

- [冻结协议](PROTOCOL.md)、[六输入清单](SOURCE-MANIFEST.json)。协议保留准备时的待执行文字，后来的结果另见下列记录，不回改历史。
- [原创夹具](fixture.c)、[预期记录](expected.json)、[离线消费器](validate.py)。这三份及协议的冻结字节保持不变。
- 固定作者 [mikktspace.c](https://raw.githubusercontent.com/mmikk/MikkTSpace/3e895b49d05ea07e4c2133156cfa94369e19e409/mikktspace.c) 与 [mikktspace.h](https://raw.githubusercontent.com/mmikk/MikkTSpace/3e895b49d05ea07e4c2133156cfa94369e19e409/mikktspace.h) 不随此包分发，须另取并核清单摘要，保留文件头许可。
- 具体构建、调用、诊断和时间限制见[固定历史复现说明](https://github.com/Container-R/GameLibrary/blob/ba9a11a2ffcb10bec72574c447f2246fdd746a71/管理档案/支持资料/MikkTSpace镜像UV面角输出/README.md#在新的目录复现不覆盖历史观察)。应使用新的目录与结果文件，不在归档原地执行或把旧PASS当作新结果。

SOURCE-MANIFEST 的 SHA256 仍为 `49ecb85282c057d78a4851074aee9f13c808f655bca0aed603cd925288bcd9a8`。同文件名不代表相同输入；本次整理没有重新冻结或执行这些输入。

## 观察、接受与真实修订

- [历史观察](observation.json)、[普通模式消费结果](validation.json)、[优化模式消费结果](validation-optimized.json)、[接受记录](ACCEPTANCE.json)。两种消费模式检查同一观察，不增加输入或生成调用。
- [独立原生复核](NATIVE-REVIEW.md)：两次同输入调用合计的依据与限度，不是两种几何情景或跨平台验证。公共目录不包含旧记录提及的两棵执行副本。
- [执行前审查与修正](PRE-REVIEW.md)、[合成检查脚本](synthetic-consumer-review.py)、[普通结果](synthetic-normal.json)及[优化结果](synthetic-optimized.json)：保留消费器曾因可替换预期而假通过的发现和修正；同14项合成情形的两个模式不是28个原生测试。

有限观察为六个面角T均+X、两面sign分别+1与−1。原样例的正反旧槽覆盖与六记录接收对照不增加生成调用，也不证明新版通用保守去重算法已经执行。glTF编码、导入器、GPU、图像、退化输入、四边形、变换和性能仍不在这项观察范围。

## 当前编辑清单与旧版本

[当前公共归档清单](ARCHIVE-MANIFEST.json)只为这次README改成材料索引更新展示身份：15个成员中仅README摘要改变，另14项保持原摘要。它不是新的输入清单或实验验收。

[旧完整README](https://github.com/Container-R/GameLibrary/blob/ba9a11a2ffcb10bec72574c447f2246fdd746a71/管理档案/支持资料/MikkTSpace镜像UV面角输出/README.md)与[旧归档清单](https://github.com/Container-R/GameLibrary/blob/ba9a11a2ffcb10bec72574c447f2246fdd746a71/管理档案/支持资料/MikkTSpace镜像UV面角输出/ARCHIVE-MANIFEST.json)按固定提交保留。旧读者审查绑定旧README，不批准现在的索引或新正式文章。新文使用本轮独立全文审查，本目录的原始结果和历史审查全部未改。
