"""Linear source-over reference, two independent pixels, opaque black background."""
from fractions import Fraction as F

A = (F(1), F(0), F(0))
B = (F(0), F(0), F(1))
colors = {"A": A, "B": B}

def solve(back_to_front):
    out = (F(0),) * 3
    for particle in back_to_front:
        out = tuple((s+d)/2 for s, d in zip(colors[particle], out))
    return out

# Depth increases away from camera. Each sample sees one A and one B;
# local sorting within A/B cannot affect their relative order at either sample.
samples = {"left": {"A": 4, "B": 2}, "right": {"A": 1, "B": 3}}
ref = {k: solve(sorted(v, key=lambda p: -v[p])) for k, v in samples.items()}
assert ref["left"] == (F(1,4), F(0), F(1,2))
assert ref["right"] == (F(1,2), F(0), F(1,4))
for name, order in [("A_then_B", "AB"), ("B_then_A", "BA")]:
    candidate = solve(order)
    wrong = [k for k, v in ref.items() if v != candidate]
    assert len(wrong) == 1
    print(name, "candidate", tuple(map(str, candidate)), "wrong_at", wrong)
print("reference", {k: tuple(map(str, v)) for k, v in ref.items()})
