from fractions import Fraction as F
from math import floor
import json

N = 16
edge = F("1.2")
receiver = F("1.38")

def texels(center, width, snap):
    pitch = width / N
    origin = center - width / 2
    if snap:
        origin = floor(origin / pitch + F(1, 2)) * pitch
    cell = floor((receiver - origin) / pitch)
    assert 0 <= cell < N
    sample = origin + (cell + F(1, 2)) * pitch
    return [str(origin), str(pitch), cell, str(sample), "shadow" if sample < edge else "lit"]

def sweep(centers, widths, snap):
    return [texels(c,w,snap) for c,w in zip(centers,widths,strict=True)]

move = [F(x) for x in ("0", "0.3", "0.55", "0.7", "0.98")]
dynamic = sweep(move,[F(16)]*len(move),False)
snapped = sweep(move,[F(16)]*len(move),True)
stretch = sweep([F(0)]*4,[F(x) for x in ("16","17","15","22.4")],True)

assert len(set(r[-1] for r in dynamic))==2
assert len(set(r[-1] for r in stretch))==2
assert len(set(r[3] for r in snapped))==1
assert len(set(r[2] for r in snapped))==2

# X or Y independently: a radius-7 receiver set, round-to-nearest center
# displacement <= half a texel; reserve two additional texels for a defined
# continuous footprint. Show that including these texels affects the final pitch.
radius, guard = F(7), F(2)
width = 2 * radius * N / (N - 2 * guard - 1)
pitch = width / N
assert width/2 == radius + (guard + F(1,2))*pitch
print(json.dumps({"edge":str(edge),"receiver":str(receiver),
                  "fields":["origin","world_units_per_texel","local_index","world_sample_center","visibility"],
                  "translated_unsnapped":dynamic,"translated_snapped":snapped,
                  "varying_scale_even_snapped":stretch,
                  "coverage":{"n":N,"r":str(radius),"guard_texels":str(guard),
                              "min_width":str(width),"pitch":str(pitch)}},indent=2))
