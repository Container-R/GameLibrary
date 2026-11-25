"""Analytical sRGB reference, not a GPU sampling test."""
from math import isclose

def decode(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

print("byte  linear_UNORM  sRGB_RGB   alpha_either")
for b in (0, 32, 64, 128, 192, 224, 255):
    x = b / 255
    print(f"{b:4d}   {x:10.6f}   {decode(x):8.6f}   {x:12.6f}")
assert isclose(decode(128 / 255), 0.2158605001, abs_tol=1e-8)
