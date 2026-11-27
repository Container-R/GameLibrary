"""Synthetic 2D chain; it compares grip targets, not the IK solver."""
import math

def point(origin,angle,v):
    x,y = v
    c,s = math.cos(angle), math.sin(angle)
    return (origin[0]+c*x-s*y, origin[1]+s*x+c*y)

def dist(a,b):
    return math.hypot(a[0]-b[0],a[1]-b[1])

base_origin=(0.,0.)
final_origin=(10.,0.)
grip=(0.,30.) # centimetres in prop space
before=point(base_origin,0,grip)
after=point(final_origin,math.pi/2,grip)
late_delta=(final_origin[0]-base_origin[0],final_origin[1]-base_origin[1])
translation_only=(before[0]+late_delta[0],before[1]+late_delta[1])
assert tuple(round(x) for x in after)==(-20,0)
assert abs(dist(after,before)-math.sqrt(1300))<1e-9
assert abs(dist(after,translation_only)-math.sqrt(1800))<1e-9
print('stale / translate-only / current',*(tuple(round(x) for x in y) for y in (before,translation_only,after)))
print('target drift in cm',round(dist(after,before),2),round(dist(after,translation_only),2))

quarter=math.pi/2
palm=(4.,0.)
wrist=point(after,quarter,(-4.,0.))
old=point(before,quarter,(-4.,0.))
world_as_component=point((7.,9.),quarter,wrist)
shoulder=(-10.,10.)
scale=16/dist(shoulder,wrist)
clamped=tuple(o+(x-o)*scale for o,x in zip(shoulder,wrist))
later=(wrist[0]+6,wrist[1]-8)

def record(request,immediate,final,angle):
    return [round(e,2) for e in (dist(request,wrist),dist(immediate,request),dist(final,immediate),
             dist(point(final,angle,palm),after))]

for key,args,expected in [
    ('baseline',(wrist,wrist,wrist,quarter),[0,0,0,0]),
    ('old',(old,old,old,quarter),[36.06,0,0,36.06]),
    ('world_as_component',(world_as_component,world_as_component,world_as_component,quarter),[31.78,0,0,31.78]),
    ('reach16',(wrist,clamped,clamped,quarter),[0,1.20,0,1.20]),
    ('later',(wrist,wrist,later,quarter),[0,0,10,10]),
    ('wrong_orientation',(wrist,wrist,wrist,0),[0,0,0,5.66]),
    ('wrist_aimed_at_grip',(after,after,after,quarter),[4,0,0,4]),
]:
    got=record(*args)
    assert got==expected,(key,got,expected)
    print(key,got)
