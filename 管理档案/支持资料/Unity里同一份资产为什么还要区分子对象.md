# Unity里同一份资产为什么还要区分子对象

一份门的模型资产里有门框和门扇。交接工具确认文件存在、`.meta` 也保留了，场景却需要更具体的答案：这项引用要用的是门框，还是门扇？如果检查记录只留下文件的 GUID，就还没有表达这一区别。

这份说明面向维护 Unity 导入与引用检查工具的技术美术和程序员，限定于 Unity 6000.0 官方编辑器文档。下面的门资产和数字都是原创假设，没有运行 Unity，也没有观察到某个模型的引用损坏。

## 文件身份与文件里的对象要分开记录

Unity 的 `.meta` 保存资产身份和导入设置，应随对应资产一起保留。[1] 但一份资产文件可以导入出多个对象。Unity 序列化资产引用时，使用 GUID 和 local file ID：前者确定资产，后者在该资产的范围内区分被引用的对象。[2][3]

假设工具需要分别检查门框与门扇，可把记录写成下面的样子：

| 要检查的对象 | 文件 GUID | local file ID |
|---|---|---:|
| 门框 | G | 101 |
| 门扇 | G | 202 |

G 只是同一 GUID 的代称，101、202 是任意教学数值，不是真实导入结果或编号规律。如果工具用 GUID 作为键，每个键下只允许存一个对象记录，这两行就不能同时保留下来。按 GUID 把它们归为一组没有问题；问题是把“属于同一个文件”当成了“就是同一个对象”。

因此，交付要求应写到实际需要的对象。例如，某个使用位置应引用门扇，就要核对门扇的对象身份和该位置实际取得的引用，而不只确认两者都来自同一个模型文件。

## 从实际对象取得身份，而不是猜数组顺序

对指定资产路径，编辑器工具可以用 `AssetDatabase.LoadAllAssetsAtPath` 查看主资产及其子资产，包括 Project 窗口中隐藏的子资产。该接口不保证主资产位于返回数组的第 0 项。[3] 因而不要把“第一个返回对象”直接当成主资产，更不能当成项目要使用的门扇。

对每个要记录的对象，`AssetDatabase.TryGetGUIDAndLocalFileIdentifier` 的对象重载可取得 GUID 和 local file ID。先检查返回值是否成功，并使用 `long` 接收 localId；官方说明某些 ID 可超过 32 位，旧的 `int` 重载不适合这个目的。[2] 返回失败时，记录为未取得身份，再调查对象和调用条件，不把失败自动解释为资产已经被删。

一种有限的交接检查是：先保存项目明确指定的预期对象记录，再在接收副本里取得相应对象与消费者引用，对照二者。对象名称和类型有助于阅读记录，但不能仅凭显示名或数组位置替代对象身份。这是检查方法建议，不是已经实现的自动修复工具。

即使身份对上了，也还要核对网格、尺寸等制作要求。相同身份并不等于相同内容；保留 `.meta` 也不能代替对子对象和实际使用位置的检查。

## 自定义导入器还要让对象键跟随对象

如果门资产由自己的导入器产生，`AssetImportContext.AddObjectToAsset` 还要求每个添加对象具有文件内唯一的字符串 `identifier`，并在重新导入时为同一对象再次生成相同、确定性的 identifier，让 Unity 能匹配前后导入的对象。[4] 这个字符串不是上面的数值 local file ID，不能从这页文档推算两者的转换。

例如，制作格式明确规定两个长期不变的部件角色，门框为 `frame`，门扇为 `leaf`，导入器就可以围绕这些角色设计对象键。反过来，若只拿当前列表序号当键，第一次列表是“门框、门扇”，下一次却是“门扇、门框”，同一个序号已经指向不同角色。即使每次都能生成序号 0 和 1，也不能用这一点证明同一对象得到了同一键。

这是对键选择的条件推演，不是说 Unity 必然生成某个 file ID 或必然把引用绑错。具体格式若允许角色变化、对象拆分、重命名或替换，就必须另行定义对应关系和迁移办法；不能给显示名加一个前缀便宣称身份永久稳定。

回到交接检查，文件、对象和内容是三层不同的问题。保留完整文件与 `.meta`，核对具体对象引用，再检查制作属性，三者不能互相替代。本说明没有验证 FBX、Sprite 切片、Unity 版本升级或跨机器导入行为，也不提供手改引用或 `.meta` 的修复配方。

## 参考来源

以下均为 Unity Technologies 的英文 Unity 6000.0 官方文档，2026-11-05 核对。它们是可变的版本化网页，不是某个 Unity 补丁版的实测报告。

1. [Asset metadata](https://docs.unity.com/en-us/engine/6000.0/manual/assets-and-media/import-assets/asset-metadata)，Asset IDs、Meta files、Moving and renaming assets：资产身份、导入设置与 `.meta` 的保存关系。
2. [AssetDatabase.TryGetGUIDAndLocalFileIdentifier](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityeditor/assetdatabase/trygetguidandlocalfileidentifier)，Object 重载的 Parameters、Returns、Remarks：GUID/file ID 组合、成功返回值与 `long` 要求。
3. [AssetDatabase.LoadAllAssetsAtPath](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityeditor/assetdatabase/loadallassetsatpath)，Remarks：多子资产、隐藏对象与主资产数组位置的限制。
4. [AssetImportContext.AddObjectToAsset](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityeditor/assetimporters/assetimportcontext/addobjecttoasset)，Parameters、Remarks：导入对象的文件内唯一 identifier 与跨导入确定性。

[返回资产导入正文](../../GameLibrary/技术美术/环境管线/资产导入/换一台电脑后如何保持资产导入结果一致.md)
