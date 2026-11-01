"""Original bounded scalar residual model; no engine or source demo code."""
import math


def number(value, low, high):
    if type(value) not in (int, float):
        raise ValueError('exact built-in int/float required')
    try:
        value = float(value)
    except (ValueError, OverflowError) as error:
        raise ValueError('not representable as finite binary64') from error
    if not math.isfinite(value) or not low <= value <= high:
        raise ValueError('nonfinite or outside declared domain')
    return value


def pair(position, velocity):
    return number(position, -100, 100), number(velocity, -100, 100)


def decay(r, u, rate, dt):
    r, u = pair(r, u)
    rate = number(rate, 0.125, 16)
    dt = number(dt, 0, 8)
    if dt == 0:
        return r, u
    b = u + rate * r
    attenuation = math.exp(-rate * dt)
    return pair((r + b * dt) * attenuation,
                (u - rate * b * dt) * attenuation)


def rebase(output, velocity, target, target_velocity):
    output, velocity = pair(output, velocity)
    target, target_velocity = pair(target, target_velocity)
    return pair(output - target, velocity - target_velocity)


def compose(target, target_velocity, residual, residual_velocity):
    target, target_velocity = pair(target, target_velocity)
    residual, residual_velocity = pair(residual, residual_velocity)
    return pair(target + residual, target_velocity + residual_velocity)
