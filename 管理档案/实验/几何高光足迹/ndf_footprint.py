"""Sphere/plane diagnostic, D_GGX only; not a renderer or an engine integration."""
import json
import math

PITCH = 0.04
ALPHA = .015
PHASES = 41

def sphere(x, y):
    return x, y, math.sqrt(1-x*x-y*y)

def plane(x, y):
    return 0., 0., 1.

def sqdiff(v, w):
    return sum((a-b)**2 for a,b in zip(v,w))

def d_ggx(nz, a2):
    return a2/(math.pi*((1-nz*nz) + nz*nz*a2)**2)

def reference(shape,x,y,res):
    a2=ALPHA**2
    return sum(d_ggx(shape(x+PITCH*((i+.5)/res-.5),y+PITCH*((j+.5)/res-.5))[2],a2)
               for i in range(res) for j in range(res))/(res*res)

def run(shape):
    result=[]
    for i in range(PHASES):
        x=PITCH*(i/(PHASES-1)-.5)
        y=.007
        n=shape(x,y)
        nx=shape(x+PITCH,y); ny=shape(x,y+PITCH)
        extra=min((sqdiff(n,nx)+sqdiff(n,ny))/math.pi,.18)
        f=d_ggx(n[2], ALPHA**2+extra)
        r=reference(shape,x,y,128)
        r64=reference(shape,x,y,64)
        result.append((d_ggx(n[2], ALPHA**2), f, r, r64, extra))
    return result

def summarize(data):
    def info(i):
        v=[r[i] for r in data]
        return [min(v),max(v),math.sqrt(sum((r[i]-r[2])**2 for r in data)/len(data))]
    return {name: info(i) for i,name in enumerate(("point","trace_approximation","reference_128","reference_64"))} | {
        "kernel_minmax":[min(r[4] for r in data),max(r[4] for r in data)]}

s=run(sphere);p=run(plane)
assert all(r[0]==r[1] and r[4]==0 for r in p)
assert all(r[4]>0 for r in s)
print(json.dumps({"pitch":PITCH,"alpha":ALPHA,"phases":PHASES,
 "columns":["min_D","max_D","RMSE_vs_reference_128"],
 "sphere":summarize(s),"plane":summarize(p)},indent=2))
