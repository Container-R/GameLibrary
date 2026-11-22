# 子对象身份与引用：来源

| 主张 | 一手资料及位置 | 适用边界 |
| --- | --- | --- |
| 自定义导入器在同一文件内提供可再生成的唯一匹配键 | Unity 6000.0，[AssetImportContext.AddObjectToAsset](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityeditor/assetimporters/assetimportcontext/addobjecttoasset)，两个重载及 Remarks。 | 官方要求同资产内确定性；不公开 identifier 到 fileID 算法，不给同名 FBX 子对象作稳定承诺。 |
| 序列化引用由文件 GUID 与文件内 local ID 构成 | Unity 6000.0，[TryGetGUIDAndLocalFileIdentifier](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityeditor/assetdatabase/trygetguidandlocalfileidentifier) 三个当前重载，[Direct reference asset management: Unity object references](https://docs.unity.com/en-us/engine/6000.0/manual/assets-and-media/assets-managing-runtime/assets-direct-reference#unity-object-references)。 | 输出 GUID 为字符串，localId 为 C# long，过时的是 int 输出。内存 instance ID 不是持久键。下游 JSON 如用 JavaScript Number 可能损精度。 |
| glTF 下标连接当前文件，不要求 name 唯一；extras 用于应用字段 | Khronos，[glTF 2.0 §3.3 Indices and Names](https://registry.khronos.org/glTF/specs/2.0/glTF-2.0.html#indices-and-names)、§5.16 Extras。 | extras 的生命期和下游保留由项目约定，不是 glTF 标准的持久 ID 或自动迁移机制。 |
| Blender 导出时可选传出多数对象的自定义属性 | [glTF-Blender-IO，Blender 4.3 发布分支的导出器文档源](https://github.com/KhronosGroup/glTF-Blender-IO/blob/blender-v4.3-release/docs/blender_docs/scene_gltf2.rst)，Custom Properties。 | 此处原生复现只检查材质的 extras 在三组简单文件中的行为；不承诺每种属性、对象或工具链都有同样结果。 |
| 稳定键保留两项并显式删除一项，而索引三项表面可读却全部错绑 | [Blender 原生及 Node 对照](../实验/重导入的子对象身份/README.md)。 | Node 是自定义抽象对照，结果不等于 Unity 的真实 fileID、持久资产读回或 FBX 表现。 |

调阅日期：2026-11-22。
