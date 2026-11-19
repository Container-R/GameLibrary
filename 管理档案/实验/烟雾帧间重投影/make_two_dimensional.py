from fractions import Fraction as F
from pathlib import Path
import json

W, H = 18, 15
XA, XB, XN, Y = 4, 10, 14, 7
T = F(1, 2)
grid = [(x,y) for y in range(H) for x in range(W)]

def soft_shape(x,y):
    # Manhattan profile gives a compact exact-alpha shape.
    return max(0, 3-abs(x)-abs(y)) / F(3)

def puff(x,y):
    return max(0, 2-abs(x)-abs(y)) / F(2)

def src_a(x,y):
    return soft_shape(x-XA,y-Y)

def src_b(x,y, newborn=False):
    return max(soft_shape(x-XB,y-Y), puff(x-XN,y-Y) if newborn else 0)

def cross(x,y):
    return (1-T)*src_a(x,y)+T*src_b(x,y)

def warp(x,y, newborn=False):
    # Main flow is a known displacement of +6 px. A toy oracle marks the
    # new feature unpaired; choose fading in place rather than advecting it.
    # This oracle is provided input, not something the algorithm infers.
    moved = (1-T)*src_a(x-T*(XB-XA),y) + T*src_b(x+(1-T)*(XB-XA),y)
    return max(moved, T*puff(x-XN,y-Y) if newborn else 0)

def mid_world(x,y, early_birth):
    return max(soft_shape(x-(XA+XB)//2,y-Y), puff(x-XN,y-Y) if early_birth else 0)

def error(a,b):
    return str(sum(abs(a(x,y)-b(x,y)) for x,y in grid))

rows = {
    "flat_mix_l1_vs_known_translation": error(cross, lambda x,y:mid_world(x,y,False)),
    "warped_l1_vs_known_translation": error(warp, lambda x,y:mid_world(x,y,False)),
    "same_endpoints_newborn_alpha_at_t_half": {
        "possible_world_A_early_birth": str(mid_world(XN,Y,True)),
        "possible_world_B_late_birth": str(mid_world(XN,Y,False)),
        "fallback_fades_in_place": str(warp(XN,Y,True))
    }
}
assert rows["flat_mix_l1_vs_known_translation"] == "32/3"
assert rows["warped_l1_vs_known_translation"] == "0"
assert warp(XN,Y,True) == F(1,2)
Path("two-dimensional-observed.json").write_text(json.dumps(rows,indent=2)+"\n")

panels = [
    ("A: first frame", src_a),
    ("B: last frame", src_b),
    ("Crossfade: two dim peaks", cross),
    ("Warp: one translated peak", warp),
    ("A: first frame (same input)", src_a),
    ("B: new puff on the right (same input)", lambda x,y:src_b(x,y,True)),
    ("Possible mid: early birth", lambda x,y:mid_world(x,y,True)),
    ("Possible mid: late birth", lambda x,y:mid_world(x,y,False)),
]
svg=['<svg xmlns="http://www.w3.org/2000/svg" width="1100" height="480" viewBox="0 0 1100 480" role="img" aria-label="Toy flipbook alpha tests">', '<rect width="1100" height="480" fill="#101925"/>', '<text x="17" y="30" fill="#f9fcff" font-family="sans-serif" font-size="21">Alpha in a synthetic smoke flipbook</text>']
for i,(label,fn) in enumerate(panels):
    x0,y0=17+(i%4)*271,67+(i//4)*202
    svg += [f'<text x="{x0}" y="{y0-5}" fill="#e6edf7" font-size="13" font-family="sans-serif">{label}</text>',
            f'<rect x="{x0}" y="{y0+7}" width="{W*14}" height="{H*10}" fill="#19293b" stroke="#526175"/>']
    for x,y in grid:
        a=fn(x,y)
        if a:
            opacity=f"{float(a):.6f}"
            svg.append(f'<rect x="{x0+x*14}" y="{y0+7+y*10}" width="14" height="10" fill="#dbeeff" opacity="{opacity}"/>')
svg.append('</svg>')
Path("two-dimensional.svg").write_text("\n".join(svg)+"\n")
