from fractions import Fraction as F
import json

def moments(points):
    n=len(points)
    return tuple(sum(v)/n for v in zip(*[(x,y,x*x,y*y,x*y) for x,y in points]))

def covariance(m):
    x,y,xx,yy,xy=m
    return xx-x*x,yy-y*y,xy-x*y

a=F(1,2)
clumps={
    "positive":[(a,a),(-a,-a)],
    "negative":[(a,-a),(-a,a)],
}
result={}
for name,(p,q) in clumps.items():
    m=moments([p,q])
    child=[moments([point]) for point in [p,q]]
    blended=tuple((x+y)/2 for x,y in zip(*child))
    wrongly_averaged_cov=tuple((x+y)/2 for x,y in zip(*[covariance(c) for c in child]))
    xx,yy,xy=covariance(blended)
    norm_z_squared=1/(1+p[0]**2+p[1]**2)
    directional=((xx+yy+2*xy)/2,(xx+yy-2*xy)/2)
    assert blended==m and wrongly_averaged_cov==(0,0,0)
    assert norm_z_squared==F(2,3) and xx==yy==F(1,4)
    assert directional==((F(1,2),0) if name=="positive" else (0,F(1,2)))
    result[name]={"mean_unit_normal_z_squared":str(norm_z_squared),"slope_cov_xx_yy_xy":list(map(str,(xx,yy,xy))),"directional_variance_plus_minus_45_deg":list(map(str,directional)),"naive_average_child_cov":list(map(str,wrongly_averaged_cov))}
print(json.dumps(result,indent=2))
