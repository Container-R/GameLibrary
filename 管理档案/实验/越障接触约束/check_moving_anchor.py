import json
# Centimetres, XY; orthonormal quarter-turn transforms; no collision or IK.
def transform(origin, rot, p):
    x,y=p
    for _ in range(rot): x,y=-y,x
    return (origin[0]+x,origin[1]+y)
local=(30,10)
frames=[((100,200),0),((112,200),0),((112,212),1)]
frozen=transform(*frames[0],local)
rows=[]
for origin,rot in frames:
    expected=transform(origin,rot,local)
    wrongly_add=(origin[0]+local[0],origin[1]+local[1])
    err=lambda p: [p[0]-expected[0],p[1]-expected[1]]
    rows.append({'anchor_world_cm':expected,'frozen_world_error_cm':err(frozen),'translate_only_error_cm':err(wrongly_add),'fresh_component_transform_error_cm':err(expected)})
assert [r['frozen_world_error_cm'] for r in rows]==[[0,0],[-12,0],[28,-32]]
assert [r['translate_only_error_cm'] for r in rows]==[[0,0],[0,0],[40,-20]]
print(json.dumps(rows,indent=2))
