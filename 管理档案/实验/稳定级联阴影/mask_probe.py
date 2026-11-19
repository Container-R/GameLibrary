"""Raster a fixed 2-D occluder with nearest shadow lookup; no camera resampling."""
from fractions import Fraction as F
from math import floor
import json
from pathlib import Path

N = 16
deltas = [(F(0), F(0)), (F(3,10), F(1,8)), (F(11,20), F(-3,4))]
widths = (F(16), F(17), F(112,5))
# Static geometry defined in a fixed light XY basis: diagonal top, flat side.
def covered(x, y):
    return F(-13,8) <= x < F(6,5) and F(-21,8) <= y < F(13,20)+x/3

def mask(center, width, snap):
    s = width / N
    if snap:
        # Round anchor for fixed-size grid to nearest pitch; axis ties to +inf.
        origin = [floor(v / s + F(1,2)) * s for v in center]
    else:
        origin = list(center)
    origin = [v - width/2 for v in origin]
    cx = [origin[0] + (i+F(1,2))*s for i in range(N)]
    cy = [origin[1] + (j+F(1,2))*s for j in range(N)]
    depth = [[covered(x,y) for x in cx] for y in cy]
    scale = len(range(-192,192))
    xx = [floor((F(i,64)-origin[0]) / s) for i in range(-192,192)]
    yy = [floor((F(i,64)-origin[1]) / s) for i in range(-192,192)]
    assert min(xx+yy)>=0 and max(xx+yy)<N
    return [depth[j][i] for j in yy for i in xx], origin, s, scale

def output(seq, moving_widths, snap):
    actual = [mask(c,w,snap) for c,w in zip(seq,moving_widths,strict=True)]
    base = actual[0][0]
    rows = []
    for m, origin, s, _ in actual:
        rows.append({"origin":[str(v) for v in origin], "pitch":str(s),
                     "shadow_count":sum(m), "mask_changed_points":sum(a != b for a,b in zip(base,m,strict=True))})
    return rows, actual

configs = {
    "moving_fixed_extent_no_snap":(deltas,(F(16),)*3,False),
    "moving_fixed_extent_snap":(deltas,(F(16),)*3,True),
    "changing_extent_despite_snap":([(F(0),F(0))]*3,widths,True),
}
results = {name: output(*settings) for name,settings in configs.items()}
assert all(f["mask_changed_points"]==0 for f in results["moving_fixed_extent_snap"][0])
assert all(f["mask_changed_points"]>0 for name in configs if name!="moving_fixed_extent_snap" for f in results[name][0][1:])
print(json.dumps({k:v[0] for k,v in results.items()},indent=2))

if __name__ == "__main__":
    import sys
    if len(sys.argv)==2:  # optional visual, not part of JSON comparison
        from PIL import Image, ImageDraw
        panels = 192
        image = Image.new("RGB",(245+panels*4,3*(panels+38)+42),"#080f1d")
        d = ImageDraw.Draw(image)
        titles = ("Baseline","Frame 2","Frame 3","Change vs baseline (3)")
        for n,t in enumerate(titles):
            d.text((245+n*panels+7,10),t,fill="white")
        for row,(name, (_, actual)) in enumerate(results.items()):
            y=(panels+38)*row+32
            d.text((10,y+7), name.replace("_"," "), fill="white")
            for col,(a,_,__,wh) in enumerate(actual):
                im=Image.new("L",(wh,wh));im.putdata([45 if m else 235 for m in a])
                image.paste(im.resize((panels-4,panels-4),Image.Resampling.NEAREST),(245+col*panels,y))
            orig=actual[0][0];last=actual[-1][0]
            im=Image.new("RGB",(wh,wh));im.putdata([(252,150,66) if p!=q else (29,45,63) for p,q in zip(orig,last,strict=True)])
            image.paste(im.resize((panels-4,panels-4),Image.Resampling.NEAREST),(245+3*panels,y))
        image.save(Path(sys.argv[1]))
