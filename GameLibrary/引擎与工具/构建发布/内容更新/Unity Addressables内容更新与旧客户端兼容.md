# Unity Addressables内容更新与旧客户端兼容

游戏已经发给玩家，现在只想替换一张装备纹理。编辑器里新纹理显示正常，内容更新也构建成功，于是团队准备上传文件。但玩家仍在运行上个月的客户端：它会找到哪份资源？没改过的装备还能加载吗？构建时选的旧状态文件，真的是这个客户端发布时留下的吗？

这些问题要分别回答。内容更新不是给最新工程打一个新包，而是让已经安装的客户端继续找到一组相容的内容。本文面向负责 Unity 内容构建、资源接入与测试的开发者，以 Addressables 1.21.21 文档为范围，说明该保存什么、怎样追更新影响，以及旧客户端应检查什么。装备例是虚构安排，没有执行 Unity 构建、托管或加载测试。

## 先把要服务的旧客户端找出来

这里的 **Player** 指实际发布给玩家的客户端程序；**AssetBundle** 是打包后的资源文件；**catalog（内容目录）**告诉 Addressables 怎样找到资源及其依赖。编辑器中的内容可以变，玩家安装的程序却不会因此自动改变。

先明确本次服务哪次发行、哪个平台，再找出当时发布的客户端和内容记录。Addressables 的 `addressables_content_state.bin` 保存内容构建状态，是制作后续更新的重要输入。应为每次完整应用发行的每个平台保存对应文件，而不是只留工作目录里最新的一份。默认构建会更新它；沿同一次原始发行继续做第二次、第三次内容更新，仍使用那次原始发行的 state。[1]

可以把客户端、原始 catalog、内容清单、state 的归档位置和文件摘要放在一起，并记录源提交、Unity、Addressables 与构建脚本版本。摘要帮助认出同一份字节，不会自行证明发行获准或整个供应链可信。建立这些关联，是团队的交接办法，不是 Addressables 替团队完成的认证。

还要先确认这条更新路线存在：旧客户端发布前须已启用远程 catalog。否则不能因为现在工程中勾选了这个选项，就假定已安装程序会开始检查远端更新。[1]

## 填对远程地址，不一定读到了那份基线

设团队想给发行线 P 更新内容，但工作机此前还处理过另一条发行线 Q。作业设置指向 P 的远程 state，机器上却留有别的本地缓存。

1.21.21 设置文档有一个值得单独检查的行为：远程 previous-state 文件不存在，而缓存位置已有文件时，系统会读取本地文件。默认位置是 `Library/com.unity.addressables/AddressablesBinFileDownload/`。[2] 文档所说的是这个缺失条件，不能直接扩展成超时、权限拒绝或所有网络错误都会如此。

因此，地址表达的是“打算读什么”，不一定回答“这次实际读了什么”。上述 P/Q 情景不是已经复现的故障；也不能仅凭它断言错基线一定构建成功或一定失败。实际工作中应从受控归档取指定 state，核对其与旧发行的关系，再确认构建真正读取了这份输入。

独立工作目录能减少残留干扰，但干净不等于正确。构建结束后才计算一个可能已被覆盖的缓存文件摘要，也不能倒推此前读入的字节。若工具链没有可靠的读取记录，就先补上并验证这一观测能力，不要凭配置截图填写成功。本篇不提供一个已经验证过的日志字段或追踪插件。

这里的缓存属于**制作更新时的基线输入**。玩家设备上的 bundle 缓存属于**运行时资源获取**。清掉玩家缓存不能修正构建选错基线；清理工作目录也不应删除唯一的原始发行归档。

## 改了共享纹理，要沿使用关系看影响

回到装备例：两件装备通过各自材质使用同一纹理，第三件使用另一组材质和纹理。虽然只编辑了共享纹理，两件装备的文件都没动，它们使用的依赖已经改变了。

Unity 的内容更新示例专门说明这种情况：未直接编辑的消费者也可能因依赖变化进入更新组，影响可以沿引用链传播。[4] 所以应先画清纹理、材质和装备的使用关系，再查看限制检查实际移动了哪些资产。第三件是否真的无关，也应由引用关系确认，而不是看外观猜测。

