"""Controlled facing-frame sign change; analytic fixture, no engine renderer."""
from math import sqrt
for x in (0.05, 0.005, 0.0, -0.005, -0.05):
    t = (0.0, 0.0, 1.0)
    v = (x, 0.0, sqrt(1-x*x))
    # t × v with these particular inputs
    raw = (-v[1], v[0], 0.0)
    norm = abs(raw[1])
    y_side = raw[1]/norm if norm else None
    plus_edge_y = 0.2*y_side if y_side is not None else None
    print(f"v.x={x:+.3f}  |T×V|={norm:.3f}  side.y={y_side}  plus_edge.y={plus_edge_y}")
assert (0.005/abs(0.005))*(-0.005/abs(-0.005)) == -1
