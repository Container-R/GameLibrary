"""Known horizontal/vertical registration errors and independent imagery controls."""
from fractions import Fraction as Q
import json
from statistics import fmean

# Positive delta means B pulls from x+delta, not B moved visibly to the right.
shift = Q(4, 5)
bias = Q(3, 25)
grades = [Q(1,4), Q(0), -Q(1,4)]
residual = [g * shift + bias for g in grades]
recovered_shift = (residual[0] - residual[2]) / (grades[0]-grades[2])
recovered_bias = residual[1]
competing_on_first_slope = grades[0] * 0 + residual[0]
assert recovered_shift == shift and recovered_bias == bias
assert competing_on_first_slope == residual[0] and competing_on_first_slope != bias

# 1D synthetic image line and first difference, indexed by World X in meters.
# Same fixed geometry in all three cases. The dark seam starts at x=-1.
x = list(range(-5, 6))
height = [0, 0, 0, 0, 0.5, 1, 0.5, 0, 0, 0, 0]
base = [16 if i < -1 else 232 for i in x]
shifted = [16 if i < 0 else 232 for i in x]
blurred = [round(fmean(base[max(0,i-1):i+2])) for i in range(len(x))]
def inspect(luma):
    step = [b-a for a,b in zip(luma, luma[1:])]
    max_step = max(step)
    # Brightness transition position uses derivative centroid, not a broken tie.
    centroid = sum(Q(x[i]+x[i+1], 2)*v for i,v in enumerate(step))/sum(step)
    return {"geometry_peak_x_m": x[height.index(max(height))], "image_edge_x_m": str(centroid),
            "strongest_one_pixel_luma_step": max_step, "luma": luma}
results = {name: inspect(samples) for name, samples in (("base",base),("image_shift_only",shifted),("image_blur_only",blurred))}
assert [v["geometry_peak_x_m"] for v in results.values()] == [0,0,0]
assert [v["image_edge_x_m"] for v in results.values()] == ["-3/2","-1/2","-3/2"]
assert [v["strongest_one_pixel_luma_step"] for v in results.values()] == [216,216,72]
out={"opposed_slopes":{"grades":[str(g) for g in grades],"B_minus_A_m":[str(v) for v in residual],
                      "pull_shift_m":str(recovered_shift),"height_bias_m":str(recovered_bias),
                      "single_slope_false_bias_if_shift_assumed_zero_m":str(competing_on_first_slope)},
     "same_geometry_different_image":{"x_m":x,"height_m":height,"results":results}}
print(json.dumps(out,indent=2))
