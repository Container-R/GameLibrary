"""Exact 2D envelope and frustum rejection reference, no engine or GPU."""
from fractions import Fraction as F
from itertools import product
import json


def points(b):
    return list(product((b[0],b[2]),(b[1],b[3])))


def bounds(pts):
    x,y=zip(*pts)
    return min(x),min(y),max(x),max(y)


def minkowski(a,d):
    return (a[0]+d[0],a[1]+d[1],a[2]+d[2],a[3]+d[3])


def overlap(a,b):
    return not (a[2]<b[0] or b[2]<a[0] or a[3]<b[1] or b[3]<a[1])


def covers(outer,inside):
    return outer[0]<=inside[0] and outer[1]<=inside[1] and outer[2]>=inside[2] and outer[3]>=inside[3]

source=(F(11,4),F(-1,4),F(13,4),F(1,4))
clip=(-1,-1,1,1)
only_left=(-3,0,0,0)
full=minkowski(source,only_left)
shifted=minkowski(source,(-3,0,-3,0))
assert not overlap(source,clip) and overlap(shifted,clip) and overlap(full,clip)
assert covers(full,source) and covers(full,shifted)

# Instance linear part sends local (x,y) -> (-3*y, 2*x).
# Convert a world displacement VECTOR with no inverse translation.
world_range=(0,-2,3,4)
def inv_vec(v):
    wx,wy=v
    return F(wy,2),F(-wx,3)
local_range=bounds([inv_vec(p) for p in points(world_range)])
assert local_range==(-1,-1,2,0)
base=(-1,-2,3,4)
required=minkowski(base,local_range)
witness=[]
for xy in points(base):
    for w in points(world_range):
        dx,dy=inv_vec(w)
        witness.append((xy[0]+dx,xy[1]+dy))
assert bounds(witness)==required==(-2,-3,5,4)
assert not covers(minkowski(base,world_range),required)

def printable(v):
    return [int(x) if x.denominator==1 else str(x) for x in v]
print(json.dumps({"scope":"2D exact axis envelope and clip overlap, synthetic reference",
 "offscreen_base":printable(source),"shader_position_box":printable(shifted),
 "bounded_union":printable(full),"stale_frustum_cull":not overlap(source,clip),
 "accepts_bounded_union":overlap(full,clip),
 "union_admits_rest_pose_as_false_positive":overlap(full,clip) and not overlap(source,clip),
 "world_dxdy_range":world_range,"inverse_transformed_vector_range":printable(local_range),
 "required_local_bounds":printable(required)},indent=2))
