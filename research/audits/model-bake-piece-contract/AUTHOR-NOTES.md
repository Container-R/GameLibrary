# 作者说明：模型烘焙 piece 可见集合

2026-11-01。拟发布路径：`research/source-notes/model-bake-piece-visibility.md`。只新增短来源笔记，元数据 ID 为 `NOTE-MODEL-BAKE-001`、type 为 research、status 为 source-backed；不创建角色档案，不增加 solutions/roles/case-studies 的目录条目数。分类使用现有 MODEL、TA、ANIM；没有建立不存在的通用 ART 学科。

## 来源与阅读

SideFX 官方 https://www.sidefx.com/docs/houdini/nodes/cop/bakegeometrytextures-2.0 。实际读取 Basic workflow、Mesh types、Baking best practices、Ray Setup、Cage Attributes、Geometry Setup、Match Pieces by Name，并定点读 Ambient Occlusion。决定性定位为正文文本92–93、243–269；cage 独立条件为76–81、117–123。行号来自当次网页文本，章节名优先。

页头 Houdini22.0、节点2.0、Since21.0 分开记录；访问2026-11-01，未确认发布日期/修改日期，没有固定源提交或安装版本认证。没有查看图片或视频。正文将来源事实集中为一小段；本说明只给定位，不重复其机制摘要。主研究也直接读取原始正文，见同目录 `MAIN-SOURCE-READ.md`。

## 原创部分与限制

箱体/锁扣、A/B 分组、候选射线准入推论、一一对应改名对照及五步接收程序均为原创未执行分析，不归因于 SideFX 生产案例。准入规则不同不证明最终命中、像素差异或缺陷；保持分组不证明逐像素一致。Include/Exclude 不被包装成任意逐对过滤，cage 对应不被名字检查替代。

两篇相关来源笔记已全文读取：`tangent-handedness-normal-transform.md` SHA-256 `59b3b75a5c7f8a50fb24fe09293c69ea7ef50ce925e6bde0f69f740350e19615`；`mesh-simplification-request-result.md` SHA-256 `edd71b9565b0f5697bd23284c3f4c2fdfcc4ccc132f31e3fb4c64a05712514e5`。这些是当次有界排重的输入身份，不继承运行证据。相对链接按最终 source-notes 同目录编写。没有生成资产、调用烘焙器、检查执行环境或添加图像。

## 最终身份

`note.md` 全文件 SHA-256：`caf10624424444810788fe4b8a8cf84658967a3c8612d522eda2095615fe669d`。去除 YAML frontmatter 与其后空行的正文 UTF-8 SHA-256：`4c93e692fa5b7b52b7f5205ccb8c1a7105682f12fa62f779b371e792bc65a440`。元数据只表达 source-only 范围，未升级证据等级。
