"""Exact arithmetic for the article's original coordinates, not mesh/engine tests.
Run: python3 verify_geometry.py
Uses only the Python 3 standard library. Prints JSON to stdout; writes no files.
The general impossibility claim is proved in the article, not by this enumeration.
"""
from fractions import Fraction as F
from itertools import combinations, product
import json

FLOOR=F(2,5)
def add(a,b): return tuple(x+y for x,y in zip(a,b))
def sub(a,b): return tuple(x-y for x,y in zip(a,b))
def neg(a): return tuple(-x for x in a)
def rot(v,degrees):
    x,y,z=v
    return {0:(x,y,z),90:(-y,x,z),180:(-x,-y,z),270:(y,-x,z)}[degrees]

ports={
    'W':((-2,0,FLOOR),(-1,0,0)),
    'E':((2,0,FLOOR),(1,0,0)),
    'N':((0,2,FLOOR),(0,1,0)),
}
def transform_port(name, angle, pivot):
    q,n=ports[name]
    s=(-n[1],n[0],0)  # u cross n, u=(0,0,1)
    boundary=[add(q,add(tuple(a*i for i in s),(0,0,b)))
              for a,b in product((-1,1),(0,F(14,5)))]
    return {'point':add(rot(q,angle),pivot),'normal':rot(n,angle),
            'up':(0,0,1),'corners':frozenset(add(rot(v,angle),pivot) for v in boundary)}

def connect(a,b):
    return a['point']==b['point'] and a['normal']==neg(b['normal']) and a['up']==b['up'] and a['corners']==b['corners']

def box(pivot,half):
    x,y,z=pivot
    return ((x-half,x+half),(y-half,y+half),(z,z+F(18,5)))
def overlap(a,b):
    return all(max(lo1,lo2)<min(hi1,hi2) for (lo1,hi1),(lo2,hi2) in zip(a,b))

# Type, angle, pivot, incoming local port, outgoing local port.
inputs=[('C',180,(-6,2,0),'W','N'),('S',90,(-6,-2,0),'E','W'),
        ('C',270,(-6,-6,0),'W','N'),('S',0,(-2,-6,0),'W','E'),
        ('C',0,(2,-6,0),'W','N')]
room_w=transform_port('W',0,(-2,2,0)) # q=(-4,2,.4)
room_s=transform_port('E',270,(2,-2,0)) # q=(2,-4,.4), normal south
route=[]
previous=room_w
boxes=[box((0,0,0),4)]
for kind,angle,pivot,pin,pout in inputs:
    a=transform_port(pin,angle,pivot)
    b=transform_port(pout,angle,pivot)
    assert connect(previous,a)
    assert all(v%2==0 for v in pivot[:2]) and pivot[2]==0
    boxes.append(box(pivot,2))
    route.append({'piece':kind,'rotation':angle,'pivot':pivot,
                  'input':a['point'],'input_normal':a['normal'],
                  'output':b['point'],'output_normal':b['normal']})
    previous=b
assert connect(previous,room_s)
assert not any(overlap(a,b) for a,b in combinations(boxes,2))

# Confirm each legal local port is 2*n from the pivot in XY.
# This finite check supports, but does not replace, the general chain proof.
for names in [('W','E'),('W','N')]:
    for angle in [0,90,180,270]:
        for name in names:
            p=transform_port(name,angle,(0,0,0))
            assert p['point'][:2]==tuple(2*n for n in p['normal'][:2])
first_center=(-6,0)
assert tuple(v%4 for v in first_center)==(2,0)
north_exit_class=(2,2)
target_class=(0,0)
assert north_exit_class!=target_class

# Introduce a defective world-space outlet on piece 3, not a new valid standard part.
offset=(F(1,5),0,0)
defective_exit=add(route[2]['output'],offset)
following=[add(route[i]['pivot'],offset) for i in (3,4)]
following_end=add(route[-1]['output'],offset)
assert sub(following_end,room_s['point'])==offset
assert sub(defective_exit,route[3]['input'])==offset
assert all(p[0]%2!=0 for p in following)

upper_base=F(18,5)
floor={'lower_walk_z':FLOOR,'upper_base_z':upper_base,
       'upper_walk_z':upper_base+FLOOR,'slab_bottom_z':upper_base,
       'slab_top_z':upper_base+FLOOR,'slab_thickness':FLOOR,
       'lower_structural_clear_height':upper_base-FLOOR,
       'door_clear_height':F(14,5)}
assert floor['lower_structural_clear_height']==F(16,5)
assert floor['upper_walk_z']==4
# Demonstrate the two different predicates, with declared coordinates only.
raised_actual_floor=F(3,5)
assert raised_actual_floor!=FLOOR
stale_marker=FLOOR
assert stale_marker==ports['W'][0][2]
assert stale_marker!=raised_actual_floor

def serial(v):
    if isinstance(v,F): return str(v)
    if isinstance(v,(tuple,list)): return [serial(x) for x in v]
    if isinstance(v,dict): return {k:serial(x) for k,x in v.items()}
    return v
out={'scope':'Original exact-coordinate teaching model only',
     'units':'metres',
     'dcc_engine_game_or_human_tests':False,
     'checks':{'five_piece_seams_point_normal_up_and_rectangle':True,
               'legal_pivots':True,'all_six_footprint_interiors_disjoint':True,
               'all_legal_port_offsets_match_two_times_normal':True,
               'center_room_impossibility':'Invariant proof in article; not finite search',
               'actual_mesh_or_collision_checked':False},
     'route':route,'center_room_pivot_class':[2,0],
     'center_room_north_exit_class':north_exit_class,'center_room_target_class':target_class,
     'defect':{'third_piece_actual_exit':defective_exit,'following_pivots':following,
               'following_end':following_end,'end_error':offset,
               'on_grid_local_seam_error':offset,'following_pivots_off_grid':True},
     'floor':floor,
     'stale_marker_example':{'actual_floor':raised_actual_floor,'marker':stale_marker,
                            'port_data_comparison_passes':True,'geometry_vs_marker_passes':False}}
print(json.dumps(serial(out),ensure_ascii=False,indent=2))
