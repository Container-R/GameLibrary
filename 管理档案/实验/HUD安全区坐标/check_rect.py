"""Synthetic rectangles, physically common reference after coordinate conversion."""
import json
from fractions import Fraction as F


def intersect(a,b):
    return max(a[0],b[0]),max(a[1],b[1]),min(a[2],b[2]),min(a[3],b[3])


def inverse(rect, viewport, logical):
    a,b,c,d = intersect(rect, viewport)
    if a>=c or b>=d:
        return None
    x,y,w,h = viewport
    return tuple(int(v) if v.denominator==1 else str(v) for v in
                 (F((a-x)*logical[0],w-x),F((b-y)*logical[1],h-y),
                  F((c-x)*logical[0],w-x),F((d-y)*logical[1],h-y)))


def lower_to_upper(rect, h):
    x,y,w,a = rect
    return (x,h-y-a,x+w,h-y)


viewport = (240,0,2160,1080)
logical = (960,540)
window_safe = lower_to_upper((100,52,2210,996),1080)
inside = inverse(window_safe, viewport, logical)
assert window_safe==(100,32,2310,1028) and inside==(0,16,960,514)
intrudes = inverse((300,32,2310,1028), viewport, logical)
assert intrudes==(30,16,960,514)
cropped_window = (0,0,2210,996)
assert inverse(cropped_window,cropped_window,(1105,498))==(0,0,1105,498)
assert inverse((0,0,100,100),viewport,logical) is None
print(json.dumps({"scope":"synthetic coordinate geometry only",
                  "player_window_safe_top_left":window_safe,
                  "viewport":viewport,"logical_bounds":inside,
                  "real_left_intrusion_in_logical_bounds":intrudes,
                  "preclipped_window_logical_safe_bounds":[0,0,1105,498],
                  "no_intersection":"do not invent a usable rectangle"}, indent=2))
