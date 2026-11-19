"""One-axis numeric model of render coordinates and periodic material anchoring."""
import json
import struct

def f32(x):
    return struct.unpack("<f",struct.pack("<f",x))[0]

def ulp32(x):
    bits = struct.unpack("<I",struct.pack("<f",x))[0]
    return struct.unpack("<f",struct.pack("<I",bits+1))[0] - f32(x)

origin = 10_000_000.0 # units chosen for demonstration, not any engine's distance.
anchors = [origin, origin+0.125]
vertices = [origin+0.125, origin+0.375]
period = 0.75
bad = [f32(f32(v)-f32(anchors[0])) for v in vertices]
good = [f32(v-anchors[0]) for v in vertices]
p = vertices[0]
relative_only = [f32(p-c) % period for c in anchors]
phase_anchored = [
    f32(f32(p-c)+f32(c % period)) % period for c in anchors
]
assert ulp32(origin) == 1.0 and bad == [0.0,0.0] and good == [0.125,0.375]
assert relative_only == [0.125,0.0] and phase_anchored == [0.375,0.375]
assert phase_anchored == [p % period] * 2
far_r = 1_000_000.0
fine_period = 0.01
fine_phases = [0.003,0.008]
assert ulp32(far_r) == 0.0625
assert [f32(far_r+a) for a in fine_phases] == [far_r,far_r]
print(json.dumps({"origin":origin,"ulp32_at_origin":ulp32(origin),
                  "world_rounds_before_subtract":bad,"subtract_before_rounding":good,
                  "fixed_point_material_phase_relative_only":relative_only,
                  "fixed_point_material_phase_origin_anchored":phase_anchored,
                  "large_relative_still_loses_phase":{
                      "r":far_r,"ulp32":ulp32(far_r),"period":fine_period,
                      "input_origin_phases":fine_phases,"f32_r_plus_phase":[f32(far_r+a) for a in fine_phases]}},indent=2))
