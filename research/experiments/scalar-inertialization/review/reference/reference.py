"""Independent protocol-only ODE integration. No author implementation imports."""
import json
import math
from fractions import Fraction

CASES = {'Z': (0., 0., 2.), 'P': (1., 0., 2.), 'V': (0., 1., 2.),
         'G': (1., 2., 2.), 'X': (1., -4., 2.), 'N': (-.75, 1.25, .5),
         'F': (.25, -.5, 8.)}
TIMES = (Fraction(0), Fraction(1, 8), Fraction(1, 2), Fraction(1), Fraction(2))

def derivative(state, rate):
    x, v = state
    return v, -(2 * rate) * v - (rate * rate) * x

def add(a, b, scale):
    return tuple(x + scale*y for x, y in zip(a, b))

def step(state, rate, h):
    k1 = derivative(state, rate)
    k2 = derivative(add(state, k1, h/2), rate)
    k3 = derivative(add(state, k2, h/2), rate)
    k4 = derivative(add(state, k3, h), rate)
    return tuple(state[j] + h*(k1[j] + 2*k2[j] + 2*k3[j] + k4[j])/6 for j in (0, 1))

def integrate(initial, rate, duration, denominator):
    n = duration * denominator
    if n.denominator != 1:
        raise ValueError('unaligned time')
    state = initial
    for _ in range(n.numerator):
        state = step(state, rate, 1/denominator)
    if not all(math.isfinite(x) for x in state):
        raise ValueError('nonfinite')
    return state

def target(name, time):
    if name == 'A': return .4*time, .4, 0.
    if name == 'B': return 1 + .5*math.sin(2*time), math.cos(2*time), -2*math.sin(2*time)
    if name == 'C': return -.25 + .2*time, .2, 0.
    raise ValueError(name)

def transition_reference(denominator):
    old = 'A'
    residual = (0., 0.)
    previous = Fraction(0)
    records = []
    for time, new in ((Fraction(3, 4), 'B'), (Fraction(9, 8), 'C')):
        residual = integrate(residual, 2., time - previous, denominator)
        old_target, new_target = target(old, float(time)), target(new, float(time))
        before = tuple(old_target[j] + residual[j] for j in (0, 1))
        rebased = tuple(before[j] - new_target[j] for j in (0, 1))
        after = tuple(new_target[j] + rebased[j] for j in (0, 1))
        acc_before = old_target[2] + derivative(residual, 2.)[1]
        acc_after = new_target[2] + derivative(rebased, 2.)[1]
        records.append({'time': str(time), 'old': old, 'new': new,
                        'old_residual': residual, 'new_residual': rebased,
                        'before': before, 'after': after,
                        'acceleration_before': acc_before, 'acceleration_after': acc_after,
                        'raw_only_rebase_jump': tuple(-x for x in residual)})
        residual, old, previous = rebased, new, time
    final_residual = integrate(residual, 2., Fraction(2) - previous, denominator)
    final_target = target('C', 2.)
    return {'transitions': records, 'final_residual': final_residual,
            'final_output': tuple(final_target[j] + final_residual[j] for j in (0, 1))}

def main():
    output = {'scope': 'protocol-only independent RK4; not author acceptance',
              'steps': {}, 'transition_steps': {}}
    for denominator in (128, 256):
        output['steps'][str(denominator)] = {
            name: {str(t): integrate((x, v), rate, t, denominator) for t in TIMES}
            for name, (x, v, rate) in CASES.items()}
        output['transition_steps'][str(denominator)] = transition_reference(denominator)
    print(json.dumps(output, indent=2, allow_nan=False))

if __name__ == '__main__': main()
