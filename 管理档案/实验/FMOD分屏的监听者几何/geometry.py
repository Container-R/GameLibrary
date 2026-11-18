import json, math
source = (0, 0)  # x right, z forward; both listeners face +z
A=(-3,-4)
cases=(
    ("same_side", {"A":A,"B":(-6,-8)}, {"A","B"}),
    ("opposing_sides", {"A":A,"B":(6,-8)}, {"A","B"}),
    ("b_outside", {"A":A,"B":(18,-24)}, {"A","B"}),
    ("b_only", {"A":A,"B":(6,-8)}, {"B"})
)
report={}
for k, listeners, mask in cases:
    out={}
    for name, (x,z) in listeners.items():
        dx,dz=source[0]-x,source[1]-z
        dist=math.hypot(dx,dz)
        if name in mask and dist<20:
            out[name]={"distance":dist,"side":"right" if dx>0 else "left" if dx<0 else "center"}
    report[k]={"in_range_and_in_mask":out,"nearest_in_this_example":min(out,key=lambda i:out[i]["distance"])}
assert [r["nearest_in_this_example"] for r in report.values()] == ["A","A","A","B"]
assert [r["in_range_and_in_mask"].get("B",{}).get("side") for r in report.values()]==["right","left",None,"left"]
print(json.dumps(report,indent=2))
