import itertools
import json

def decode_srgb(x):
    x = x / 255
    return x/12.92 if x <= 0.04045 else ((x+0.055)/1.055)**2.4

def encode_srgb(x):
    return 12.92*x if x <= 0.0031308 else 1.055*x**(1/2.4)-0.055

def luminance(rgb):
    return sum(w*decode_srgb(x) for w,x in zip((0.2126,0.7152,0.0722),rgb))

def contrast(a,b):
    return (max(a,b)+0.05)/(min(a,b)+0.05)

colors = {'ready': (0,148,0), 'blocked': (255,0,0)}
lums = {k:luminance(v) for k,v in colors.items()}
grays = {k:round(255*encode_srgb(v)) for k,v in lums.items()}
assert grays["ready"] == grays["blocked"]
assert min(contrast(i,0) for i in lums.values()) > 4.5
assert contrast(*lums.values()) < 1.01

# Distinct gameplay readiness and current navigation focus are independent.
# This is a semantic-encoding uniqueness test, not a human vision model.
states=list(itertools.product(("ready","blocked"),(False,True)))
def color_only(state):
    op,focus=state
    return [grays[op],focus]
def redundant(state):
    op,focus=state
    return ["open-notch" if op=="ready" else "locked-crossbar", focus]
def count(f): return len({tuple(f(x)) for x in states})
assert count(color_only)==2 and count(redundant)==4
out = {
 'sRGB_colors': colors,
 'relative_luminance': {k:round(v,6) for k,v in lums.items()},
 'contrast_each_on_black': {k:round(contrast(v,0),5) for k,v in lums.items()},
 'contrast_between_state_colors': round(contrast(*lums.values()),5),
 'grayscale_encoded_8bit': grays,
 'distinct_state_focus_combinations_after_color_removed': {
   'of_four_color_only':count(color_only), 'of_four_separate_pattern_and_focus':count(redundant)
 },
}
print(json.dumps(out,indent=2))
