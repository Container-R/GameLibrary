# Shader displacement versus authored CPU bounds

Run in a temporary copy, keeping archived outputs unchanged:

```sh
tmp=$(mktemp -d)
cp probe.py "$tmp/"
python3 -B "$tmp/probe.py" > "$tmp/observed.json"
cmp "$tmp/observed.json" observed.json
cmp "$tmp/readback.ppm" readback.ppm
```

`readback.png` preserves the exact RGB pixels of `readback.ppm`. Uses only Python standard library ctypes and existing EGL/OpenGL libraries. Software surfaceless Mesa, no Xvfb, no installation. Writes readback.ppm beside the copied script. Two runs produced identical JSON and actual readback PPM.

Known geometry: two triangles form a quad, x=[2.5,3.5], y=[−0.5,0.5], z=0,w=1 with identity view/projection. The vertex shader adds a uniform x displacement. At dx=−3 the quad covers the center 32×32 pixels of a 64×64 RGBA8 framebuffer. At dx=0 it is entirely clipped. No perspective, transform hierarchy or animation.

The Python application decides whether to submit glDrawArrays at all, by an explicit inclusive 2D AABB intersection with clip xy=[−1,1]². This deliberately stands in for an application admission stage: it is NOT Godot/Unreal/native engine culling. Declared allowed displacement envelope is dx=[−3,0], dy=0, producing conservative bounds x=[−0.5,3.5], y=[−0.5,0.5].

Actual five raster panels, left to right in readback.ppm:
1. Culling disabled, dx=−3: submitted, 1024 red pixels.
2. Source AABB admission, dx=−3: not submitted, 0 red pixels.
3. Expanded-envelope admission, dx=−3: submitted, 1024 red pixels.
4. Expanded-envelope admission, dx=0: submitted, 0 red pixels.
5. Culling disabled, dx=0: submitted, 0 red pixels.

Every framebuffer pixel is checked to be either opaque black or opaque red; center pixel, counts, GL error and PPM hash are recorded. PPM directly concatenates actual framebuffer readbacks rather than an illustrative reconstruction. Blending, depth, face culling, dithering, framebuffer sRGB disabled; single-sample RGBA8 target. Shader compile/link and FBO completeness checked.

Case 4 demonstrates a conservative false positive: draw submitted but not visible. It is harmless to these pixel results, not necessarily free in performance. No performance measurement, hardware GPU claim, native engine bounds update, shadow/depth pass test, collision test, occlusion or LOD test is made. Envelope is manually specified and valid only for the tested declared displacement range; if a material can exceed that range this bound is no longer guaranteed conservative.
