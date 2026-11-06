"""Original Rodrigues/length checks for a source-derived ozz axis counterexample.
Not an ozz implementation, engine run, SIMD test or upstream test execution.
"""
import math, json

def dot(a,b): return math.fsum(x*y for x,y in zip(a,b))
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def mul(s,a): return tuple(s*x for x in a)
def cross(a,b):
    return (a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0])
def norm(v): return math.hypot(*v)
def unit(v): return mul(1/norm(v),v)
def rotate(v,n,t):
    return add(add(mul(math.cos(t),v),mul(math.sin(t),cross(n,v))),mul(dot(n,v)*(1-math.cos(t)),n))
def inner(r,s): return math.acos(max(-1,min(1,-dot(r,s)/(norm(r)*norm(s)))))

r=(1.,0.,0.); s=(0.,1.,0.); target_distance=2.
initial_angle=inner(r,s)
corrected_angle=math.acos((norm(r)**2+norm(s)**2-target_distance**2)/(2*norm(r)*norm(s)))
rows=[]
for name,n in [('oblique',unit((0.,1.,-1.))),('perpendicular',(0.,0.,-1.))]:
    side=dot(cross(r,n),s)
    signed_initial=initial_angle if side>=0 else -initial_angle
    delta=corrected_angle-signed_initial
    after=rotate(s,n,delta)
    distance=norm(add(r,after))
    opening=inner(r,rotate(s,n,.01))-initial_angle
    assert abs(norm(n)-1)<1e-15 and opening>0
    if name=='oblique':
        assert abs(distance-math.sqrt(2+math.sqrt(2)))<1e-14
        assert abs(after[0]-1/math.sqrt(2))<1e-14
        assert abs(after[1]-.5)<1e-14 and abs(after[2]+.5)<1e-14
        assert target_distance-distance>.15
    else:
        assert abs(dot(n,r))<1e-15 and abs(dot(n,s))<1e-15
        assert abs(distance-target_distance)<1e-14
        assert norm(add(after,mul(-1,r)))<1e-14
    rows.append(dict(name=name,axis=n,dot_first=dot(n,r),dot_second=dot(n,s),
        positive_001_angle_change=opening,source_formula_angle_delta=delta,
        second_vector_after=after,root_end_distance=distance,
        best_possible_error_after_rigid_start_rotation=abs(target_distance-distance)))

# Same planar construction under an explicit rotation and positive uniform scales.
# Also check an interior target, not only full extension.
rotation_axis=unit((1.,2.,-3.)); angle=.73
rr=rotate(r,rotation_axis,angle); ss=rotate(s,rotation_axis,angle)
nn=rotate((0.,0.,-1.),rotation_axis,angle)
transformed=[]
for scale in (.125,1.,8.):
    R=mul(scale,rr); S=mul(scale,ss)
    for d in (1.,1.5,2.):
        target=d*scale
        theta=math.acos((norm(R)**2+norm(S)**2-target**2)/(2*norm(R)*norm(S)))
        out=add(R,rotate(S,nn,theta-inner(R,S)))
        err=abs(norm(out)-target)
        assert err<1e-13
        transformed.append({'scale':scale,'target':target,'residual':err})
print(json.dumps({'scope':__doc__,
 'input':{'O':(0,0,0),'K':(1,0,0),'E':(1,1,0),'target':(2,0,0),
          'joint_rotations':'identity','weight':1,'soften':1},
 'cases':rows,'positive_similarity_cases':transformed},indent=2))
