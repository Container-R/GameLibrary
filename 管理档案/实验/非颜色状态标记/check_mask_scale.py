from fractions import Fraction as F
import json

def interval_overlap(a,b,c,d):
    return max(F(0), min(b,d)-max(a,c))

# Exact box filtering of a bar between the 1/4 and 3/4 positions horizontally;
# the visual asset path is deliberately modeled as alpha >= 1/2 -> solid.
def box_sample(n, thickness, dy):
    ax,bx = F(1,4),F(3,4)
    ay,by = F(1,2)-thickness/2+dy,F(1,2)+thickness/2+dy
    cover = [n*n*interval_overlap(F(x,n),F(x+1,n),ax,bx)*
                  interval_overlap(F(y,n),F(y+1,n),ay,by)
             for y in range(n) for x in range(n)]
    return {"max_alpha":str(max(cover)),
            "nonzero_pixels_before_cut":sum(a>0 for a in cover),
            "solid_pixels_after_half_alpha_cut":sum(a>=F(1,2) for a in cover)}

rows = {}
for n in (24,12):
    rows[str(n)] = {
        "thin_aligned_between_rows":box_sample(n,F(1,20),F(0)),
        "thin_offset_half_pixel":box_sample(n,F(1,20),F(1,2*n)),
        "wide_aligned_between_rows":box_sample(n,F(1,6),F(0)),
    }
assert rows["24"]["thin_aligned_between_rows"]["solid_pixels_after_half_alpha_cut"] == 24
assert rows["12"]["thin_aligned_between_rows"]["max_alpha"] == "3/10"
assert rows["12"]["thin_aligned_between_rows"]["solid_pixels_after_half_alpha_cut"] == 0
assert rows["12"]["thin_offset_half_pixel"]["solid_pixels_after_half_alpha_cut"] == 6
assert rows["12"]["wide_aligned_between_rows"]["solid_pixels_after_half_alpha_cut"] == 12
print(json.dumps(rows,indent=2))
