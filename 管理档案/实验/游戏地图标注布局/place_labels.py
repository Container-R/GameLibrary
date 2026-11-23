"""Original screen-space map-label placement fixture. Run with Pillow + Noto Sans CJK."""
import argparse
from dataclasses import dataclass, replace
from itertools import combinations
import json
import math
from pathlib import Path

import PIL
from PIL import Image, ImageDraw, ImageFont, features

W, H = 400, 130
DEFAULT_FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"
PAD, GAP, HEIGHT = 6, 8, 28

@dataclass(frozen=True)
class Label:
    key: str
    rank: int  # Lower numbers place first
    text: str
    x: int
    y: int
    anchors: tuple[str, ...] = ("R", "L")

@dataclass(frozen=True)
class Frame:
    label: str
    scale: float
    pan_x: float
    activate_goal: bool = False

# Independent scenario A verifies that prior visibility is not ownership.
A = (Label("camp", 1, "砂脊营地", 139, 48, ("R",)),
     Label("goal", 0, "当前任务：北门", 171, 48),
     Label("tower", 1, "West Watchtower", 230, 92))
# Independent scenario B highlights low-amplitude camera movement. The
# focal-side heuristic toggles near viewport center, but both sides are legal.
B = (Label("harbor", 1, "Porte des Étoiles", 200, 53),
     Label("garden", 1, "旧花园", 160, 96))
A_FRAMES = (Frame("A0", 1.00, 0),
            Frame("A1", 1.04, -5, True),
            Frame("A2", 1.13, -12, True))
B_FRAMES = (Frame("B0", 1.00, -2), Frame("B1", 1.01, 2),
            Frame("B2", 1.02, -1), Frame("B3", 1.01, 2),
            Frame("B4", 1.05, 140), Frame("B5", 1.06, 250),
            Frame("B6", 1.00, -2))

def project(l, f):
    return round((l.x - 200) * f.scale + 200 + f.pan_x), round((l.y - 65) * f.scale + 65)

def overlap(a, b):
    return a[0] < b[2] and b[0] < a[2] and a[1] < b[3] and b[1] < a[3]

def box(x, y, w, side):
    l = x + GAP if side == "R" else x - GAP - w
    return l, y - HEIGHT // 2, l + w, y + HEIGHT // 2

def inside(rect):
    return 0 <= rect[0] < rect[2] <= W and 0 <= rect[1] < rect[3] <= H

def place(labels, f, previous, policy, widths):
    def sort_key(label):
        if policy == "sticky_first":
            return (label.key not in previous, label.rank, label.key)
        return label.rank, label.key
    placed, points, trace = {}, {}, {}
    for label in sorted(labels, key=sort_key):
        if label.key == "goal" and not f.activate_goal:
            continue
        x, y = points[label.key] = project(label, f)
        if not (0 <= x < W and 0 <= y < H):
            trace[label.key] = {"status": "offscreen-point"}
            continue
        preference = "R" if x <= W // 2 else "L"
        options = sorted(label.anchors, key=lambda s: s != preference)
        last = previous.get(label.key)
        if last in options and policy != "fresh":
            options = [last] + [side for side in options if side != last]
        misses = {}
        for side in options:
            r = box(x, y, widths[label.key], side)
            conflict = [key for key, (_, q) in placed.items() if overlap(r, q)]
            if not inside(r):
                misses[side] = "outside"
            elif conflict:
                misses[side] = conflict
            else:
                placed[label.key] = side, r
                break
        trace[label.key] = {"status": "visible" if label.key in placed else "hidden",
                            "rejected": misses}
    assert all(inside(r) for _,r in placed.values())
    assert not any(overlap(a[1], b[1]) for a,b in combinations(placed.values(), 2))
    return placed, points, trace

def simulate(labels, frames, policy, widths):
    previous, output = {}, {}
    for f in frames:
        placed, points, trace = place(labels, f, previous, policy, widths)
        # Preserve only current visible choices as preferences, not occupancy.
        previous = {label: p[0] for label, p in placed.items()}
        output[f.label] = {"placed": placed, "points": points, "trace": trace}
    return output

def draw_panel(target, at, f, row, labels, font, caption, header):
    layer = Image.new("RGB", (W, H + 35), "#153342")
    d = ImageDraw.Draw(layer)
    oy = 33
    colors = {"goal": ("#e1ad59", "#1b2630"), "default": ("#def0e9", "#163543")}
    d.rectangle((0, 0, W-1, 32), fill="#dce8e9")
    d.text((9, 17), f"{f.label}  {caption}", fill="#14303f", anchor="lm", font=header)
    d.text((W-8, 17), f"×{f.scale:.2f}", fill="#375b68", anchor="rm", font=header)
    for y in (39, 75, 110):
        d.line([(0, y+oy), (78,y+oy-13), (140,y+oy+6), (210,y+oy+2), (300,y+oy+11),(W, y+oy-8)], fill="#284857", width=2)
    for key, (x, y) in row["points"].items():
        if not (0 <= x < W and 0 <= y < H):
            continue
        fill, _ = colors.get(key, colors["default"])
        d.ellipse((x-3, y+oy-3, x+3, y+oy+3), fill=fill if key in row["placed"] else "#79909c")
    text_map = {l.key: l.text for l in labels}
    for key,(side,(x0,y0,x1,y1)) in row["placed"].items():
        fill, col = colors.get(key, colors["default"])
        d.rounded_rectangle((x0,y0+oy,x1-1,y1+oy-1), radius=4, fill=fill)
        left, top, right, bottom = font.getbbox(text_map[key])
        text_y = (y0 + y1 - (bottom - top)) / 2 - top + oy
        d.text((x0 + PAD - min(left,0), text_y), text_map[key], fill=col, font=font)
    target.paste(layer, at)

