"""Local slope, not the gradient of a globally weighted height field."""
from math import sqrt, sin, cos, acos, radians, degrees
import json
from struct import pack, unpack

def add(a,b):return tuple(x+y for x,y in zip(a,b))
def sub(a,b):return tuple(x-y for x,y in zip(a,b))
def times(a,s):return tuple(x*s for x in a)
def dot(a,b):return sum(x*y for x,y in zip(a,b))
def unit(a):return times(a,1/sqrt(dot(a,a)))
def weights(n,p):
    strength=tuple(abs(x)**p for x in n)
    return times(strength,1/sum(strength))
def tangent(n,g):return sub(g,times(n,dot(n,g)))
def resolve(n,g):return unit(sub(n,tangent(n,g)))
def angle(a,b):return degrees(acos(max(-1,min(1,dot(a,b)))))
def close(a,b):return max(abs(x-y) for x,y in zip(a,b))<1e-9

flat_errors={}
for p in (1,2,4):
 for theta in range(90):
    n=(cos(radians(theta)),sin(radians(theta)),0)
    w=weights(n,p)
    flat_errors.setdefault(p,[]).append((theta,angle(n,unit(w)),angle(n,resolve(n,(0,0,0)))))
assert max(x[1] for x in flat_errors[1])<1e-5
assert max(x[1] for x in flat_errors[4])>20
assert max(x[2] for e in flat_errors.values() for x in e)<1e-5

# P is in world-length units; each row is the gradient of a sampler coordinate.
# For X, U = -2*z is mirrored and tiled; V = y.
basis=((0,0,-2),(0,1,0))
q=unit((.35,-.15,1))
d=(-q[0]/q[2],-q[1]/q[2])
chain=add(times(basis[0],d[0]),times(basis[1],d[1]))
wrong=add(times((0,0,2),d[0]),times(basis[1],d[1]))
h=lambda p:d[0]*dot(p,basis[0])+d[1]*dot(p,basis[1])
p=(.7,-1.2,2.1)
step=1e-5
directions=[(.0,.0,step),(.0,step,.0),(step,.0,.0)]
fd=tuple((h(add(p,e))-h(sub(p,e)))/(2*step) for e in directions)[::-1]
assert close(fd,chain)
n=(1,0,0)
a,b=resolve(n,chain),resolve(n,wrong)
assert a[2]<0<b[2]
assert abs(dot(n,tangent(n,chain)))<1e-9

# Two projected slopes each contain a component along the base normal.
n=unit((1,2,3))
g0=(0,.15,.7);g1=(.25,0,-.15);g2=(-.2,.4,0)
w=weights(n,2)
gg=(0,0,0);tg=(0,0,0)
for gi, wi in zip((g0,g1,g2),w):
    gg=add(gg,times(gi,wi));tg=add(tg,times(tangent(n,gi),wi))
assert close(tangent(n,gg),tg)
assert abs(dot(n,tg))<1e-9
# Direct power rounds to zero at float32 precision; rescale ratios first.
n_equal=unit((1,1,1))
f32=lambda x:unpack("<f",pack("<f",x))[0]
unsafe=[f32(abs(x)**256) for x in n_equal]
safe=[f32((abs(x)/max(map(abs,n_equal)))**256) for x in n_equal]
assert unsafe==[0.0]*3 and safe==[1.0]*3
print(json.dumps({
 "fp32_equal_axis_high_exponent":{"p":256,"original_unnormalized":unsafe,"rescaled_weights":[x/sum(safe) for x in safe]},
 "neutral_baseline":{"normal_angle_degrees":25,
                     "naive_axis_blend_error_degrees":{p:round(flat_errors[p][25][1],6) for p in flat_errors},
                     "surface_gradient_error_degrees":{p:round(flat_errors[p][25][2],6) for p in flat_errors}},
 "negative_u_and_scale":{"sample_uv_gradient":d,"world_gradient_chain_rule":chain,"world_gradient_finite_difference":fd,
                         "resolved_normal":a,"resolved_if_flip_ignored":b},
 "projection_removes_normal_component":{"base":n,"weights":w,"weighted_world_gradient":gg,"tangent_gradient":tg,
                                       "dot_before":dot(n,gg),"dot_after":dot(n,tg)}
}, indent=2))
