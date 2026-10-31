# Sprite交接的alpha表示：相同四通道不等于相同RGB含义

2026-10-31。原创1×1原始数值buffer，五组有限条件，共实际5次Pillow模式转换与6次alpha_composite。不是图像作品/用户图片编辑，没有生成PNG、渲染画面或显示。先冻结contract.md，再写run.py，原始预期无事后调整。

## 实际结果

|条件|实际字节或结果|
|---|---|
|RGBA(240,120,60,85)→RGBa|[80,40,20,85]|
|上述RGBa显式→RGBA|[240,120,60,85]，仅该特选可整除样例|
|正确straight over不透明黑|[80,40,20,255]|
|显式转换后同样composite|[80,40,20,255]|
|关联RGBa字节直接重标RGBA再composite|[27,13,7,255]，重复alpha加权|
|alpha255控制|关联转换不改变字节；over黑为[240,120,60,255]|
|alpha0控制|关联/反向转换后[0,0,0,0]，原隐藏RGB没有恢复；两条透明源over黑均[0,0,0,255]|

第三条错误路径不是API拒绝或坏文件：操作成功，但同样四个通道被赋予错误表示语义。它是一个可测交接反例，不是某个游戏已经发生黑边的报告。不能据此归因所有边缘问题，也不能断言预乘普遍优于straight。

数字oracle使用Fraction85/255=1/3，独立计算正确贡献240/3、120/3、60/3；误读则再次除3，采用最近整数政策得到27/13/7。没有复制Pillow的定点实现。这里是储存字节域运算；**未执行sRGB解码、线性光合成、ICC转换或显示测量**，不将这组值推荐为物理正确颜色流程。

## 复跑与证据

```
python3 run.py > run-output.txt 2> run-stderr.txt
```

当前exit0、stderr空。请复制run.py和contract.md到新目录再运行，不覆盖原档。results/summary.json记录每次操作的模式/输入/输出字节、Python/Pillow自报版本、解释器/Pillow入口/Image模块/原生_imaging文件SHA以及源码SHA。stdout含同一单个RESULT_JSON。先删除旧summary，拒绝-O，再导入Pillow；失败不写新的PASS，不是一般文件系统事务保证。

run.py SHA7895e68073e93b09eacbd86879baec1d3be6e5bc5be22df65a7307f925e6f74f；contract.md SHA17537214fca5580d77cea7175472028ac2b26c828be4c9325fde9a4397b773e2。运行Python3.12.14，Pillow自报13.0.0。没有图片二进制需要发布，全部实验数据为数值JSON/文本。

## 来源与身份

- Pillow13.0.0标签解析固定commit293218ad059d994baf1777d882911bed6a49704a；[Concepts](https://github.com/python-pillow/Pillow/blob/293218ad059d994baf1777d882911bed6a49704a/docs/handbook/concepts.rst)的RGBA/RGBa区分、[Convert.c](https://github.com/python-pillow/Pillow/blob/293218ad059d994baf1777d882911bed6a49704a/src/libImaging/Convert.c#L406-L435)和转换表、[AlphaComposite.c](https://github.com/python-pillow/Pillow/blob/293218ad059d994baf1777d882911bed6a49704a/src/libImaging/AlphaComposite.c)用于源码比较，不认证安装二进制来自该commit。
- [W3C Compositing Level1 dated2024-03-21 §5.1](https://www.w3.org/TR/2024/CRD-compositing-1-20240321/#simplealphacompositing)提供straight/associated source-over公式；这是Candidate Recommendation Draft版本，不声称最终Recommendation。
- [PNG第二版2003-11-10 §6.2](https://www.w3.org/TR/2003/REC-PNG-20031110/#6AlphaRepresentation)用于历史格式边界背景：文件颜色不预乘。**本实验不执行PNG，不验证任何PNG importer/exporter**，不能把工作buffer模式当成文件的隐藏blend配置。

全部来源读取2026-10-31。详细发现过程在同级art2d-gate/GATE.md，非实验依赖。没有下载/安装依赖、第三方美术或GPU调用。

## 界限与实际交接建议

原创建议：交付明确RGB关联方式、alpha、储存颜色编码、转换责任和消费者composite模式；不要从通道数、尺寸或字节长度推断含义。适当工作流需另验目标工具、颜色域及资产类型。与BC压缩预算不同，本例字节尺寸不变而语义改变。

alpha0展示隐藏RGB不可恢复；低alpha量化可能损失精度，但未声称所有值的误差界或测试完整8-bit空间。无filter/resize/mipmaps/atlas bleeding、DCC、GPU混合状态、引擎导入、视觉质量、感知或性能证据。独立复核待完成；当前仅作者有限实际结果。
