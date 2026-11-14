from fractions import Fraction as F

A = (0, 0, 0)
B = (1, 0, 1)
C = (1, 1, 0)
D = (0, 1, 1)
P = (F(1,2), F(1,2), F(0))
# ABD: x+y-z=0, BCD: -x-y-z+2=0. Projection is nearest on
# its plane; convex weights certify that the foot lies in the triangle.
checks = [((1,1,-1),0,(A,B,D),(F(2,3),F(1,6),F(1,6))),
          ((-1,-1,-1),2,(B,C,D),(F(1,6),F(2,3),F(1,6)))]
def dot(X,Y):
    return sum(x*y for x,y in zip(X,Y))
for n,d,triangle,weights in checks:
    assert all(dot(n,v)+d==0 for v in triangle)
    r=dot(n,P)+d
    foot=tuple(p-r*x/dot(n,n) for p,x in zip(P,n))
    assert sum(weights)==1 and all(w>=0 for w in weights)
    assert foot==tuple(sum(w*v[i] for w,v in zip(weights,triangle)) for i in range(3))
    squared=dot(tuple(p-q for p,q in zip(P,foot)),tuple(p-q for p,q in zip(P,foot)))
    assert squared==F(1,3) and squared>F(1,4)
    print(foot,squared)
