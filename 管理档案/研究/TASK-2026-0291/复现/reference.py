"""Original stateless position-only two-bone reference, binary64 Python floats.
No ozz/engine code imported, installed or executed. See article for contract.
"""
import math

SIN_MIN = 1e-6          # policy: reject weak bend hints
REL_ERROR = 1e-9        # policy: relative residual per bone / chain scale
MIN_LENGTH_RATIO = 1e-8 # policy: supported ratio for this reference


def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def mul(s,a): return tuple(s*x for x in a)
def div(a,s): return tuple(x/s for x in a)
def dot(a,b): return math.fsum(x*y for x,y in zip(a,b))
def norm(a): return math.hypot(*a)
def finite_vec(a):
    return isinstance(a,(tuple,list)) and len(a)==3 and all(isinstance(x,(int,float)) and math.isfinite(x) for x in a)
def unit(a):
    if a is None: return None
    s=max(abs(x) for x in a)
    if s==0: return None
    v=div(a,s)
    return div(v,norm(v))


def solve(O,T,a,b,p=None,mode='reject',zero_dir=None):
    """p is a direction, not a point. zero_dir has branch-dependent explicit use.
    Failures have no K or E output. Reach classification is float, not exact-real.
    """
    result={'status':'INVALID_INPUT','positions':None}
    if (not finite_vec(O) or not finite_vec(T) or
        (p is not None and not finite_vec(p)) or
        (zero_dir is not None and not finite_vec(zero_dir)) or
        not isinstance(a,(int,float)) or not isinstance(b,(int,float)) or
        not math.isfinite(a) or not math.isfinite(b) or a<=0 or b<=0 or
        mode not in ('reject','nearest')): return result
    S=max(a,b)
    A,B=a/S,b/S
    if min(A,B)<MIN_LENGTH_RATIO:
        result['status']='NUMERIC_RANGE'; return result
    delta=sub(T,O)
    if not finite_vec(delta):
        result['status']='NUMERIC_RANGE'; return result
    t=div(delta,S)
    if not finite_vec(t) or any(x!=0 and y==0 for x,y in zip(delta,t)):
        result['status']='NUMERIC_RANGE'; return result
    D=norm(t)
    if not math.isfinite(D):
        result['status']='NUMERIC_RANGE'; return result
    lo,hi=abs(A-B),A+B
    relation='inside' if lo<=D<=hi else ('too_close' if D<lo else 'too_far')
    result.update(relation=relation,target_changed=False,
                  near_boundary=min(abs(D-lo),abs(D-hi))<=REL_ERROR,
                  direction_used=None)
    if relation!='inside' and mode=='reject':
        result['status']='UNREACHABLE'; return result
    De=min(hi,max(lo,D)) if mode=='nearest' else D
    result['target_changed']=De!=D
    if D==0:
        w=unit(zero_dir)
        if w is None:
            result['status']='NEED_FOLD_DIRECTION' if A==B else 'NEED_TARGET_DIRECTION'
            return result
        if A==B:
            k=mul(A,w); e=(0.,0.,0.); shape='folded_at_root'
        else:
            e=mul(lo,w); k=mul(A if A>B else -A,w); shape='inner_boundary'
        result['direction_used']=w
    else:
        u=div(t,D)
        # Preserve supplied endpoint when not projected, avoiding unnecessary roundtrip.
        e=t if De==D else mul(De,u)
        if De==hi:
            k=mul(A,u); shape='outer_boundary'
        elif De==lo:
            k=mul(A if A>B else -A,u); shape='inner_boundary'
        else:
            x=0.5*(De+((A-B)/De)*(A+B))
            # Factored radius: all factors nonnegative after domain checking.
            h=0.5*math.sqrt(hi-De)*math.sqrt(hi+De)*math.sqrt((De-lo)/De)*math.sqrt((De+lo)/De)
            if not math.isfinite(x) or not math.isfinite(h) or h<=0:
                result['status']='NUMERIC_FAILURE'; return result
            ph=unit(p)
            if ph is None:
                result['status']='NEED_BEND_DIRECTION'; return result
            q=sub(ph,mul(dot(ph,u),u))
            nq=norm(q)
            result['pole_sine']=nq
            if nq<=SIN_MIN:
                result['status']='NEED_BEND_DIRECTION'; return result
            v=div(q,nq)
            k=add(mul(x,u),mul(h,v)); shape='bent'
            result['direction_used']=v
    K=add(O,mul(S,k))
    E=T if not result['target_changed'] else add(O,mul(S,e))
    if not finite_vec(K) or not finite_vec(E):
        result['status']='NUMERIC_RANGE'; return result
    # Check assembled outputs, not only ideal normalized intermediate values.
    kr=div(sub(K,O),S); er=div(sub(E,O),S)
    residuals={'first_relative':abs(norm(kr)-A)/A,
               'second_relative':abs(norm(sub(er,kr))-B)/B,
               'effective_scaled':norm(sub(er,e))}
    if not all(math.isfinite(v) and v<=REL_ERROR for v in residuals.values()):
        result.update(status='NUMERIC_FAILURE',residuals=residuals); return result
    result.update(status='SOLVED',shape=shape,positions={'O':O,'K':K,'E':E},
                  residuals=residuals,
                  original_error_scaled=norm(sub(er,t)),
                  policy_error_scaled=abs(De-D))
    return result
