"""A 1-D symmetric velocity choice, not an ORCA implementation."""
from math import isclose
r, tau, step, preferred = .5, 1.0, .1, 1.0
gap=4.
for k in range(101):
    # gap = center separation - sum of radii
    v=min(preferred,max(0,gap)/(2*tau))
    if k in (0,10,30,60,100):
        print(f"t={k*step:4.1f}s surface_gap={gap:.8f} each_speed={v:.8f}")
    if k==100: break
    gap-=2*v*step
    assert gap>=0
assert v<0.001
# Necessary width at equal longitudinal coordinates for two round agents.
for corridor in (1.8,2.0,2.3):
    lateral_center_separation=corridor-2*r
    clearance=lateral_center_separation-2*r
    print(f"corridor={corridor:.1f} possible_lateral_surface_clearance={clearance:+.2f}")
