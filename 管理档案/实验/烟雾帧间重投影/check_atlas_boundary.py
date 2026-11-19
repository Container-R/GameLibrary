from fractions import Fraction as F
import json

# First tile's last texel has alpha 1/4. The next tile starts at alpha 1.
# Use exact continuous texel-index coordinates (texel centres are integers).
tile_a = [F(0)]*7 + [F(1,4)]
tile_b = [F(1)]*8
atlas = tile_a + tile_b

def bilinear_1d(texels, x):
    i = x // 1
    u = x - i
    return ((1-u)*texels[i] if 0 <= i < len(texels) else 0) + (
           u*texels[i+1] if 0 <= i+1 < len(texels) else 0)

def sample(x):
    return {
        'atlas_no_tile_guard': str(bilinear_1d(atlas,x)),
        'clamp_to_tile_centres': str(bilinear_1d(tile_a,min(max(x,0),7))),
        'outside_tile_is_transparent': str(bilinear_1d(tile_a,x))
    }

rows = {str(x):sample(x) for x in (F(27,4),F(15,2),F(17,2))}
assert rows['15/2'] == {'atlas_no_tile_guard':'5/8','clamp_to_tile_centres':'1/4','outside_tile_is_transparent':'1/8'}
assert rows['17/2'] == {'atlas_no_tile_guard':'1','clamp_to_tile_centres':'1/4','outside_tile_is_transparent':'0'}
print(json.dumps(rows,indent=2))