def main():
    pa = argparse.ArgumentParser()
    pa.add_argument("--font", default=DEFAULT_FONT)
    pa.add_argument("--index", type=int, default=2)
    pa.add_argument("--out", type=Path, default=Path(__file__).resolve().parent)
    args = pa.parse_args()
    font = ImageFont.truetype(args.font, 18, index=args.index, layout_engine=ImageFont.Layout.RAQM)
    header = ImageFont.truetype(args.font, 14, index=args.index)
    measured = {}
    for l in A+B:
        left, top, right, bottom = font.getbbox(l.text)
        advance = font.getlength(l.text)
        assert HEIGHT >= bottom-top+4
        measured[l.key] = {"text": l.text, "bbox": [left,top,right,bottom],
                           "advance_px": advance,
                           "box_width_px": math.ceil(max(right, advance) - min(0, left)) + 2*PAD}
    widths = {k:v["box_width_px"] for k,v in measured.items()}
    a_ref = simulate(A, A_FRAMES, "sticky_first", widths)
    a_fix = simulate(A, A_FRAMES, "ranked", widths)
    b_ref = simulate(B, B_FRAMES, "fresh", widths)
    b_fix = simulate(B, B_FRAMES, "ranked", widths)

    def switches(rows, key, subset):
        p = [rows[f]["placed"][key][0] for f in subset]
        return sum(x != y for x, y in zip(p, p[1:]))

    assert all("goal" in a_fix[f]["placed"] for f in ("A1","A2")), a_fix
    assert all("goal" not in a_ref[f]["placed"] for f in ("A1","A2")), a_ref
    assert a_fix["A1"]["trace"]["camp"]["rejected"]["R"] == ["goal"], a_fix
    subset = ("B0","B1","B2","B3")
    assert switches(b_ref,"harbor",subset) == 3
    assert switches(b_fix,"harbor",subset) == 0
    assert b_fix["B4"]["trace"]["harbor"]["rejected"]["R"] == "outside"
    assert b_fix["B4"]["placed"]["harbor"][0] == "L"
    assert b_fix["B5"]["trace"]["harbor"]["status"] == "offscreen-point"
    assert "harbor" not in b_fix["B5"]["placed"]
    assert b_fix["B6"]["placed"]["harbor"][0] == "R"
    assert simulate(tuple(reversed(B)), B_FRAMES, "ranked", widths) == b_fix
    # An identity surviving a UI mode change need not keep the old allowed anchors.
    changed = (replace(B[0], anchors=("L",)), B[1])
    p, _, _ = place(changed, B_FRAMES[1], {"harbor": "R"}, "ranked", widths)
    assert p["harbor"][0] == "L"
    comparisons = {"A_prior_visibility_first": a_ref, "A_rank_then_previous": a_fix,
                   "B_recompute_focal_side": b_ref, "B_rank_then_previous": b_fix}
    out = {"software":{"pillow": PIL.__version__, "freetype": features.version_module("freetype2"),
                       "raqm": features.version_feature("raqm"),"font_name":font.getname(),
                       "face_index":args.index,"px":18},
           "labels":measured, "placements":comparisons,
           "summary":{"goal_visible_when_active":{"previous_visible_first":"0/2","rank_then_previous":"2/2"},
                      "harbor_anchor_flips_frames_B0_B3":{"fresh":3,"rank_then_previous":0},
                      "retention_invalidates":{"B4":"outside on previous R, switches to L","B5":"source point exits view","B6":"re-enters with fresh R choice"},
                      "viewport_px":[W,H],"rectangles":"half-open; validates whole box and no pairwise overlap"}}
    args.out.mkdir(parents=True, exist_ok=True)
    (args.out/"observed.json").write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    rows = [(A, A_FRAMES[1:3], a_ref, "先保留旧标注"), (A, A_FRAMES[1:3], a_fix, "任务优先"),
            (B, B_FRAMES[0:2], b_ref, "每帧重选"),
            (B, B_FRAMES[0:2], b_fix, "优先级内复用锚点"),
            (B, B_FRAMES[4:6], b_fix, "旧锚点失效")]
    sheet = Image.new("RGB", (824, 181*len(rows)+12), "#f4f5f1")
    for i,(labels, frames, result, caption) in enumerate(rows):
        for j,f in enumerate(frames):
            draw_panel(sheet,(8+j*408,8+i*181), f,result[f.label],labels,font,caption,header)
    sheet.save(args.out/"comparison.png", optimize=True)
    print(json.dumps(out["summary"],ensure_ascii=False))

if __name__ == "__main__":
    main()
