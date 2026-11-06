"""Author's original exact arithmetic and cache-policy model, NOT Box2D/GJK.
No library load, upstream build, convergence/precision or performance validation.
"""
from fractions import Fraction as Q
import json


def add(x, y): return tuple(a+b for a,b in zip(x,y))
def sub(x, y): return tuple(a-b for a,b in zip(x,y))
def rotation(turns, p):
    x, y = p
    return [(x,y),(-y,x),(-x,-y),(y,-x)][turns % 4]
def world(pos, turns, p): return add(pos, rotation(turns, p))
def inverse_world(pos, turns, p): return rotation(-turns, sub(p, pos))
def relative(pa, qa, pb, qb): return rotation(-qa, sub(pb, pa)), (qb-qa) % 4

def ordered_key(a, b, rev_a, rev_b, mode='SurfaceGap'):
    return a, b, rev_a, rev_b, mode

def can_reuse(saved_key, request_key, count, indices_a, indices_b, n_a, n_b, continuous):
    return (saved_key == request_key and continuous and 0 <= count <= 3 and
            all(0 <= i < n_a for i in indices_a[:count]) and
            all(0 <= i < n_b for i in indices_b[:count]))

def serialize(value):
    if isinstance(value, Q): return str(value)
    if isinstance(value, (list, tuple)): return [serialize(x) for x in value]
    if isinstance(value, dict): return {k: serialize(v) for k,v in value.items()}
    return value

pa=(Q(10), Q(5)); qa=1; qb=2; center=(Q(1),Q(0)); rows=[]
for x in (Q(3),Q(11,4),Q(5,2)):
    pb=(Q(11),Q(5)+x)
    rel_p, rel_q=relative(pa,qa,pb,qb)
    c=world(rel_p,rel_q,center)
    assert rel_p==(x,Q(-1)) and rel_q==1 and c==(x,Q(0))
    assert world(pa,qa,c)==world(pb,qb,center)
    core_a=(Q(2),Q(0)); core_b=c
    d=x-Q(2)
    a=(Q(9,4),Q(0)); b=(x-Q(1,2),Q(0))
    gap=max(Q(0),d-Q(1,4)-Q(1,2))
    wa=world(pa,qa,a); wb=world(pa,qa,b)
    n=rotation(qa,(Q(1),Q(0)))
    positive=gap>0
    rows.append({'B_world_origin':pb,'B_to_A_translation':rel_p,
      'B_to_A_quarter_turns':rel_q,'B_center_in_A':c,'core_gap':d,
      'ordinary_branch_gap':gap,'ordinary_branch_points_A':(a,b),
      'ordinary_branch_point_length':abs(b[0]-a[0]),
      'consumer_result':'PositiveGap' if positive else 'ZeroDistance',
      'consumer_world_points':(wa,wb) if positive else None,
      'consumer_normal_world':n if positive else None})
    if positive:
        assert wa==(Q(10),Q(29,4)) and wb==(Q(10),Q(15,2))
        assert n==(Q(0),Q(1))
        # Swap ordering: A becomes former B, outputs are in former B's local frame.
        a2=inverse_world(pb,qb,wb); b2=inverse_world(pb,qb,wa)
        assert world(pb,qb,a2)==wb and world(pb,qb,b2)==wa
        assert a2==(Q(1),Q(1,2)) and b2==(Q(1),Q(3,4))
        wrong=world(pb,qb,b)
        assert wrong==(Q(17,2),Q(8))
assert [r['ordinary_branch_gap'] for r in rows]==[Q(1,4),Q(0),Q(0)]
assert rows[2]['ordinary_branch_point_length']==Q(1,4)
assert Q(1,4)<=Q(3,10) and not Q(1,4)<=Q(1,5)
# Interior point: only containment and zero mathematical solid distance; no native witness prediction.
assert world(*relative(pa,qa,(Q(11),Q(6)),qb), center)==(Q(1),Q(0))

A=('shape-slot-A',1); B=('shape-slot-B',4); old_key=ordered_key(A,B,12,8)
cases=[]
for label,key,continuous,n_a,idx_a,want in [
 ('same_pair_adjacent_pose',old_key,True,4,[1,2],True),
 ('swapped_order',ordered_key(B,A,8,12),True,1,[0,0],False),
 ('geometry_changed',ordered_key(A,B,13,8),True,3,[1,2],False),
 ('same_slot_new_generation',ordered_key(('shape-slot-A',2),B,12,8),True,4,[1,2],False),
 ('mode_changed',ordered_key(A,B,12,8,'CoreDistance'),True,4,[1,2],False),
 ('discontinuous_pose',old_key,False,4,[1,2],False),
 ('index_range_guard',old_key,True,3,[1,3],False),
]:
    actual=can_reuse(old_key,key,2,idx_a,[0,0],n_a,1,continuous)
    assert actual==want
    cases.append({'case':label,'reuse':actual})
result={'kind':'exact_original_geometry_and_application_policy_only',
        'box2d_or_gjk_executed':False,'result':'passed',
        'geometry_rows':rows,'cache_policy_cases':cases,
        'limits':['Does not execute the article pseudocode against the Box2D library.',
                  'Does not verify native output, rounding, convergence, or performance.',
                  'Native integration tests remain to be performed by an adopting project.']}
print(json.dumps(serialize(result), ensure_ascii=False, indent=2))
