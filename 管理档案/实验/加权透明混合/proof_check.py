"""Original exact rational arithmetic checks for two-layer transparency.

No renderer, shader, image processing, hardware performance, or GPU is tested.
RGB is linear, the background is opaque black, and colors are non-emissive.
Each layer is (straight RGB, alpha, positive order-independent weight).
"""
from fractions import Fraction as F

RED = (F(1), F(0), F(0))
BLUE = (F(0), F(0), F(1))
BLACK = (F(0), F(0), F(0))


def weighted(layers):
    accum = [F(0)] * 3
    denominator, revealage = F(0), F(1)
    for color, alpha, weight in layers:
        for channel in range(3):
            accum[channel] += color[channel] * alpha * weight
        denominator += alpha * weight
        revealage *= 1 - alpha
    if denominator == 0:
        return BLACK, tuple(accum), denominator, revealage
    result = tuple(value / denominator * (1 - revealage) for value in accum)
    return result, tuple(accum), denominator, revealage


def over(back_to_front):
    result = BLACK
    for color, alpha, _ in back_to_front:
        result = tuple(color[c] * alpha + result[c] * (1 - alpha)
                       for c in range(3))
    return result


def show(name, near, far, expected_weighted, expected_over):
    result, accum, denominator, revealage = weighted([near, far])
    assert result == weighted([far, near])[0]
    assert result == expected_weighted
    reference = over([far, near])
    assert reference == expected_over
    print(name)
    print('  A =', accum, 'S =', denominator, 'R =', revealage)
    print('  WBOIT =', result, '; sorted OVER =', reference)


if __name__ == '__main__':
    show('Equal weights (legal simplification, not production tuning)',
         (RED, F(1, 2), F(1)), (BLUE, F(1, 2), F(1)),
         (F(3, 8), F(0), F(3, 8)), (F(1, 2), F(0), F(1, 4)))
    assert over([(RED, F(1, 2), F(1)), (BLUE, F(1, 2), F(1))]) == (F(1, 4), F(0), F(1, 2))
    show('Depth weights 2:1, alpha 3/4 (original teaching function)',
         (RED, F(3, 4), F(2)), (BLUE, F(3, 4), F(1)),
         (F(5, 8), F(0), F(5, 16)), (F(3, 4), F(0), F(3, 16)))
    show('Opaque-front limit, still explicitly in transparent accumulation',
         (RED, F(1), F(2)), (BLUE, F(1, 2), F(1)),
         (F(4, 5), F(0), F(1, 5)), RED)
    show('Coincidental match is not universal: weights 2:1, alpha 1/2',
         (RED, F(1, 2), F(2)), (BLUE, F(1, 2), F(1)),
         (F(1, 2), F(0), F(1, 4)), (F(1, 2), F(0), F(1, 4)))
    show('Unequal-alpha example',
         (RED, F(1, 4), F(1)), (BLUE, F(3, 4), F(1)),
         (F(13, 64), F(0), F(39, 64)), (F(1, 4), F(0), F(9, 16)))
    assert weighted([])[0] == BLACK
    assert weighted([(RED, F(0), F(1))])[0] == BLACK
    print('All rational checks passed. This is not a GPU test.')
