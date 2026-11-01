# 透明度与 PCM 支持入口：有限差异复核

## 结论

接受两项修改。结合 `research-drafts/reader-original-scope-checks/alpha-pcm.md` 已完整读取四篇正文的逐节去向核对，A1与P1关闭条件已满足；四个待整理任务可按已有覆盖与精确支持保留处置，两个旧范围允许登记 `accounted_for`，不需另建书。

## 实际差异与可读性

本次读取两份diff、CHANGES.json，并从batch12基线与候选独立生成差异。实际差异与所提供内容一致：

- 透明度仅在LittleCMS数值段后增加一段可选支持入口及空行。它明确说明浮点接近不保证舍入字节相同，同时限定有限反例不是全部转换的保证。接在相关例子之后自然，不把D50或内部精度实现塞进入门主线。
- PCM仅替换同一段中的“保留给独立文章处理”，改为精确旧资料支持章节。主体与另一个编码例内容不同、未证明随机进入/循环重入无缝的原限制均保留，不再造成还必须另写一本的虚假承诺。

计数、公式、原有引用、参考标题和返回尾注没有其他变化。新增文字是处置与导航说明，不新增实验结论。

## 链接及技术内容去向

以两本书各自canonical目录计算，四级相对路径分别解析到batch12实际存在的：

- `solutions/art2d/alpha-association-contract.md`，标题 **“double buffer 不代表全程 double，也不保证最终字节相同”**。片段标识与GitHub标题锚点规则一致。旧§6精度反例、相邻交接项及有限范围仍保留，未以摘要替换原技术内容。
- `solutions/music/pcm-loop-frame-contract.md`，标题 **“7. 编码补充：呈现帧数、最终 granule 与包时长不是同一数字”**。片段标识与标题规则一致。P/G/D/T、初始偏移条件和实际包计数的详细范围保留在同一节，不把未验证的循环重入改成已验证。

本次为文件与标题解析核对，不声称浏览器锚点点击测试；集成导航可在后续stage检查。旧支持正文已在前一报告完整读取，本次不重新宣称重开规范或复验整个历史技术链。

## 精确绑定

路径相对本报告所在目录，SHA256：

- `alpha.md`：`08c1fc0cbbceca25c5142807e7340029cbd6a10a86f4007c5c7cdcb900a8860b`
- `pcm.md`：`b0c04989de758a6f3679c92c7cd1661552249e32ae2dcd27d216fd20cac8fbe9`
- `alpha.diff`：`1c38118548d3e3a48f9ca27ee7f8038178d7b7e2caa6544391c155ab7f4078f1`
- `pcm.diff`：`84f6d9752f70c30cd8e8d8aabe3ac154c5c20aa60e96beda3feb5b0d386ced2e`
- `CHANGES.json`：`14744e5d729f4fc7d45a6eb4fc78fb5cda154d60706f6e607136bd1260dfddce`
- 前报告 `research-drafts/reader-original-scope-checks/alpha-pcm.md`：`ddc9623d5259c8403ae32090aca7424afedd1510f4b5f3da49f0d13930c2199e`，其中保留基线四篇与管理目录身份。

这是代理独立有限编辑复核，不是真人测试。未读raw、执行附件或运行模型，未改正文、stage或远端。范围结清不等于全部颜色/编码主题完成，也不授权删除支持资料或继承运行保证。
