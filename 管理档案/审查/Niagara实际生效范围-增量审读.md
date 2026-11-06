# Niagara实际生效范围：存量文章增补审查

审查日期：2026-11-06。基线：960c445be0268d0e255ca3b71757d847439dee70。对象为《拆分测量Niagara实例与模拟和像素成本》的范围诊断增补，不新增图书。

独立读者视角审读确认有实质增量：既有正文已说明完整生命周期与范围成本，新段落补入 UE5.6 的模式条件、资产与实例设置区别，以及只改变固定盒范围的原创对照。原有成本测量、分位数和视觉要求仍保留。

## 独立来源核对

重新读取 Epic UE5.6 NiagaraEmitterCalculateBoundMode、VersionedNiagaraEmitterData、NiagaraComponent、NiagaraSystemVisibilityCullingSettings 与 Niagara Debugger 文本。核对 CPU-only Dynamic、系统固定范围对 emitter 属性的忽略、实例局部空间盒、固定范围 getter 的无效返回边界、预剔除与渲染反馈区别，以及 HUD 的 scalability 原因范围。

根据审读补上发射器实例固定范围检查，CPU Dynamic 对照前同时排除系统与发射器实例固定覆盖。没有从不同作用域的 setter 描述推导完整优先级表。镜头动作明确为移动镜头而非同时移动发射器，并补上启用 Debug HUD 的步骤。

## 实际阅读路线

固定基线的根 README → GameLibrary/README → 视觉特效 → 特效制作 → 性能分析 → 正文逐页可达，保存基线与远端正文相同。本次书架另加问题式章节入口，保留全书入口。

## 结论范围

接受上述修订后的有限增补。CPU 烟雾喷流 A/B 是未执行安排，不是缺陷复现；结果若改善，仅支持范围参与问题，不能排除其他因素。没有运行 Unreal、Python API、GPU 对照、帧时间采集或真人测试，也没有检查来源截图。未复制第三方图像或长段源码，不扩大为其他版本或全库质量保证。
