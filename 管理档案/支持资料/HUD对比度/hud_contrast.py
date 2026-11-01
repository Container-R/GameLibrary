"""SDR sRGB teaching arithmetic; no rendering or compliance decisions."""
import math


def _number(value, name, low=0, high=1):
    if type(value) not in (int, float):
        raise TypeError(f"{name} must be a built-in int or float, not bool")
    # Check integer bounds before float conversion (also rejects huge integers).
    if not low <= value <= high or not math.isfinite(value):
        raise ValueError(f"{name} must be finite and within [{low}, {high}]")
    return float(value)


def srgb_decode(channel):
    """Decode one normalized sRGB encoded channel to a linear value."""
    c = _number(channel, "channel")
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def srgb_luminance(red, green, blue):
    """Relative luminance from three encoded sRGB channels, each in [0, 1]."""
    return (0.2126 * srgb_decode(red) + 0.7152 * srgb_decode(green)
            + 0.0722 * srgb_decode(blue))


def panel_luminance(alpha, background_luminance):
    """Black source-over panel on an opaque LINEAR-luminance background."""
    a = _number(alpha, "alpha")
    b = _number(background_luminance, "background_luminance")
    return (1.0 - a) * b


def white_text_contrast(alpha, background_luminance):
    """Opaque white text against the panel result; return a scalar, not a verdict."""
    return 1.05 / (panel_luminance(alpha, background_luminance) + 0.05)


def minimum_panel_alpha(target_ratio, maximum_background_luminance):
    """Float approximation of the analytic minimum, NOT an upward safety bound.

    Target is in [1, 21]. Background maximum is a caller-supplied linear bound
    in [0, 1], not something this helper measures. Near a threshold, rounding
    can put the returned approximation below the exact mathematical minimum.
    """
    t = _number(target_ratio, "target_ratio", 1, 21)
    b = _number(maximum_background_luminance, "maximum_background_luminance")
    if b == 0 or t == 1:
        return 0.0
    if t == 21:
        return 1.0
    return max(0.0, 1.0 - (1.05 / t - 0.05) / b)
