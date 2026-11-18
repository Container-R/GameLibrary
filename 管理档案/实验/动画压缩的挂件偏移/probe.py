import json, math
theta = math.radians(0.1)
cases = dict(origin=(0,0,0), short_perpendicular=(3,0,0), prop_perpendicular=(80,0,0), prop_on_axis=(0,0,80), prop_oblique=(48,0,64))
results={}
for k,(x,y,z) in cases.items():
    # Independently compare direct rotation and analytic chord in the xy plane.
    expected=2*math.hypot(x,y)*math.sin(theta/2)
    after=(math.cos(theta)*x-math.sin(theta)*y,math.sin(theta)*x+math.cos(theta)*y,z)
    delta=math.dist((x,y,z),after)
    assert math.isclose(expected,delta,abs_tol=1e-12)
    results[k]=dict(point_cm=[x,y,z],axis_radius_cm=math.hypot(x,y),error_cm=round(delta,9),within_illustrative_001_cm=delta<=0.01)
assert [v["within_illustrative_001_cm"] for v in results.values()]==[True,True,False,True,False]
print(json.dumps({"rotation_axis":[0,0,1],"rotation_degrees":0.1,"metric":"3D point chord; fixed origin; no scale or translation","result":results},indent=2))
