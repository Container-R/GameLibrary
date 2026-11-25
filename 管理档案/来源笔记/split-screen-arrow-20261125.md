# 分屏视口的离屏箭头：来源核对

核查日期 2026-11-25。[复现实验](../实验/分屏视口的离屏箭头/README.md)。

- [OpenGL 4.6 Core](https://registry.khronos.org/OpenGL/specs/gl/glspec46.core.pdf)，§13.8 坐标变换，剪裁坐标除以齐次 w 得到归一化坐标。截取原理，不将 OpenGL 轴符号直接套到 Unity 或 Godot。
- [Unity 6000.0 Camera.WorldToViewportPoint](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Camera.WorldToViewportPoint.html)：归一化坐标相对于相机，左下为 (0,0)，z 用世界单位。未运行 Unity。
- [Godot 4.7 Camera3D](https://docs.godotengine.org/en/4.7/classes/class_camera3d.html#class-camera3d-method-unproject-position) 与 [4.7.2-stable 源码](https://github.com/godotengine/godot/blob/4.7.2-stable/scene/3d/camera_3d.cpp#L458-L504)：视口局部投影、Y 反向；behind 比较采用近裁剪面。本篇不泛化镜头偏移或自定义投影下的坐标约定。
- 箭头采用侧向提示、视口内缩矩形与零侧向策略，属于本篇约定；不声称引擎提供同一套 UI 策略。
