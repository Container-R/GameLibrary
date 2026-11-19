from fractions import Fraction as F
import json

left = (F(-1), F(-3))
right = (F(1), F(-3))
focus = (F(0), F(5))
pillar = (F(0), F(-3))
combined_r = F(1,5) + F(7,20)  # proxy radius + pillar radius
waypoint = (F(0),F(-2))

def minus(a,b): return tuple(x-y for x,y in zip(a,b))
def plus(a,b): return tuple(x+y for x,y in zip(a,b))
def scale(a,s): return tuple(x*s for x in a)
def dot(a,b): return sum(x*y for x,y in zip(a,b))

def point_segment_distance_sq(q,a,b):
    ab = minus(b,a)
    if a == b:
        aq = minus(a,q)
        return dot(aq,aq)
    t = max(F(0), min(F(1), dot(minus(q,a),ab)/dot(ab,ab)))
    d = minus(q,plus(a,scale(ab,t)))
    return dot(d,d)

def at_focus_depth(origin, direction):
    assert direction[1] > 0
    return plus(origin,scale(direction,(focus[1]-origin[1])/direction[1]))

keep_old_direction = at_focus_depth(right,minus(focus,left))
point_to_anchored_focus = at_focus_depth(right,minus(focus,right))
tests = {
    "start_endpoint": (left,left),
    "end_endpoint": (right,right),
    "direct_lateral_segment": (left,right),
    "detour_left_segment": (left,waypoint),
    "detour_right_segment": (waypoint,right),
    "focus_ray_start_local_segment": (left,focus),
    "focus_ray_end_local_segment": (right,focus),
}
rows={}
for name,(a,b) in tests.items():
    s = point_segment_distance_sq(pillar,a,b)
    # A view ray has zero radius. Path checks use a round camera proxy, not a near-plane shape.
    threshold = F(7,20) if "focus_ray" in name else combined_r
    rows[name] = {"distance_sq":str(s),"threshold_sq":str(threshold**2),"clear":s>threshold**2}
assert keep_old_direction == (2,5) and point_to_anchored_focus == (0,5)
assert rows["start_endpoint"]["clear"] and rows["end_endpoint"]["clear"]
assert not rows["direct_lateral_segment"]["clear"]
assert rows["detour_left_segment"]["distance_sq"] == "1/2" and rows["detour_right_segment"]["clear"]
assert all(rows[name]["clear"] for name in rows if "focus_ray" in name)
# Secondary case: a separate prop in front of the player, far from the camera path.
# Its radius is 1/5; both endpoint rays pass, but the midpoint ray goes through it.
forward_prop = (F(0), F(1))
prop_radius = F(1,5)
focus_clear = {name: point_segment_distance_sq(forward_prop, camera, focus) > prop_radius**2
               for name,camera in (("left",left),("waypoint",waypoint),("right",right))}
assert focus_clear == {"left": True, "waypoint": False, "right": True}
assert all(point_segment_distance_sq(forward_prop,a,b) > (prop_radius+F(1,5))**2
           for a,b in ((left,waypoint),(waypoint,right)))
print(json.dumps({"keep_old_direction_at_target_depth":list(map(str,keep_old_direction)), "reaim_at_saved_world_focus":list(map(str,point_to_anchored_focus)), "clearance":rows, "focus_visibility_with_second_prop":focus_clear},indent=2))
