"""Eye depth increases with distance, no engine representation or filter assumed."""
from fractions import Fraction as F
near, far, fragment = 2, 10, 4

def alpha(surface):
    return min(F(1),max(F(0),F(surface-fragment,2)))

truth = [alpha(d) for d in [near,far]]
close = [alpha(min(near,far))]*2
remote = [alpha(max(near,far))]*2
average = [alpha(F(near+far,2))]*2
assert truth==[0,1] and close==[0,0] and remote==average==[1,1]
for name, pair in [('per-pixel',truth),('nearest',close),('farthest',remote),('mean',average)]:
    print(name, *(str(x) for x in pair))
