# sRGB 工作域交接：固定来源与实际证据分层

读取日期 2026-11-01。对应[alpha 关联交接文章的新工作域小节](../../solutions/art2d/alpha-association-contract.md)与[独立 LittleCMS 数值夹具](../experiments/lcms-transfer-boundary/README.md)。不是现有 Pillow 字节域实验的重跑。

## 原始来源

- [SVG 2 固定 CR，2018-10-04，§13.9](https://www.w3.org/TR/2018/CR-SVG2-20181004/painting.html#ColorInterpolation)：区分 sRGB/linearRGB 操作空间，初始属性为 sRGB。用于避免把线性工作合同说成所有艺术流程的默认义务；没有浏览器验证。
- [CSS Color 4 固定 CRD，2024-02-13，§17](https://www.w3.org/TR/2024/CRD-css-color-4-20240213/#color-conversion-code)：明确为非规范性的 sRGB 转换示例，用于独立数学参考。该 dated 文档不是当前最新版声明，也不是 ICC 任意 profile 的数值保证。
- [PNG 第二版固定 Recommendation，2003-11-10，§4.2](https://www.w3.org/TR/2003/REC-PNG-20031110/#4Concepts.ColourSpaces)：历史格式背景中颜色 gamma 与 alpha 语义分离；本次没有 PNG 文件或 PNG 编解码。
- [Pillow ImageCms 官方文档](https://pillow.readthedocs.io/en/stable/reference/ImageCms.html#createprofile)，访问时页眉为 13.0.0：createProfile 只提供 LAB、XYZ、sRGB。其普通构造入口不是一个可直接宣称的 linear-sRGB 工作 profile。本次转而使用经审查的有限 LittleCMS C API，没有执行 Pillow ImageCms。
- [LittleCMS 作者网站](https://www.littlecms.com/color-engine/)指向官方仓库与 API 文档。GitHub 原始 tag `lcms2.19` 解析到 **b76633e60c8387a77268fb3359277ca25b5fd75c**；tag 日期未另行认证，版本名不证明安装来源。

## 固定实现定位与原创建议的分界

[头文件](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/include/lcms2.h)用于类型、结构、C API 签名和 RGB double 格式/intent/flag 定义。[cmsvirt.c 的 RGB profile 路径](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmsvirt.c#L101-L215)与[sRGB 构造](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmsvirt.c#L638-L682)说明源比较中的白点、原色与 TRC 关系。相同原色/白点不取消[内部 D50 适配](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmswtpnt.c#L252-L321)。

[输入 unpack](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmspack.c#L1402-L1450)、[输出 pack](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmspack.c#L3108-L3155)和[FloatXFORM](https://github.com/mm2/Little-CMS/blob/b76633e60c8387a77268fb3359277ca25b5fd75c/src/cmsxform.c#L258-L316)支持“double ABI 不等于全程 double”的限定。选择 relative intent、无 BPC、NOOPTIMIZE/NOCACHE 是本夹具固定设置；不是对所有项目的最佳参数建议。NOOPTIMIZE 之前仍可有简单预处理，不将它描述为绝无优化。

原创部分：不等通道输入、两种 alpha 条件、工作值关联检查、预先冻结的 1e-4 门槛、量化边界分析及团队交接表。数学参考由 Decimal 独立计算；实际输出来自记录的库调用。门槛不是从观察结果反推，也不是源码提供的全域误差界。

## 身份与未覆盖项

选定字节为 Pillow 包目录中的 `liblcms2-88eaba2f.so.2.0.19`，SHA256 `4cf9f69016c7804bcb4fa56f5bbc55640cb1b7196ac7b93ba29ed9df9bd9ff4d`；读取进程映射、版本及前后摘要以确认本次选择一致。系统另有不同的 liblcms2，未将其混作此结果。源码 tag、文件名和运行时自报都不认证安装构建来源；未审计全部加载依赖。

没有导入第三方图片或任意 ICC 文件，没有 GPU、显示、感知、HDR/广色域、过滤或性能测试。源文件/原始流/静态 checker 一致只支持可复查记录，不构成执行真实性签名。初次代码审查的合成假接受与修正保留，但从未运行有缺陷初稿的 CMM 目标子进程；不能把合成检查数写成颜色场景数。
