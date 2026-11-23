#!/usr/bin/env python3
"""Actual Pillow float mask rendering and reconstruction; no GPU/TSR."""
from fractions import Fraction
from math import floor
from pathlib import Path
from PIL import Image, ImageDraw

W, H, OUTLINE = 32, 12, 3
DIR = Path(__file__).parent

def band(n, width):
    # Rasterize a vertical outside band against a pixel-aligned step edge
    # with exact box coverage per column (fractional radius allowed).
    left, right = Fraction(n, 2) - width, Fraction(n, 2)
    row = [float(max(0, min(i+1, right)-max(i, left))) for i in range(n)]
    im = Image.new("F", (n, H))
    im.putdata(row * H)
    return im

def measure(im):
    row = [im.getpixel((i, H//2)) for i in range(W)]
    return max(row), sum(row), sum(v > .5 for v in row)

def run():
    print(f"Pillow {Image.__version__}, float masks; output {W}x{H}")
    sheet = Image.new("RGB", (560, 285), "#e7edf2")
    d = ImageDraw.Draw(sheet)
    d.text((8, 8), "Step-edge coverage, approx. 5x horizontal magnification", fill="#202622")
    d.text((8, 32), "Scale", fill="#202622")
    for j, policy in enumerate(("fixed", "rounded", "fractional")):
        d.text((66+j*162, 32), policy, fill="#202622")
    for yi,n in enumerate((32,24,16)):
        s = Fraction(n,W)
        d.text((8,59+yi*55), f"{float(s):.0%}", fill="#202622")
        cases = {"fixed": Fraction(OUTLINE), "rounded": Fraction(floor(OUTLINE*s+Fraction(1,2))),
                 "fractional": OUTLINE*s}
        for j,(policy,width) in enumerate(cases.items()):
            im = band(n, width).resize((W,H), Image.Resampling.BILINEAR)
            peak, area, threshold = measure(im)
            geom = width/s
            print(f"s={float(s):.2f} {policy:10} geometry={float(geom):.4f} peak={peak:.4f} coverage={area:.4f} alpha>.5={threshold}")
            assert abs(area-float(geom)) < .10
            vis = Image.new("RGB", (W,H))
            vis.putdata([(round(255*x),round(155*x),round(35*x)) if i%W<(W//2) else
                         (35,70,80) for i,x in enumerate(im.get_flattened_data())])
            sheet.paste(vis.resize((150,41),Image.Resampling.NEAREST),(66+j*162,52+yi*55))

    # Half-scale target band of only one output pixel has a half-covered
    # internal texel. Interpolation may preserve area but reduce peak.
    thin=[]
    for filt in (Image.Resampling.NEAREST, Image.Resampling.BILINEAR):
        peak, area, threshold=measure(band(16,Fraction(1,2)).resize((W,H),filt))
        print(f"thin 50% {filt.name:8} peak={peak:.4f} coverage={area:.4f} alpha>.5={threshold}")
        assert abs(area-1) < 1e-6 and threshold == 0
        thin.append((peak,area))
    assert thin == [(.5,1),(.375,1)]

    # Attachment W=10; active [1,7), rightmost center at 6.5. One-texel
    # step addresses center 7.5, legal texture UV but authored poison.
    tex=Image.new("L",(10,1))
    tex.putdata([255,0,0,0,0,0,0,255,255,255])
    tap=7.5
    texture_only=tex.getpixel((floor(min(max(tap,.5),9.5)),0))
    active_clamp=tex.getpixel((floor(min(max(tap,1.5),6.5)),0))
    print(f"padding tap UV={tap/10:.2f}: allocation-clamp={texture_only/255:.0f}, active-viewport-clamp={active_clamp/255:.0f}")
    assert (texture_only,active_clamp)==(255,0)
    d.text((8,225),"50% scale, 1px target: peak .500 nearest / .375 linear; area 1.000 in both.",fill="#202622")
    d.text((8,247),"Padding tap at UV .75: texture clamp reads 1, active viewport clamp reads 0.",fill="#202622")
    sheet.save(DIR/"comparison.png")

if __name__ == "__main__":
    run()
