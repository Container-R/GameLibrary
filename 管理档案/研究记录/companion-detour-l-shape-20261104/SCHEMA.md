# 最小消费者契约

状态：执行前数据契约，尚无消费者实现或原生观察。expected.json是唯一成功形状/字面oracle，不是已发生输出。

1. UTF-8单个JSON对象，允许结束换行但不允许第二份对象/非空尾随内容。拒绝重复键、NaN/Infinity、非有限数字和未知键。所有对象键集合、数组长度与顺序与expected精确一致；唯一例外是失败记录不走成功匹配，不可接受为pass。
2. protocol、commit、status、stage、completed、calls与四cases顺序精确匹配。整数处要求JSON integer且不允许bool冒充；几何、filter费用、t与normal处允许有限JSON int/float，数值精确匹配，排除bool。布尔、null、字符串类型不混淆。正常零允许负零数值等价。
3. expected中的`$P0`、`$P1`、`$P2`是文档占位符，绝不是原生输出。实际setup.refs须为三个非零、互异、仅ASCII十进制数字的规范字符串（无符号/空格/前导零）。分别绑定P0/P1/P2。所有链接ref、起终ref与path槽按该映射比对；`"0"`为唯一空槽/prevRef哨兵。拒绝未绑定引用或仅有标签。setup.refs_valid必须为true，且fixture已调用实际有效性检查；消费者本身不能再次验证库对象。
4. `$POSITIVE_INT`仅用于setup.data_size，实际为正JSON整数且不是bool。除此与三个引用占位符之外，无通配符。数据大小不预设ABI值，不能以宽泛“任意正数”替代其他setup断言。
5. links顺序按edge升序匹配expected；fixture记录真实链遍历结果，源码规定该顺序。各link的target索引、ref、edge、side、bmin/bmax全部匹配。任何额外link拒绝。header与实际顶点/polygon/neis亦须精确匹配，不只接受setup=true。
6. 三个raycast全部max_path3、精确SUCCESS状态与全部3槽：LC=[P0,P1,0]，CF=[P1,P2,0]，LF=[P0,0,0]。前两个t=有限数值3.4028234663852886e38，后者t=.5。no-hit hit_normal/hit_edge输出null表示不适用，不是原始值断言。受阻normal=[0,0,-1]、edge1。pathCost不在schema中，不添加无用断言。
7. findPath必须精确SUCCESS、count3、path[P0,P1,P2]；不能只核最后引用或success位。其对象没有raycast的t/options/normal等字段。calls精确为builder1/nav_init1/query_init1/raycast3/findPath1。
8. 建议纯合成反例：额外状态位、错t/Infinity、把wall hit当clear、路径缺尾/未知引用、计数或未写槽错误、错neis/link、错call count/顺序、重复键、bool代数、额外字段、缺行/多对象、错误源码commit、失败记录冒充pass。测试合成内容不构成实际库查询。
9. 失败JSON使用protocol/commit/status=fail/stage/completed/calls/setup/cases，加failure_detail及partial_setup_text。setup可null或已完成观察；cases仅已调用前缀；不会强塞成功schema。消费者不得以成功匹配通过失败结果；runner同时保留退出状态和原始stdout/stderr，解析失败也保留原文。
10. 消费结果必须标明consumer_only。没有原生启动记录、身份前后核验及整体成功receipt时，不能宣布本实验通过。执行记录中私有环境字段不进入公共观察JSON。
