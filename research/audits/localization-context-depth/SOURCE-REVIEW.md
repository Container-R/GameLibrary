# 独立来源核对：译者说明与查找 context

2026-11-01。**接受作为 ROLE-LOC-001 的窄深化**，不需要新岗位或运行实验。已读原角色全文及本次 gate（70b9ee608b5daa6b2e05dbb43653893207c3abf0766b6dea180218e8cc58d1a0）、源码补充（d7e415167c79fd6112c1efb4c266d07bfcdf2244395570aa91b882187788993e）。新增价值是把原“同文异境”责任落实到解释资料与消息身份的不同交付物，而非重复要求提供语境。

## 实际核对的官方链路

独立查询官方 tag `4.6-stable`，指向 `89cea143987d564363e15d207438530651d943ac`。以下均为该不可变源码；文档为可变的4.6系列页面，未确认页面发布日期。

- [GDScript 提取器](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/modules/gdscript/editor/gdscript_translation_parser_plugin.cpp#L81-L139)：说明与 id/context 分槽；`_assess_call` 328–356 核对常量字符串实参，不能以动态表达式运行时存在代替可提取前提。`NO_TRANSLATE` 另有跳过作用。
- [模板生成器](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/editor/translations/template_generator.cpp#L37-L99)：85–96以 context、id 建键，说明另存集合。102–123选择 POT 写出；175–213分别写说明注释与非空 `msgctxt`。因此本题的两条不同说明本身不拆分消息键。
- [文本 PO 加载](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/core/io/translation_loader_po.cpp#L182-L265)：context 状态、单数 `add_message` 与跳过条件；290–321核对累积及最后条目提交。不能概括“所有注释均无行为影响”：260–265还检查含 fuzzy 的注释。仅讨论有效、未被跳过的普通单数条目。
- [Translation 默认实现](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/core/string/translation.cpp#L145-L175)及[键定义](https://github.com/godotengine/godot/blob/89cea143987d564363e15d207438530651d943ac/core/string/translation.h#L44-L61)：添加与默认查找使用同一二元键；相等比较同时包含两项。查找先允许虚方法覆盖，不推广到任意自定义资源。

另独立读[Translation contexts](https://docs.godotengine.org/en/4.6/tutorials/i18n/internationalizing_games.html#translation-contexts)、[gettext 提取与 context](https://docs.godotengine.org/en/4.6/tutorials/i18n/localization_using_gettext.html#extracting-localizable-strings-from-gdscript-files)及[Translation 描述](https://docs.godotengine.org/en/4.6/classes/class_translation.html#description)。所读文档与上述窄机制一致。

## 接收条件与限制

Confirm 两用途是原创、未执行例子；先由语言侧判断是否需不同译文，再核对调用 context、模板身份和交付条目的一致性。不同用途不自动要求拆键；相同说明也不强制共享键。可以说本默认链路不以说明差异建立不同查找身份，不能声称实际导出、加载或界面显示已验证。

没有审计 Object.tr 到语言/域选择的完整链路、缺失项回退、译文迁移、GNU 合并、复数、MO、CSV或自定义插件。POT 的空译文字段不是已完成译文。此来源阅读不升级原角色的翻译、集成或 LQA 证据，不改写其历史实践样本。保留原有阅读记录，以新增日期/范围说明此次扩展。未运行引擎、提取器、gettext或任何测试；无运行环境元数据。
