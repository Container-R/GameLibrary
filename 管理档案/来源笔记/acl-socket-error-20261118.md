# 骨骼压缩虚拟探针与真实道具点：证据

核读：2026-11-18。动画运行时相邻目录和当前、链接历史正式目录未发现同题；未对全部未索引档案作覆盖声明。

1. Nicholas Frechette，[Measuring Accuracy](https://nfrechette.github.io/2016/11/01/anim_compression_accuracy/)，2016。物体空间与父骨、偏心点、用虚拟顶点近似真实皮肤形变。尽量靠近真实几何、不要把历史探针数量套给所有版本。
2. nfrechette/acl [v2.1.0](https://github.com/nfrechette/acl/releases/tag/v2.1.0)，固定提交 414689d5cff4286a7898487a46dc5e48005d38da。docs/creating_a_raw_track_list.md 24–40 定义 precision、shell_distance；includes/acl/compression/transform_error_metrics.h 230–263、333–375 确认点构造和 QVV 分支误差。所核有缩放分支取三个点，无缩放分支两个；不声称 UE 集成恰用同一版或每个误差度量均如此。
3. Epic [ACL 插件](https://dev.epicgames.com/documentation/unreal-engine/animation-compression-library-in-unreal-engine) 和 [Skeletal Mesh Sockets](https://dev.epicgames.com/documentation/unreal-engine/skeletal-mesh-sockets-in-unreal-engine)，重读时页面为 UE 5.9。前者给虚拟顶点距离、阈值与 Skeletal Mesh 形变估计目标；不能凭字段就认定独立附着几何参与。后者给 Socket 固定挂接与 Force Always Animated 的父链 LOD 求值行为；不代表压缩误差变小。前者误差阈值文字中高低两侧重复写“less error”，不转引歧义句。
4. 原创 Python 几何对照：探针旋转前后欧氏距离和弦长交叉核验。同一纯旋转误差下，0 cm 轴距保持位置；3 cm、80 cm 离轴分别约 0.005236、0.139626 cm。不能用这些数字推定某段动画的真实误差或字节数。
