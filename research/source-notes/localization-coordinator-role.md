# 本地化协调角色：来源定位

对应[ROLE-LOC-001](../../roles/localization/localization-coordinator.md)。访问2026-11-01，仅正文阅读。

| 来源 | 身份/日期与已读范围 |
|---|---|
| [Plarium官方访谈转载](https://company.plarium.com/en/articles/good-lockits-and-style-guides-save-time/) | Natalia Gladkaya，时任本地化部门负责人；官方页2021-11-22，注明原载InLingo。读取31–37、51–66、69–82、94–99；重点为指南维护、语境支持和接受边界。 |
| [PlatinumGames官方制作自述](https://www.platinumgames.com/official-blog/article/2188) | JP Kellams，2009-12-11；自述英语改编，不是协调员职位证明。读取7–12、18、24；选取语义沟通/批准接口。 |

行号为访问时文本视图，回查以问题和段落为准。两份英语资料来自具名实践者；发现包含日语查询，但没有据此声称拥有日语实质证据。Plarium是官方转载，不重复计为InLingo与Plarium两份独立研究。其历史工具、人员配置和机器翻译展望不作当前建议；标题的效率表述不是本库测量。

正文同文异境情境、locale接收状态和修订记录均为原创未执行建议。来源未公布这套字段、未报告本例缺陷，也未验证其效果。没有完整翻译、图像分析、游戏运行、真实译文审阅或LQA；既有ICU实验仍只支持自己的有限格式化范围。

## 2026-11-01 追加：Godot 特定的说明／消息身份示例

原有 Plarium 与 PlatinumGames 的阅读记录及从业者归属保持不变。此追加仅为角色正文提供一个具体接入机制，不把两篇实践者访谈改称该工具流程的证据，也不改变原文“未翻译、集成、运行界面或执行 LQA”的状态。

实际读取 Godot 官方 4.6 文档：[Localization using gettext](https://docs.godotengine.org/en/4.6/tutorials/i18n/localization_using_gettext.html)，Automatic generation、Extracting localizable strings、Using context；以及 [Translation](https://docs.godotengine.org/en/4.6/classes/class_translation.html) 的 Description 与 add/get_message。版本页面可变，未确认页面发布日期，不当作固定实现。

官方 `godotengine/godot` 的 `4.6-stable` 标签解析为 **`89cea143987d564363e15d207438530651d943ac`**，提交日期 **2026-01-25T12:41:41Z**。本次实际读取以下固定源码位置，不复制上游正文或代码：

| 文件及函数 | 阅读范围与用途 |
|---|---|
| [gdscript_translation_parser_plugin.cpp](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/modules/gdscript/editor/gdscript_translation_parser_plugin.cpp#L76-L140) `_is_constant_string`、`_parse_comment`、`_add_id_ctx_plural`；[同文件 `_assess_call`](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/modules/gdscript/editor/gdscript_translation_parser_plugin.cpp#L328-L356) | 76–140、328–356：说明独立于 context 保存；本例限常量单数调用。 |
| [template_generator.cpp](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/editor/translations/template_generator.cpp#L37-L123) `parse`、`generate`；[`_write_to_pot`](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/editor/translations/template_generator.cpp#L175-L213) | 37–123、175–213：按消息键归集说明与来源，写出注释和 `msgctxt` 的不同字段。 |
| [translation_loader_po.cpp](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/core/io/translation_loader_po.cpp#L140-L321) `load_translation` 文本分支 | 140–321：读取 context、有效非跳过消息传给 `add_message`；包含 fuzzy 跳过处理，不支持“所有注释都无作用”的概括。 |
| [translation.h](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/core/string/translation.h#L44-L61) `MessageKey`；[translation.cpp](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/core/string/translation.cpp#L145-L175) `add_message`、`get_message` | 44–61、145–175：context 与源消息共同构成键；查找结论限定默认实现，虚方法覆盖另论。 |

未检查全部解析器、GNU 合并算法、MO/CSV、动态提取、复数或完整语言域与回退链；也没有运行上述源码。两个同时存在的 Confirm 用途及其交接表是原创假设，不是实际翻译结果或引擎故障。它说明为何语言决定需要落实到调用、模板和语言条目的一致身份，不证明项目已经完成该接入。
