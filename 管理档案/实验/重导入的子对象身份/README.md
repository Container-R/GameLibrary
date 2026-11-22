# 子对象身份与引用：Blender 原生导出及 Node 对照

[正文](../../../GameLibrary/引擎与工具/资产工具/资产标识与引用/资产重导入后，怎样防止引用悄悄接错子对象.md)

```sh
blender -b -t 1 --python-exit-code 11 --python blender_probe.py -- /tmp/asset-subobject-repro
cmp /tmp/asset-subobject-repro/blender.observed.json blender.observed.json
node reimport.js
```

- [Blender 脚本](blender_probe.py) 和 [实测数组](blender.observed.json)：Blender 4.3.2，真实生成三个原始三角片的材质，再对原文件对象进行改色、改名、重排、删除和同名新建。开启自定义属性导出时核实际 glTF 材质 `extras`；关掉的对照无该字段。命令写入指定输出目录，不改已有 Blender 项目。旧版与新版都是 GLTF_SEPARATE，而不是旧的内联编码选项。
- [Node 对照](reimport.js) 读取并检查 Blender 实测数组，与同一合成试件的语义用途配对。[输出](reimport.observed.json) 分别列每个旧引用按索引、名字、稳定 ID 和模拟内容键所得的结果；在缺少 ID、副本身份冲突、退役 ID 重用和重复键时主动拒绝。内容键使用试件输入字符串，不是对 Blender 材质做二进制哈希。这个对照没有运行 Unity 或内置 FBX，也不模拟第三方导入器、存盘或项目迁移。
