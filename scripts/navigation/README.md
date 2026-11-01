# 旧路线的维护草稿生成器

读者入口已经改为[中文书库](../../GameLibrary/README.md)。本工具仅将[旧路线注册表](../../taxonomy/reading-routes.json)中的关系生成维护草稿，不再生成根目录阅读页，也不代表现行分类或文章通过编辑验收。

`管理档案/图书目录.json` 是现行规范书目；本工具不重新生成、不修改该文件。旧角色、方案等目录仍作为本工具输入，生成结果只供维护者查旧关系，不应直接发布成另一套书架。

## 用法

在仓库根目录运行，先创建专用草稿目录：

```sh
mkdir -p 管理档案/草稿
python3 scripts/navigation/build_routes.py . --registry taxonomy/reading-routes.json --output 管理档案/草稿/旧路线候选.md
python3 scripts/navigation/build_routes.py . --registry taxonomy/reading-routes.json --output 管理档案/草稿/旧路线候选.md --check
python3 scripts/navigation/test_routes.py
```

- 输出仅允许位于指定仓库的 `管理档案/草稿/` 内，且扩展名必须为 `.md`。可使用其下级目录，链接会按输出文件所在目录重新计算并编码。
- 根 `README.md`、`DISCOVERY.md`、`CATALOG.md` 均受保护；写入和 `--check` 都拒绝，不会因旧生成结果碰巧相同而报告通过。其他书库、规范书目和根预览路径同样不允许输出。
- 已有符号链接按解析后的目标检查；不能经草稿文件或草稿目录的链接覆盖读者入口或跳出草稿范围。这是本地维护防误写检查，不是针对恶意并发更换链接的安全边界。
- `--check` 只比较当前草稿与生成文本：一致退出 0，缺失或不同退出 1；输入、路径或解析错误退出 2。输出父目录须预先存在。完整校验后才写临时文件并替换，不承诺断电持久性或并发发布协调。

## 原解析范围不变

仍从 `roles`、`knowledge`、`solutions`、`case-studies`、`comparisons` 读取有限 frontmatter，通过稳定 ID 解析目标。必需字段为 `id,title,type,status,primary_discipline`，限定单行标量而非完整 YAML；缺失／重复 ID、未知状态、未完成目标及非法注册字段报错。其他 YAML 字段不作完整验证。保留文本转义、路径编码和确定顺序；旧证据状态不因路线存在而升级。

## 检查与历史

本次有限测试为 16 个方法：11 个既有方法保留并将成功输出改到草稿路径，另加 5 个方法覆盖保护路径、规范书目拒绝、嵌套相对链接与缺失／陈旧检查、文件及目录符号链接误写防护。测试只使用临时合成目录，不重生成全库目录。

此前根目录生成方式与旧审查保留在版本历史及[旧路线审查档案](../../research/audits/reading-routes/REVIEW.md)，其中旧 `--check` 结论不等于新读者导航验收。通过这些回归测试也不证明真人寻路、全学科分类或文章可读性。
