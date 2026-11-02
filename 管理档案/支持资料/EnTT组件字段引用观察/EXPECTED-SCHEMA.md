# Typed expected schema：作者提案，待独立字面 oracle

本 schema 只定义协议中的单条件，不是执行输出或已接受的独立 oracle。成功11行按以下顺序；任何缺行、额外字段、重复JSON键、非有限值、类型混淆均拒绝。所有整数不得用bool代替。

## 通用类型

- Handle：对象，字段顺序 `full,index,version`；均整数，full 在0..2^32−1，index=full & 0xfffff，version=full >>20。真实 null entity 若被观察，仍表示完整4294967295及拆分，不用JSON null冒充。
- 可空 Handle：没有发生相应读取时才用JSON null。
- Bool：仅true/false。
- Count：非负整数。

## 第1行 declaration

字段顺序：`kind,schema,cplusplus,gcc,clang,entt,entity_mask,version_mask`。

kind=declaration，schema=1；cplusplus整数>=201703。gcc/clang各为三个非负宏整数或null，描述实际构建，不要求本机特定版本。entt=[3,13,2]，entity_mask=1048575，version_mask=4095。不输出自由版本字符串、安装路径或__FILE__。

## 第2–8行 token

每行字段顺序 `kind,stream,index,type,value`，kind=token。前四行stream=entities、index依次0..3；后三行stream=links、index依次0..2。

| stream/index | type | value类型与预期 |
|---|---|---|
| entities/0 | uint32 | 整数2（存储计数） |
| entities/1 | uint32 | 整数2（活跃计数） |
| entities/2,3 | entity | Handle；这两条恰为remote_box与remote_holder，彼此不同，不把任一未来分配整数硬编码 |
| links/0 | uint32 | 整数1 |
| links/1 | entity | Handle=remote_holder |
| links/2 | Link | 对象仅有target字段，Handle=remote_box |

两个实体token的实际次序原样记录；本命题不需要把内部存储排序作为通过条件，检查集合恰含两个来源实体即可。两个成功重复须实际逐行同值，而非先排序遮蔽差异。

这里的7个token同时对应限定普通Link路径的7次单参数writer调用；entity4、Link3分别计数。reader也分别4/3单参数调用，不把std::apply的tuple展开算成双参数archive。

## 第9–11行 stage

字段顺序：

`kind,stage,remote_box,remote_holder,local_seed,mapped_box,mapped_holder,source_target,archive_target,input_target,loaded_target,source_box_valid,source_holder_valid,seed_valid,box_contains,holder_contains,mapped_box_valid,mapped_holder_valid,holder_has_link,target_active_count,target_link_count,entity_written,link_written,entity_read,link_read,loaded_target_in_local_valid,loaded_target_equals_seed`

kind=stage，stage依次prepared、entities_loaded、component_loaded。

remote_box/remote_holder/local_seed/mapped_box/mapped_holder/source_target/archive_target 为Handle。input_target/loaded_target 可空Handle。三个来源/seed有效性、两个contains、两个mapped有效性、holder_has_link为Bool。六个计数为Count。最后两项为可空Bool。

`holder_has_link` 在 mapped_holder 无效时记录 false，不能调用无效组件 get；仅有效时询问是否存在Link。最终 get必须另行确认有效且存在。

| 字段 | prepared | entities_loaded | component_loaded |
|---|---|---|---|
| source_box_valid/source_holder_valid/seed_valid | true/true/true | true/true/true | true/true/true |
| box_contains/holder_contains | false/false | true/true | true/true |
| mapped_box_valid/mapped_holder_valid | false/false | true/true | true/true |
| holder_has_link | false | false | true |
| target_active_count | 1 | 3 | 3 |
| target_link_count | 0 | 0 | 1 |
| entity_written/link_written | 4/3 | 4/3 | 4/3 |
| entity_read/link_read | 0/0 | 4/0 | 4/3 |
| input_target/loaded_target | null/null | null/null | remote_box/remote_box |
| loaded_target_in_local_valid | null | null | 实际Bool，不规定真假 |
| loaded_target_equals_seed | null | null | 实际Bool，必须等于完整Handle比较结果 |

## 跨行关系与安全接收

- remote_box与remote_holder不同，三个固定实体值在所有阶段不变。source_target与archive_target始终等于remote_box，并与links/2的target一致。归档links/1=remote_holder。
- prepared两个map均为真实null哨兵。entities_loaded后两map均非null、彼此不同且各不等seed；mapped_box!=remote_box是**组件读取之前**必须成立的区分力门槛。不满足即停止，不能转用另一分配方案。
- component_loaded两map保持entities_loaded值；最终input_target、loaded_target=remote_box，而loaded_target!=mapped_box。目标Link数恰1且在mapped_holder上；没有引用转换路径。
- loaded_target_in_local_valid如实调用目标valid记录，不预设“无效”或“必为seed”。目标没有额外创建或销毁，且活跃数为3，因此该布尔值必须等于 loaded_target 的完整句柄是否属于 {local_seed, mapped_box, mapped_holder}。这只核内部自洽，不预先指定分配整数或固定真假。它不能证明业务等价；不对这个target做get/destroy/开箱操作。loaded_target_equals_seed只能由实际完整值比较计算。
- 归档输入reader每次取token前检查类型与游标，读后检查边界；不把整个结构reinterpret_cast成不同类型。writer仅保存值。Link是无hooks简单值类型，读取target不访问无效指针。
- 先真实emit，再显式核本阶段字面条件，失败停止后续读；涉及安全get的前提在get前检查，失败允许输出截断并整体拒绝。输出不可用预期值代替实际值。
- 两副本所有11行按严格类型逐项相同，包括编译宏描述。单次部分成功不是总体PASS。独立oracle须由reviewer另行冻结，不能以此schema作者身份冒充独立检查。