不过，两个受影响装备不等于两个新 bundle。组内怎样打包取决于 **Bundle Mode**：一起打包、按主要资产分开，或按标签组合打包，会有不同组织结果。[6] 应继续看实际输出和候选 catalog 的引用，才能知道哪些内容落在新包、哪些仍指向旧包。编辑文件数、迁组资产数、bundle 数和玩家下载量是不同问题。

“静态组”也不等于永远禁止修改素材。该版本设置页称为 **Prevent Updates**，示例页仍使用 **Cannot Change Post Release**；这里保留文档的用词差别，不声称看过某个已安装编辑器的标签。限制检查会按原有设置组织变更内容；不要为了让本次构建通过，临时改变组的 Update Restriction。该设置的变更应留到完整构建。[2]

检查可能重排分组，适合先在版本控制中建立分支。随后用同一基线运行更新构建，检查新目录如何连接新旧 bundle。[3] 官方示例中的旧本地数据可以继续占据玩家设备空间，新引用则转向远程内容，不是把安装包里的旧资源原地改掉。[4]

还有一个容易混淆的判断：限制检查所用的依赖哈希变化，不总等于最后 bundle 字节变化；构建产生了某文件，也不等于发布目录会引用它。[3] 内容作者负责说清新纹理应呈现什么，构建人员负责追清它实际在哪里，不能用“检查完成”代替两者。

## 让真正的旧客户端读取候选内容

准备一份候选时，同时保存 catalog、hash 文件、bundle 清单及其摘要和托管位置，并记录改动前后的分组。这里的 hash 文件供客户端判断目录是否更新；文件之间的关系仍需检查，不是上传成功就自动成立。[3]

装备例可以这样安排一轮有区分力的检查，以下都是待实施建议：

1. **使用当时真正发布的客户端。** 不只运行新工程的编辑器，也不重新构建一个自称相同的旧版本。先用正确归档基线制作候选，把它交给对应平台的旧客户端。
2. **同时检查改变和未变内容。** 预先写明两件装备应出现怎样的新纹理，以及第三件应保持什么。确认实际加载与玩法中的结果，不只看请求完成或下载进度。
3. **分开两种缓存起点。** 在隔离测试数据中，分别检查尚未缓存相关远程 bundle、已有旧 bundle 的情况。某一种成功不能代替另一种。
4. **再做一次后续更新。** 仍从原始发行基线出发，检查流程有没有误用上一次更新留下的工作文件；并明确支持哪些旧客户端及目录状态。

