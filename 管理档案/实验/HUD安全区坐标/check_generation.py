"""Synthetic rotation pairing and same-obstruction composition controls."""
from collections import namedtuple
from fractions import Fraction
import json

Frame = namedtuple("Frame", "epoch size rect")

def reduce(safe, viewport):
    if safe.epoch != viewport.epoch or safe.size != viewport.size:
        return None
    a,b,c,d = viewport.rect
    x0,y0,x1,y1 = safe.rect
    n=(max(a,x0)-a,max(b,y0)-b,min(c,x1)-a,min(d,y1)-b)
    return n if n[0]<n[2] and n[1]<n[3] else None

portrait = Frame(1,(1080,2400),(0,80,1075,2340))
landscape = Frame(2,(2400,1080),(8,0,2400,1080))
canvas = Frame(2,(2400,1080),(0,0,2400,1080))
assert reduce(portrait, canvas) is None
fresh=reduce(landscape,canvas)
assert fresh == (8,0,2400,1080)
pretend_fresh = portrait._replace(epoch=2,size=(2400,1080))
mixed=reduce(pretend_fresh,canvas)
assert mixed==(0,80,1075,1080)
right=Fraction(mixed[2],canvas.size[0])

# Full local content host (960x540): platform already spends 30 units on left.
# Child is positioned in parent's local coordinates, not the stale original root.
parent_inner = (30,0,960,540)
child_correct = (0,0,930,540)
child_double = (30,0,930,540)
assert parent_inner[0]+child_correct[0]==30
assert parent_inner[0]+child_double[0]==60

# Reflect two y corners, then reorder; reflect-min-and-reuse-height is invalid.
h=2200
low_min,low_height=24,2100
top=h-(low_min+low_height)
bottom=h-low_min
assert (top,bottom)==(76,2176)
bad=(h-low_min,h-low_min+low_height)
assert bad==(2176,4276)

print(json.dumps({"scope":"synthetic geometry, not a device rotation trace",
                  "coherent_landscape":fresh,"mixed_but_nonempty":mixed,
                  "mixed_right_percent":round(100*float(right),3),
                  "same_generation_guard_rejects_mixed":True,
                  "same_obstruction_world_left_once":30,
                  "same_obstruction_world_left_twice":60,
                  "correct_reflected_vertical_bounds":[top,bottom],
                  "reflected_lower_edge_mistaken_for_top":bad},indent=2))
