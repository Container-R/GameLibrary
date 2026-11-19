"""Exact reference model, NOT a GPU/engine experiment.

Each base texel is opaque linear scalar color: A=0, B=1. Rows are
identical, so this is exactly the horizontal component of separable 2D box
filtering and bilinear sampling, away from vertical borders. Coordinates
are base-texel units; texel centers are i+1/2. Mips use globally aligned
nonoverlapping boxes, recursively equivalent to averaging 2x at each level.
No sRGB, alpha, compression, anisotropy, derivatives, or automatic LOD.
All sampled coordinates are interior to the full atlas; no address wrapping.
An A region ends at edge, g A-colored extrusion texels follow, then B.
The left background is also A: only right-neighbor contamination is tested.
Values are B contribution fractions, not perceptual error measurements.
"""
from fractions import Fraction as F
import json

WIDTH = 32


def atlas(edge, gutter):
    return [F(int(i >= edge + gutter)) for i in range(WIDTH)]


def mip(base, level):
    width = 2 ** level
    assert len(base) % width == 0
    return [sum(base[i:i+width], F(0))/width
            for i in range(0, len(base), width)]


def sample(base, level, x):
    values = mip(base, level)
    q = F(x)/(2 ** level) - F(1, 2)
    lo = q.numerator // q.denominator
    t = q - lo
    assert 0 <= lo < len(values)
    if t == 0:
        return values[lo]
    assert lo + 1 < len(values)
    return values[lo]*(1-t) + values[lo+1]*t


def exact_overlap(a, b, c, d):
    return max(F(0), F(min(b, d)-max(a, c)))


def verify_box(base, edge, gutter):
    for level in range(6):
        w = 2 ** level
        for i, value in enumerate(mip(base, level)):
            expected = exact_overlap(i*w, (i+1)*w, edge+gutter, WIDTH)/w
            assert value == expected
        if level:
            prev = mip(base, level-1)
            assert mip(base, level) == [(prev[i]+prev[i+1])/2
                                       for i in range(0,len(prev),2)]


aligned = atlas(8, 0)
unaligned = atlas(7, 0)
for edge in (7, 8):
    for gutter in (0, 1, 2):
        verify_box(atlas(edge, gutter), edge, gutter)

# Level 2 has centers 2,6,10,...; aligned edge 8 lies between cells.
# At x=7.5, only the bilinear footprint crosses the edge: 5/8*A+3/8*B.
assert mip(aligned, 2)[1:3] == [0, 1]
assert sample(aligned, 2, F(15,2)) == F(3,8)
assert sample(aligned, 2, 6) == 0  # clamp to last pure A center
# Moving the boundary to 7 makes the [4,8) mip texel itself impure.
# At its exact center there is no contribution from another mip texel.
assert mip(unaligned, 2)[1] == F(1,4)
assert sample(unaligned, 2, 6) == F(1,4)

profiles = {}
for g in (0,1,2):
    base = atlas(8,g)
    profiles[str(g)] = {
        'B_at_original_last_A_center_x_7.5_levels_0_to_3':
            [sample(base,l,F(15,2)) for l in range(4)],
        # A content [4,8) and its entire small gutter are inside [0,16).
        # Even sampling only this mip texel cannot recover pure A.
        'level_4_cell_0_footprint': [0,16],
        'level_4_cell_0_B_fraction': mip(base,4)[0],
        'level_4_exact_center_x_8_B_fraction': sample(base,4,8),
    }
assert profiles['1']['B_at_original_last_A_center_x_7.5_levels_0_to_3'][1] == F(1,8)
assert profiles['2']['B_at_original_last_A_center_x_7.5_levels_0_to_3'][1] == 0
assert profiles['2']['B_at_original_last_A_center_x_7.5_levels_0_to_3'][2] == F(3,16)
assert profiles['1']['level_4_cell_0_B_fraction'] == F(7,16)
assert profiles['2']['level_4_cell_0_B_fraction'] == F(3,8)

# Explicit trilinear weight 1/2 between levels 1 and 2. Fine level is safe
# at this coordinate with two extruded base texels; coarser neighbor isn't.
base = atlas(8,2)
fine, coarse = sample(base,1,F(15,2)),sample(base,2,F(15,2))
tri = (fine+coarse)/2
assert (fine,coarse,tri) == (0,F(3,16),F(3,32))

def serial(x):
    if isinstance(x,F): return str(x)
    if isinstance(x,dict): return {k:serial(v) for k,v in x.items()}
    if isinstance(x,(list,tuple)): return [serial(v) for v in x]
    return x

print(json.dumps(serial({
    'scope':'exact linear opaque row-constant box mips; explicit sample coordinates and LOD; no engine',
    'aligned_sample_only': {'edge':8,'level':2,'neighbor_cell_B':[F(0),F(1)],
        'x':F(15,2),'right_weight':F(3,8),'sample_B':sample(aligned,2,F(15,2)),
        'clamped_x':6,'clamped_B':sample(aligned,2,6)},
    'unaligned_already_mixed': {'edge':7,'level':2,'footprint':[4,8],
        'x':6,'sample_B':sample(unaligned,2,6)},
    'extrusion_base_texels':profiles,
    'explicit_trilinear': {'gutter':2,'x':F(15,2),'LOD':F(3,2),
        'level_1_B':fine,'level_2_B':coarse,'sample_B':tri},
    'limit':'1 or 2 base extrusion texels are not universally safe across mip levels. This does not claim no safe level or derive a production padding budget.'
}),indent=2))
