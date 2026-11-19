#!/usr/bin/env python3
"""Exact discrete SE(2) reference; no engine, interpolation, or physics.

Column vectors: T=(quarter_turns, translation), T*x=R*x+t.
A*B applies B first, then A. Delta is body-relative U(a)^-1*U(b),
so U(a)*D(a,b)=U(b) and D(a,b)*D(b,c)=D(a,c).
The two-tick authored loop has P(0)=P0 (not identity), P(1)=P0*Q1,
P(2)=P0*C. Unwrapped U(2*n+p)=P0*C**n*Q[p], p in {0,1}.
Exact endpoints belong to the next cycle, phase zero. Negative ticks use
Python floor divmod and inverse cycle powers, not truncation toward zero.
"""
import json
from dataclasses import dataclass


def rotate(r, p):
    x, y = p
    return ((x, y), (-y, x), (-x, -y), (y, -x))[r % 4]


@dataclass(frozen=True)
class Pose:
    r: int = 0
    x: int = 0
    y: int = 0

    def __mul__(self, other):
        x, y = rotate(self.r, (other.x, other.y))
        return Pose((self.r + other.r) % 4, self.x + x, self.y + y)

    def inverse(self):
        r = (-self.r) % 4
        x, y = rotate(r, (-self.x, -self.y))
        return Pose(r, x, y)

    def power(self, n):
        base = self if n >= 0 else self.inverse()
        result = Pose()
        for _ in range(abs(n)):
            result = result * base
        return result

    def record(self):
        return {"rotation_degrees": self.r * 90, "translation": [self.x, self.y]}


IDENTITY = Pose()
P0 = Pose(1, 3, -2)
C = Pose(1, 2, 1)
Q = (IDENTITY, Pose(0, 1, 0))
PERIOD = 2


def unwrapped(t):
    n, phase = divmod(t, PERIOD)
    return P0 * C.power(n) * Q[phase]


def wrapped(t):
    return P0 * Q[t % PERIOD]


def delta(a, b):
    return unwrapped(a).inverse() * unwrapped(b)


def main():
    ticks = list(range(-4, 11))
    counts = {"pose_reconstruction": 0, "reverse_inverse": 0,
              "partition_composition": 0, "exact_endpoints": 0}
    for a in ticks:
        for b in ticks:
            d = delta(a, b)
            assert unwrapped(a) * d == unwrapped(b)
            counts["pose_reconstruction"] += 1
            assert delta(b, a) == d.inverse()
            counts["reverse_inverse"] += 1
            for c in ticks:
                assert d * delta(b, c) == delta(a, c)
                counts["partition_composition"] += 1
    for n in range(-4, 9):
        assert unwrapped(2*n) == P0 * C.power(n)
        assert delta(0, 2*n) == C.power(n)
        counts["exact_endpoints"] += 1

    # Explicit expectations independent of the loop-unwrapping expression.
    expected = {0: Pose(1, 3, -2), 1: Pose(1, 3, -1),
                2: Pose(2, 2, 0), 3: Pose(2, 1, 0),
                4: Pose(3, 0, -1), 6: Pose(0, 1, -3),
                8: Pose(1, 3, -2)}
    for t, p in expected.items():
        assert unwrapped(t) == p
    assert C.power(2) == Pose(2, 1, 3)
    assert C.power(4) == IDENTITY
    assert delta(1, 3) == Pose(1, 1, 2)

    wrapped_delta = wrapped(1).inverse() * wrapped(3)
    assert wrapped_delta == IDENTITY and wrapped_delta != delta(1, 3)
    raw_difference = [unwrapped(3).x - unwrapped(1).x,
                      unwrapped(3).y - unwrapped(1).y]
    assert raw_difference == [-2, 1]  # world displacement, not body delta
    assert raw_difference != [delta(1, 3).x, delta(1, 3).y]
    wrong_order = P0 * Q[1] * C
    assert wrong_order == Pose(2, 2, 1) and wrong_order != unwrapped(3)
    wrong_initial = C
    assert wrong_initial != unwrapped(2)
    wrong_linear_cycles = Pose(2, 4, 2)
    assert wrong_linear_cycles != C.power(2)

    result = {
        "scope": "Exact integer 2D rigid transforms at discrete integer ticks only; no engine, interpolation, collision, or performance test.",
        "convention": "Column vectors; A*B applies B then A; D(a,b)=inverse(U(a))*U(b).",
        "period_ticks": PERIOD,
        "initial_authored_pose": P0.record(),
        "cycle_relative_transform": C.record(),
        "authored_samples_including_end": [P0.record(), (P0*Q[1]).record(), (P0*C).record()],
        "unwrapping": "divmod(t,2)=(n,p); U(t)=P0*C^n*Q[p]. End tick 2 uses n=1,p=0, not the start pose.",
        "assertion_counts": counts,
        "explicit_pose_assertions": len(expected),
        "poses": [{"tick": t, **p.record()} for t, p in expected.items()],
        "cross_wrap_1_to_3": {"correct_body_delta": delta(1, 3).record(),
                              "wrapped_endpoint_delta": wrapped_delta.record(),
                              "world_translation_subtraction": raw_difference},
        "noncommuting_order_at_tick_3": {"correct_P0_C_Q1": unwrapped(3).record(),
                                         "wrong_P0_Q1_C": wrong_order.record()},
        "two_cycles": {"correct": C.power(2).record(), "wrong_add_translation_twice": wrong_linear_cycles.record()},
        "four_cycles": C.power(4).record(),
        "all_assertions_passed": True,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2) + "\n", end="")


if __name__ == "__main__":
    main()
