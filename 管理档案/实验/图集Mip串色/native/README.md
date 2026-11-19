# Atlas mip: two separate failure mechanisms

Run in a fresh temporary copy so the archived outputs stay unchanged:

```sh
tmp=$(mktemp -d)
cp probe.py "$tmp/"
python3 -B "$tmp/probe.py" > "$tmp/observed.json"
cmp "$tmp/observed.json" observed.json
cmp "$tmp/readback.ppm" readback.ppm
```

`readback.png` is a nearest-neighbor 5x enlargement of the exact 128x32 readback (640x160, RGB), using no color changes. Uses Python stdlib ctypes and existing EGL/OpenGL libraries, forces Mesa software surfaceless rendering, disables shader disk cache. No installs. Writes only readback.ppm next to the copied script and JSON to stdout.

Three 8×4 opaque linear RGBA8 atlases: all rows identical. Red (255,0,0,255) for x<3, x<4, or x<6 respectively, blue elsewhere. Each calls actual glGenerateMipmap; glGetTexImage reads every level, including 4×2 level 1. No manually supplied mips.

Actual raster framebuffer is 128×32 RGBA8. Four adjacent 32×32 viewports draw a fullscreen triangle with constant fragment output; framebuffer RGB bytes produce readback.ppm. Left to right:

1. Misaligned x=3 boundary: texelFetch(1,0,LOD1) returns (128,0,128,255). Mixture is ALREADY in mip texel; no sample filtering is needed to expose it.
2. Aligned x=4 boundary: same texelFetch returns pure red. Level 1 row is red, red, blue, blue.
3. Same pure mip: textureLod at uv=(0.46875,0.5), LOD=1 returns (159,0,96,255). Texel x coordinate is u*4−0.5=1.375, hence 37.5% blue; RGBA8 quantization yields the recorded integers. Min filter GL_LINEAR_MIPMAP_NEAREST selects one level, bilinear within it; no trilinear or derivative-selected LOD.
4. Gutter control: nominal red tile ends at x=4, red edge is extruded into columns 4 and 5; blue begins at x=6. Same UV/LOD returns pure red. The blue content was shifted to reserve gutter, not silently painted over production content. This is a local footprint control, not a complete atlas packing algorithm or two-sided tile protection.

GL_CLAMP_TO_EDGE clamps only the whole atlas, not the internal tile. Dithering, blending, sRGB conversion and depth disabled; single-sample FBO. All four entire swatches are checked for uniform exact color. Both shader compilation and program link checked, FBO completeness and glGetError checked.

Boundaries: Mesa 25.0.7 llvmpipe (LLVM 19.1.7), actual software OpenGL 4.5 core; not hardware GPU benchmarking or engine mip-generation evidence. Exact reduction/rounding is an observation on this implementation, not a guarantee across all implementations. Known flat opaque colors avoid alpha, gamma, compression and normal-map effects. No anisotropic filtering or UV derivatives measured. The two-base-texel gutter only protects this sample at LOD1: level 2 already contains a mixed red/blue texel, explicitly asserted. Therefore do not infer fixed padding protects every mip.
