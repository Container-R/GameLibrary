"""Exact 2D texture coordinates for two adjacent modules; not a rendered material."""
from fractions import Fraction as Q

def add(a,b):
    return tuple(x+y for x,y in zip(a,b))
def sub(a,b):
    return tuple(x-y for x,y in zip(a,b))
def rot90(p):
    return (-p[1],p[0])
def inv90(p):
    return (p[1],-p[0])
def phase(p):
    # 3m period in x, enough to show a seam at the 2m module boundary.
    return p[0]%3/3
def result(name,p):
    print(name, p, 'x phase',phase(p))

a,b=(Q(0),Q(0)),(Q(2),Q(0))
shared=(Q(2),Q(1,4))
assert phase(sub(shared,a))!=phase(sub(shared,b))
result('seam A in per-piece space',sub(shared,a))
result('seam B in per-piece space',sub(shared,b))
translation=(Q(5),Q(7))
moved=add(rot90(shared),translation)
anchored=inv90(sub(moved,translation))
assert anchored==shared and phase(moved)!=phase(shared)
result('both sides before movement in shared frame',shared)
result('both sides after rotate/translate in same shared frame',anchored)
result('moved surface in fixed world frame',moved)
world_before_rebase=(Q(2002),Q(16001,4))
origin_shift=(Q(1000),Q(2000))
world_after_rebase=sub(world_before_rebase,origin_shift)
group_before=(Q(2000),Q(4000))
group_after=sub(group_before,origin_shift)
assert sub(world_before_rebase,group_before)==sub(world_after_rebase,group_after)==shared
assert phase(world_before_rebase)!=phase(world_after_rebase)
result('raw coordinate phase before origin rebase',world_before_rebase)
result('raw coordinate phase after origin rebase',world_after_rebase)
local_point=(Q(2),Q(1,4))
scaled_point=(2*local_point[0],local_point[1])
result('point with x2 object scale, object-fixed lookup',local_point)
result('same point with world-metre lookup',scaled_point)
