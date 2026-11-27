from fractions import Fraction as F
from itertools import product

CORNERS = tuple(product((0, 1), repeat=3))
POINT = (F(1, 4), F(1, 2), F(1, 2))

def sample(values, accepted, point=POINT):
    weights = [((point[0] if x else 1 - point[0])
                * (point[1] if y else 1 - point[1])
                * (point[2] if z else 1 - point[2])) if (x, y, z) in accepted
               else F(0) for x, y, z in CORNERS]
    total = sum(weights)
    if total == 0:
        return None
    return sum(w * values[p] for w, p in zip(weights, CORNERS)) / total

def probes(dark):
    return {p: F(1) if p[0] else F(dark) for p in CORNERS}

all_probes = set(CORNERS)
room = {p for p in CORNERS if p[0] == 0}
correct = probes(0)
contaminated = probes(F(1, 4))
cases = [
    ('foreign-probes', correct, all_probes, F(1, 4)),
    ('foreign-probes / mask only', correct, room, F(0)),
    ('foreign-probes / rebake same values', probes(0), all_probes, F(1, 4)),
    ('contaminated-values', contaminated, room, F(1, 4)),
    ('contaminated-values / mask only', contaminated, room, F(1, 4)),
    ('contaminated-values / fix values', correct, room, F(0)),
    ('both causes', contaminated, all_probes, F(7, 16)),
    ('both causes / mask only', contaminated, room, F(1, 4)),
    ('both causes / fix values only', correct, all_probes, F(1, 4)),
    ('both causes / fix both', correct, room, F(0)),
    ('no accepted probes', correct, set(), None),
]
for name, values, accepted, expected in cases:
    actual = sample(values, accepted)
    assert actual == expected, (name, actual, expected)
    print(name, '=>', actual)

# Rejection plus normalization preserves a same-room constant field.
assert sample(probes(F(1, 10)), room) == F(1, 10)
# The unfixed dark-side leak follows x in this fixture, not y or z.
assert sample(correct, all_probes, (F(3, 8), F(1, 3), F(2, 3))) == F(3, 8)
print('constant field and x-gradient controls => passed')
