# HUD 安全区坐标：来源和证据

- Unity [Screen.safeArea](https://docs.unity.com/en-us/engine/6000.0/script-reference/unityengine/screen/safearea)，6000.0，Remarks：窗口局部像素、左下原点、部分 Android 14 及以前配置下已裁窗，返回往往是整窗口。该页面 2026-11-19 所见转换片段对目标左上矩形使用 H−y 并原样保留高度。独立反射上下边的几何试件得到 H−(y+h) 与 H−y；不能把片段的结果当成 UIKit 或 Unity 运行时测量。没有运行 Unity。
- Android Developers [Support display cutouts](https://developer.android.com/develop/ui/views/layout/display-cutout) 与 [Android 15 的目标行为](https://developer.android.com/about/versions/15/behavior-changes-15)：使用窗口范围而不是整块显示假设；非浮动窗口的 target 35 与 Android 15 行为受到具体版本条件约束，不能按设备型号外推。
- Godot [DisplayServer](https://docs.godotengine.org/en/4.6/classes/class_displayserver.html)，4.6，get_display_safe_area：Android/iOS 原生，其他平台回退到主窗口屏幕 usable rect；headless 窗口接口大多返回占位值。实际 Control 布局试件故意不将其当遮挡数据。
- Apple [UIView.safeAreaInsets](https://developer.apple.com/documentation/uikit/uiview/safeareainsets?language=objc) 和 [UIViewController.viewSafeAreaInsetsDidChange](https://developer.apple.com/documentation/uikit/uiviewcontroller/viewsafeareainsetsdidchange%28%29?changes=_6)：view 局部安全边距，早期未显示场景及本已在父级安全区的边距不等于设备切口永久为零；变化通知用来重读，不视为窗口、viewport 和布局全部原子更新。
- [复现材料](../实验/HUD安全区坐标/README.md) 用齐次窗口坐标的精确几何、故意混代与双扣对照，外加 Godot 4.6.3 的实际 Control 读回（模拟输入、一致布局调用）。插图为自行按算例比例制作的 SVG/PNG，不是真机截图。不证明设备安全区来源、旋转事件或命中分派。
