"""Bounded authored checks, not an engine/upstream test suite."""
import json, math, random
from reference import solve, add, mul, sub, norm
rows=[]

def check(name,args,status='SOLVED',K=None,E=None):
    r=solve(**args)
    assert r['status']==status,(name,r)
    if K is not None: assert norm(sub(r['positions']['K'],K))<1e-8,(name,r)
    if E is not None: assert norm(sub(r['positions']['E'],E))<1e-8,(name,r)
    rows.append({'name':name,'input':args,'output':r})
    return r

base=dict(O=(0.,0.,0.),T=(.5,0.,0.),a=.6,b=.4,p=(0.,1.,0.))
check('normal_06_04',base,K=(.45,math.sqrt(.1575),0.))
check('normal_04_06',dict(base,a=.4,b=.6),K=(.05,math.sqrt(.1575),0.))
r_decimal=check('decimal_inner_a_lt_b',dict(base,a=.4,b=.6,T=(.2,0.,0.)))
assert r_decimal['near_boundary'] and r_decimal['positions']['K'][0]<0
check('binary_exact_inner_a_lt_b',dict(base,a=.5,b=1.,T=(.5,0.,0.),p=None),K=(-.5,0.,0.))
check('binary_exact_inner_a_gt_b',dict(base,a=1.,b=.5,T=(.5,0.,0.),p=None),K=(1.,0.,0.))
check('binary_exact_outer',dict(base,a=1.,b=.5,T=(1.5,0.,0.),p=None),K=(1.,0.,0.))
for d in (.1,1.1):
    check('reject_'+str(d),dict(base,T=(d,0.,0.)),status='UNREACHABLE')
    check('project_'+str(d),dict(base,T=(d,0.,0.),mode='nearest',p=None))
check('no_pole',dict(base,p=None),status='NEED_BEND_DIRECTION')
check('zero_pole',dict(base,p=(0.,0.,0.)),status='NEED_BEND_DIRECTION')
check('collinear_pole',dict(base,p=(1.,0.,0.)),status='NEED_BEND_DIRECTION')
check('weak_pole',dict(base,p=(1.,1e-8,0.)),status='NEED_BEND_DIRECTION')
a=check('pole_positive',dict(base,p=(1.,.01,0.)))
b=check('pole_negative',dict(base,p=(1.,-.01,0.)))
assert abs(norm(sub(a['positions']['K'],b['positions']['K']))-2*math.sqrt(.1575))<1e-12
for aa,bb in ((.5,.5),(.6,.4),(.4,.6)):
    args=dict(base,T=(0.,0.,0.),a=aa,b=bb,p=None)
    if aa==bb:
        check('zero_equal_no_direction',args,status='NEED_FOLD_DIRECTION')
        check('zero_equal_direction',dict(args,zero_dir=(0.,1.,0.)),K=(0.,aa,0.),E=(0.,0.,0.))
    else:
        check('zero_unequal_reject_'+str(aa),args,status='UNREACHABLE')
        check('zero_unequal_nearest_missing_'+str(aa),dict(args,mode='nearest'),status='NEED_TARGET_DIRECTION')
        check('zero_unequal_nearest_direction_'+str(aa),dict(args,mode='nearest',zero_dir=(1.,0.,0.)),K=((aa if aa>bb else -aa),0.,0.),E=(abs(aa-bb),0.,0.))
for key,value in [('a',0.),('a',-1.),('a',float('nan')),('b',float('inf')),('T',(float('nan'),0.,0.)),('p',(0.,float('inf'),0.)),('mode','stretch')]:
    # Encode invalid floating inputs later as strings for strict JSON.
    check('invalid_'+key+'_'+str(value),dict(base,**{key:value}),status='INVALID_INPUT')
check('unsupported_length_ratio',dict(base,a=1e-10,b=1.),status='NUMERIC_RANGE')
check('coordinate_subtraction_overflow',dict(base,O=(-1e308,0.,0.),T=(1e308,0.,0.)),status='NUMERIC_RANGE')
check('large_origin_residual_failure',dict(base,O=(1e16,0.,0.),T=(1e16,0.,0.),a=.5,b=.5,zero_dir=(1.,0.,0.)),status='NUMERIC_FAILURE')
for scale in (1e-120,1e-6,1.,1e6,1e120):
    oo=mul(scale,(3.,-5.,2.)); tt=add(oo,mul(scale,base['T']))
    check('scale_'+str(scale),dict(base,O=oo,T=tt,a=.6*scale,b=.4*scale))
check('tiny_nonzero_equal_target',dict(base,a=.5,b=.5,T=(1e-200,0.,0.)))

# A fixed nontrivial rigid transform: cyclic rotation plus translation.
rot=lambda v:(v[2],v[0],v[1])
tr=(3.,-2.,5.)
r0=solve(**base)
r1=check('rigid_transform',dict(base,O=add(rot(base['O']),tr),T=add(rot(base['T']),tr),p=rot(base['p'])))
assert norm(sub(r1['positions']['K'],add(rot(r0['positions']['K']),tr)))<1e-12

rng=random.Random(291)
maxerr=0.
for i in range(256):
    aa=rng.uniform(.1,2.); bb=rng.uniform(.1,2.)
    direction=(rng.uniform(-1,1),rng.uniform(-1,1),rng.uniform(-1,1)); dn=norm(direction)
    u=mul(1/dn,direction)
    d=abs(aa-bb)+(aa+bb-abs(aa-bb))*rng.uniform(.02,.98)
    pp=(u[1],-u[0],.4)  # skipped only if weak; generated inputs checked below
    r=solve((0.,0.,0.),mul(d,u),aa,bb,pp)
    assert r['status']=='SOLVED',(i,r)
    maxerr=max(maxerr,*r['residuals'].values())

def clean(x):
    if isinstance(x,float) and not math.isfinite(x): return str(x)
    if isinstance(x,dict): return {k:clean(v) for k,v in x.items()}
    if isinstance(x,(tuple,list)): return [clean(v) for v in x]
    return x
report={'scope':'Original position-only binary64 reference; no engine or upstream test execution.',
        'named_cases':len(rows),'seeded_cases':256,'seed':291,'max_seeded_residual':maxerr,
        'cases':clean(rows)}
print(json.dumps(report,ensure_ascii=False,indent=2,allow_nan=False))
