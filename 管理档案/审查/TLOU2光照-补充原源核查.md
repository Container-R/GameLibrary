# 《最后生还者第二部》光照案例的补充原源核查

审查日期：2026-11-02。对象为当前读者文章《最后生还者第二部如何结合顶点与探针照明》，正文 SHA256 为 `a3983eb9fe61014015940066a11e18f6b83384d286c86d25430fbd5ad4c69dd3`。

独立审查完整读取现有文章；对照原作者 SIGGRAPH 2020 两页论文，以及讲义第 2–5、15–20、48–51 页及相应已列说明中的关键段落。主编另读两页论文文字、第 3、5、15–20、48–50 页文字和第 5、49、50 页备注，并实际查看第 50 页 Hybrid、Vertex、Probe 三张原图。不是整份讲义通读，也没有运行游戏或重建演示场景。

核查重点是混合表示的职责：静态背景中的顶点数据保存主要亮度信息，探针贡献色彩与方向相关信息，不能压缩成单个颜色混合公式；方向提取和法线相关处理仍有作用。动态前景仅用探针是原案例的范围限定，不应把静态背景方法推广到所有对象。八个包围盒角探针、逐像素三线性插值以及旧方法每对象采样的区别，与现文解释一致。

卡车比较图用了比游戏常见阴天场景更强的色彩差异。图示支持作者对表示误差的讨论，不是本库的新性能测量、图像质量认证或运行成本证据。未发现必须修改现文的核心冲突；现有工程试验建议仍是建议，不改写成已执行结论。

## 原始来源

- Naughty Dog，2020，[*Lighting Technology of The Last of Us Part II* 讲义](https://s3.amazonaws.com/nd.images/research/2020_siggraph/LightingTechTlou2.pptx)，上述页段与备注。原文件 SHA256：`f2ceec1821ef3855f87b2a6532cf9a11bfc4abd8a0814eb81d567004cb04b283`。
- SIGGRAPH 2020，[*Lighting Technology of The Last of Us Part II* 两页论文](https://history.siggraph.org/wp-content/uploads/2022/08/2020-Talks-Doghramachi_Lighting-Technology-of-The-Last-of-Us-Part-II.pdf)。原文件 SHA256：`9ee9ccd8b722384f80178e30e1d0aa2f51acc8fc718177cc1d860f2333d9215d`。

只归档本次核查结论，不重新发布整份论文、讲义或原图。