还可以在隔离构建环境中故意准备一个已知不同的 state，并使指定远程文件缺失，检查团队自己的输入核对是否会拦下错配。这个负例不应指向生产服务，也不预设 Unity 最后一定报哪一种错。需要详细分工与记录时，可选读旧文的[基线交接建议](../../../../管理档案/历史正文/solutions/engine/addressables-content-update-baseline.md#2-原创交接协议把选择结果变成可核对的证据)及[旧客户端检查安排](../../../../管理档案/历史正文/solutions/engine/addressables-content-update-baseline.md#4-旧版客户端验证最小有区分力的候选测试)。它们仍是未执行方案。

支持的发行线越多，历史包、测试环境和缓存组合的维护成本越高。团队可以缩小支持范围，但应改变承诺，而不是用“最新版能运行”替代所有旧版结果。候选包怎样与输入对应，另见[《构建工程师如何交付可用的游戏版本》](../岗位与协作/构建工程师如何交付可用的游戏版本.md)。

## 会话中更新，还要处理已经持有的东西

启动时取得新目录，再开始加载，与玩家正在游戏中途换内容，是不同安排。检查目录有没有更新、更新目录、释放旧资产，也不是同一个动作。官方将旧资产的释放责任留给调用方；目录更新完成不会替现有对象自动换上新资源。[5]

若旧 bundle 仍在内存中，新版本可能遇到内部身份冲突。**Unique Bundle IDs** 用于让新旧版本共存，但开启后，含有引用变更资产的内容的 bundle 也须重建，可能增加成本。[2] 它不是限制检查迁组的另一种名字，更不是兼容性合格证。构建多了多少、用户多下载多少，仍要看实际结果。

因此，若产品要求中途更新，就另行安排旧对象持有、释放、重新加载和玩法状态接续的检查，不能直接继承启动加载的结论。

### 手动加载附加目录时，别漏掉加载操作

应用也可能通过 `LoadContentCatalogAsync` 手动加载附加 catalog。此时除了资源，还有“加载这份目录的异步操作”需要管理。

1.21.21 文档说明，指向同一 catalog 的先前加载操作未释放时，后续调用可能复用操作缓存而不下载新的远程目录。手动加载后的目录更新也要求先释放该加载操作。[7] 于是，“再次调用成功”不足以说明取到了远端新版本；先查谁还持有这个操作，而不是先删 bundle 缓存。

调用时应明确选一种管理办法：不需要继续持有，就使用 `autoReleaseHandle=true`，完成时自动释放；需要手动持有，就用 `false`，由明确的所有者在完成且不再需要操作时释放。需要处理结果，应在释放前完成；自动释放后不要继续读取句柄或再次手动释放。[8] 若还有其他持有者，只释放自己拥有的一份引用，不代表全部先前操作已释放。这里不猜测无 bool 参数重载的行为。

释放的是操作，不是卸载已经加载的 catalog；它也不保证一定重新下载。按 hash 判断目录缓存是否可用是另一层规则，hash 未变化时仍可能使用缓存。[7][8] 旧资产、设备上的 bundle 缓存，又分别是其他对象。详细的对象区分及两种持有条件对照，可读旧文[附加 catalog 的操作所有权](../../../../管理档案/历史正文/solutions/engine/addressables-content-update-baseline.md#41-手动加载附加-catalog先交代加载操作的所有权)。不要把其中任何一种“释放完成”当成所有内容已经更新。

尚未完成的资产加载则是另一项问题：玩家退出预览时，不能把目录操作的释放规则直接照搬。可参见[装备预览的迟到结果与加载收尾](../../运行时系统/异步资源/关闭装备预览后，未完成的资源加载怎样收尾.md)，其中明确区分放弃显示与底层取消。

## 有些变化，应回到新版客户端发行

Addressables 分发内容，不分发程序代码。代码变化需要新 Player，通常还需要新内容；想复用旧 bundle，需要分析类型树与新代码的兼容性。Unity 或 Addressables 升级也要求新客户端及新的内容构建。有自身补丁机制或不支持远程内容分发的平台，官方建议完整内容构建。[1] 制作内容更新时也不应悄悄改掉构建脚本。[3]

所以，在接受“只更新资源”这个任务前，就先确认改动是否仍在原发行线能够承担的范围。若不在，应明确转为新版客户端工作，而不是到最后才靠一份成功构建报告掩盖差别。

这篇文章提供的是版本化文档下的排查顺序：先选对基线，追依赖与输出，再用旧客户端检查目标内容。它没有验证内容分发网络（CDN）的上传原子性、回滚安全、目录签名、并发加载或所有网络错误，也没有下载量与内存性能数据。能读到一份目录，与整次上线安全，仍是两件事。

## 参考来源

2026-11-01 重新读取以下 Unity 官方页面的相关正文，页面标识均为 Addressables 1.21.21；只读文字，不使用截图推断已安装 Inspector，也未运行 Unity。示例及交接安排是本文的未执行建议，不是官方或本库测试结果。

1. [Content update builds overview](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-overview.html)：Content update build workflow、Build updated content、When to perform a full rebuild；原始 state、远程目录及完整重建边界。
2. [Content update build settings](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-settings.html)：Update a Previous Build setting、Group Update Restriction、Unique Bundle IDs。
3. [Build a content update](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-create.html)：两类工具、输出关系、限制检查与依赖哈希局限。
4. [Content update examples](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-examples.html)：假想静态组例及 Content update dependencies；不是实际项目观测。
5. [Check for content updates at runtime](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-builds-check.html)：目录更新与旧资产释放责任。
6. [Content Packing & Loading schema reference](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/ContentPackingAndLoadingSchema.html#advanced-options)：Advanced Options 中 Bundle Mode。
7. [Manage catalogs at runtime](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/LoadContentCatalogAsync.html)：Load additional catalogs、Update catalogs；操作缓存、目录缓存及释放前提。
8. [LoadContentCatalogAsync API](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/api/UnityEngine.AddressableAssets.Addressables.LoadContentCatalogAsync.html)：带 bool 参数重载及 Remarks。

---

[返回本书架](README.md)
