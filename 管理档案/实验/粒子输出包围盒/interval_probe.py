"""One-axis interval model: orthographic side crop; other axes wholly in view."""
import json

camera=(0,4)
center=-2
updated_extent=0.25       # footprint known when bounds are recorded
output_offset=1.0        # render-only pivot/position adjustment
output_extent=2.0        # render-only stretched half-width
def range_at(x,r): return [x-r,x+r]
def touches(a,b): return max(a[0],b[0]) <= min(a[1],b[1])
updated=range_at(center,updated_extent)
output=range_at(center+output_offset,output_extent)
one_sided=[max(0,updated[0]-output[0]),max(0,output[1]-updated[1])]
assert one_sided==[0.75,2.75]
minimal=[updated[0]-one_sided[0],updated[1]+one_sided[1]]
symmetric=range_at(center,updated_extent+max(one_sided))
assert not touches(updated,camera) and touches(output,camera)
assert touches(minimal,camera) and touches(symmetric,camera)
extra_view=(-5,-4)
assert not touches(output,extra_view) and touches(symmetric,extra_view)
print(json.dumps(dict(camera=camera, update_bound=updated, rendered=output,
  extension_neg_pos=one_sided, exact_bounds=minimal, symmetric_bounds=symmetric,
  camera_admitted_before=touches(updated,camera), camera_admitted_after=touches(minimal,camera),
  oversized_extra_admission=extra_view),indent=2))
