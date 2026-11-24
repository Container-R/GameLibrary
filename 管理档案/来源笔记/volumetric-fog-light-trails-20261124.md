# 体积雾灯光拖尾：来源记录

- Epic Games，[Volumetric Fog，Unreal Engine 5.9](https://dev.epicgames.com/documentation/en-us/unreal-engine/volumetric-fog-in-unreal-engine)，Temporal Reprojection。文档说明相机视锥低分辨率体积纹理、子体素抖动、历史重投影以及快速变化灯的拖尾。Volumetric Scattering Intensity 设为零是禁用该灯的雾贡献，不宣称能只保留新处。访问日期：2026-11-24。
- Godot Engine，[Volumetric fog and fog volumes，4.7](https://docs.godotengine.org/en/4.7/tutorials/3d/volumetric_fog.html)，Volumetric fog properties 与 Temporal Reprojection。只采用混合强度的稳定/拖尾取舍与 Volumetric Fog Energy，不把试件 0.9、0.7 当作默认值。
- [软件试件](../实验/体积雾的灯光历史/README.md)为本文独立固定视图所用数据。用简化深度透射、历史平滑和已知遮罩；无真实引擎/硬件重投影、移动相机、阴影或自动甄别。
