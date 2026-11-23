"""Plot isolated particle birth positions over a sampled polyline; no engine."""
from math import dist, floor, isclose
from pathlib import Path
import PIL
from PIL import Image, ImageDraw, ImageFont

GAP = 0.5
STRAIGHT = [(0, 0), (4, 0)]
SPLIT = [(0, 0), (.3, 0), (1.2, 0), (4, 0)]
CORNER = [(0, 0), (2, 0), (2, 2)]
CHORD = [CORNER[0], CORNER[-1]]


def sample(points, phase=0., cap=None):
    """One chronological batch. phase = distance accumulated toward next birth."""
    out, attempted = [], 0
    for a, b in zip(points, points[1:]):
        length = dist(a, b)
        if length == 0:
            continue
        total = phase + length
        n = floor((total + 1e-12) / GAP)
        retained = n if cap is None else min(n, cap - len(out))
        for k in range(1, retained + 1):
            t = min(1., (k * GAP - phase) / length)
            out.append(tuple(a[i] + t * (b[i] - a[i]) for i in (0, 1)))
        phase = max(0., total - n * GAP)
        attempted += n
    return out, phase, attempted


def fmt(points):
    return " ".join(f"({x:.3f},{y:.3f})" for x, y in points)


def make_plot(straight, corner, chord):
    image = Image.new("RGB", (810, 455), "#edf4f6")
    draw = ImageDraw.Draw(image)
    title_font = ImageFont.load_default(size=18)
    label_font = ImageFont.load_default(size=14)
    draw.text((20, 10), "Particle birth positions on sampled paths", fill="#153447", font=title_font)
    draw.text((20, 34), "Orange: births     Navy: true path     Blue dashes: endpoint-only path", fill="#355368", font=label_font)

    def panel(col, row, title, truth, dots, chord_path=None, marker=None):
        left, top = 18 + col * 395, 56 + row * 190
        draw.rounded_rectangle((left, top, left+380, top+174), 10, fill="#ffffff", outline="#a4bbc6")
        draw.text((left+12, top+10), title, fill="#153447", font=label_font)
        def px(p): return (left+44+59*p[0], top+148-59*p[1])
        draw.line([px(p) for p in truth], fill="#23475c", width=3)
        if chord_path:
            a, b = chord_path
            for i in range(0, 16, 2):
                segment = [px(tuple(a[j]+(b[j]-a[j])*k/16 for j in (0, 1))) for k in (i, i+1)]
                draw.line(segment, fill="#4d83ad", width=2)
        for x,y in set(dots):
            x,y = px((x,y))
            draw.ellipse((x-6,y-6,x+6,y+6), fill="#e25317", outline="#98350d", width=1)
        if marker:
            x,y=px(dots[-1])
            draw.text((x+11,y-22), marker, fill="#963709", font=label_font)
    panel(0, 0, "A. Same 8 births, all at frame end", STRAIGHT, [STRAIGHT[-1]]*8, marker="x8")
    panel(1, 0, "B. Same 8 births, spaced along 4 m", STRAIGHT, straight)
    panel(0, 1, "C. Corner sampled: 8 births on the path", CORNER, corner)
    panel(1, 1, "D. Endpoint chord only: 5 births off path", CORNER, chord, CHORD)
    image.save(Path(__file__).with_name("comparison.png"))


def main():
    straight, residual, _ = sample(STRAIGHT)
    split, residual_split, _ = sample(SPLIT)
    corner, _, _ = sample(CORNER)
    chord, chord_residual, _ = sample(CHORD)
    assert len(straight) == len(split) == 8 and isclose(residual, residual_split, abs_tol=1e-12)
    assert all(dist(a,b) < 1e-12 for a,b in zip(straight, split))
    assert len(corner) == 8 and len(chord) == 5
    capped, phase, attempted = sample([(0,0),(2.25,0)], cap=2)
    following, next_phase, next_attempted = sample([(2.25,0),(2.5,0)], phase)
    assert capped == [(.5,0), (1.,0)] and phase == .25 and attempted == 4
    assert following == [(2.5,0)] and next_phase == 0. and next_attempted == 1
    print("Pillow", PIL.__version__)
    print("straight, same count at endpoint: 8 x (4.000,0.000)")
    print("straight, along path:", fmt(straight))
    print("straight, split path:", fmt(split))
    print("corner, retained waypoint:", fmt(corner))
    print(f"corner, endpoint chord only: {fmt(chord)}; residual={chord_residual:.6f}")
    print(f"budget first frame: attempted={attempted} actual={len(capped)} dropped={attempted-len(capped)} phase={phase:.3f}")
    print(f"budget next frame: attempted={next_attempted} actual={len(following)} positions={fmt(following)}")
    make_plot(straight, corner, chord)


if __name__ == "__main__":
    main()
