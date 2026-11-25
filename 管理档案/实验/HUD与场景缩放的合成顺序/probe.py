"""One grayscale row: screen HUD after upscale versus baked into scene image."""
from math import floor
N = 16
def hud(column):
    return [float(x == column) for x in range(N)]
def half_then_bilinear(values):
    half = [(a+b)/2 for a,b in zip(values[::2],values[1::2])]
    output = []
    for px in range(N):
        x = (px+0.5)/2-0.5
        k = floor(x)
        a = half[min(max(k,0),len(half)-1)]
        b = half[min(max(k+1,0),len(half)-1)]
        output.append(a+(x-k)*(b-a))
    return output
def support(row):
    return [(i, v) for i, v in enumerate(row) if v > 0]
for col in (6,7,8):
    native,baked = hud(col),half_then_bilinear(hud(col))
    print(f"column={col} native={support(native)} baked={support(baked)}")
    assert sum(native)==sum(baked)==1
assert half_then_bilinear(hud(6))==half_then_bilinear(hud(7))
assert hud(6)!=hud(7)
