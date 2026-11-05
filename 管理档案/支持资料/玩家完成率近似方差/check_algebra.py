"""Original deterministic rational-arithmetic checks; no statistical calibration."""
from fractions import Fraction as F


def mean(xs):
    return sum(xs) / len(xs)


def variance(xs):
    return sum((x - mean(xs)) ** 2 for x in xs) / (len(xs) - 1)


def covariance(xs, ys):
    return sum((x - mean(xs)) * (y - mean(ys)) for x, y in zip(xs, ys)) / (len(xs) - 1)


S = list(map(F, [1, 1, 0]))
N = list(map(F, [1, 2, 3]))
K = len(S)
R = sum(S) / sum(N)
U = [s - R * n for s, n in zip(S, N)]
V = variance(U) / (K * mean(N) ** 2)
assert R == F(1, 3)
assert mean([s / n for s, n in zip(S, N)]) == F(1, 2)
assert U == [F(2, 3), F(1, 3), F(-1)] and sum(U) == 0
assert variance(U) == F(7, 9)
assert variance(S) == F(1, 3) and variance(N) == 1
assert covariance(S, N) == F(-1, 2)
assert V == F(7, 108)
assert V == (variance(S) - 2 * R * covariance(S, N) + R**2 * variance(N)) / (K * mean(N)**2)
assert V == F(K, K - 1) * sum(u**2 for u in U) / sum(N)**2
for scale in [F(2), F(100)]:
    assert variance([scale * u for u in U]) / (K * mean([scale * n for n in N])**2) == V
S_equal = list(map(F, [0, 1, 2]))
N_equal = [F(2)] * 3
R_equal = sum(S_equal) / sum(N_equal)
assert variance([s - R_equal * n for s, n in zip(S_equal, N_equal)]) / (3 * mean(N_equal)**2) == variance([s / n for s, n in zip(S_equal, N_equal)]) / 3
print('PASS: deterministic algebra only. R=1/3; sample residual variance=7/9; plug-in variance=7/108. No sampling, coverage, or calibration tested.')
