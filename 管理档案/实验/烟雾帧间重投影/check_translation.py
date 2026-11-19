from fractions import Fraction as F
import json

# Exact horizontal alpha profile of a deliberately sparse flipbook.
start = {2: F(1)}
end = {6: F(1)}
truth = {4: F(1)}
t = F(1, 2)

def sample(frame, x):
    i = x // 1
    f = x - i
    return frame.get(i, 0) * (1-f) + frame.get(i+1, 0) * f

def interpolate(frame_a, frame_b, displacement, t):
    # Const translation only. Inverse sample so the feature moves forward.
    return {x: (1-t) * sample(frame_a, x-t*displacement)
               + t * sample(frame_b, x+(1-t)*displacement)
            for x in range(10)}

def report(row):
    return {
        "nonzero_x_alpha": [[x,str(a)] for x,a in row.items() if a],
        "mass": str(sum(row.values())),
        "centroid_x": str(sum(x*a for x,a in row.items()) / sum(row.values())),
        "l1_to_truth_midpoint": str(sum(abs(a-truth.get(x,0)) for x,a in row.items()))
    }

rows = {name:report(interpolate(start,end,d,t))
        for name,d in {"unwarped":0,"correct":4,"wrong_sign":-4,"half_scale":2}.items()}
assert all(r["centroid_x"]=="4" and r["mass"]=="1" for r in rows.values())
assert rows["unwarped"]["nonzero_x_alpha"] == [[2,"1/2"],[6,"1/2"]]
assert rows["correct"]["l1_to_truth_midpoint"] == "0"
assert rows["wrong_sign"]["nonzero_x_alpha"] == [[0,"1/2"],[8,"1/2"]]
assert rows["half_scale"]["nonzero_x_alpha"] == [[3,"1/2"],[5,"1/2"]]
print(json.dumps(rows,indent=2))
