#!/usr/bin/env python3
"""Reproduce the article's invented records. Python standard library only.

Default: read case.json beside this script, emit JSON to stdout, write nothing.
--svg-dir DIR writes two original SVGs there; existing files are refused unless
--overwrite is given. No networking, package installation, or article editing.
The checks concern these records and arithmetic, not a real tracking product.
"""
import argparse
import copy
import json
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from xml.sax.saxutils import escape


def F(value):
    return Fraction(str(value))


def serial(value):
    if isinstance(value, Fraction):
        return str(value)
    raise TypeError(type(value).__name__)


def analyze(rows, a, b, initial=None, final=None):
    """Unknown start is allowed only for a confirmed initial item."""
    a, b = F(a), F(b)
    if b <= a:
        raise ValueError("The observation duration must be positive")
    ids = [r["id"] for r in rows]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate flow ID")
    initial = set(initial if initial is not None else [
        r["id"] for r in rows
        if r["start"] is not None and F(r["start"]) <= a
        and (r["end"] is None or a < F(r["end"]))])
    if not initial <= set(ids):
        raise ValueError("Initial snapshot contains an unknown flow ID")
    changes = defaultdict(lambda: {"in": [], "out": []})
    per_item, complete, successful = [], [], []
    start_age = end_age = Fraction(0)
    unknown_start_age = unknown_end_age = False
    for r in rows:
        s = F(r["start"]) if r["start"] is not None else None
        e = F(r["end"]) if r["end"] is not None else None
        if s is None and r["id"] not in initial:
            raise ValueError("Unknown start without confirmed initial presence")
        if s is not None and e is not None and e <= s:
            raise ValueError("Every represented visit must have positive duration")
        if (e is None) != (r.get("outcome") is None):
            raise ValueError("Exit timestamp and exit outcome must agree")
        if e is None and F(r.get("open_confirmed_at", -1)) < b:
            raise ValueError("No confirmation that the item is still open at cutoff")
        if s is not None:
            should_be_initial = s <= a and (e is None or a < e)
            if should_be_initial != (r["id"] in initial):
                raise ValueError("Initial snapshot disagrees with event records")
        if s is not None and a < s <= b:
            changes[s]["in"].append(r["id"])
        if e is not None and a < e <= b:
            changes[e]["out"].append(r["id"])
        # Unknown pre-window arrival is clipped for residence only, not imputed.
        left = max(a, s) if s is not None else a
        right = min(b, e) if e is not None else b
        h = max(F(0), right - left)
        duration = e - s if s is not None and e is not None else None
        at_end = (s is None or s <= b) and (e is None or b < e)
        age_end = b - s if s is not None and at_end else None
        per_item.append({"id": r["id"], "window_hours": h,
                         "full_exit_hours": duration if e is not None and a < e <= b else None,
                         "age_at_end": age_end})
        if e is not None and a < e <= b:
            complete.append(duration)
            if r["outcome"] == "success":
                successful.append(duration)
        if r["id"] in initial:
            if s is None:
                unknown_start_age = True
            else:
                start_age += a - s
        if at_end:
            if s is None:
                unknown_end_age = True
            else:
                end_age += b - s
    # Event sweep: preserve all simultaneous in/out records, including net zero.
    active = set(initial)
    segments, events = [], []
    previous, area = a, F(0)
    for t in sorted(set(changes) | {b}):
        if previous < t:
            part = len(active) * (t - previous)
            segments.append({"from": previous, "to": t, "count": len(active), "area": part})
            area += part
        change = changes[t]
        for flow in change["out"]:
            if flow not in active:
                raise ValueError("Exit without active visit")
            active.remove(flow)
        for flow in change["in"]:
            if flow in active:
                raise ValueError("Duplicate arrival for active visit")
            active.add(flow)
        events.append({"time": t, "in": change["in"], "out": change["out"], "after": sorted(active)})
        previous = t
    if final is not None and active != set(final):
        raise ValueError("Final snapshot disagrees with event records")
    total = sum((x["window_hours"] for x in per_item), F(0))
    if area != total:
        raise AssertionError("Event area and residence sum differ")
    incoming = sum(len(c["in"]) for c in changes.values())
    outgoing, success = len(complete), len(successful)
    if len(initial) + incoming - outgoing != len(active):
        raise AssertionError("Count conservation failed")
    q = sum(complete, F(0)) if None not in complete else None
    ba = None if unknown_start_age else start_age
    bb = None if unknown_end_age else end_age
    if None not in (q, ba, bb) and area != q + bb - ba:
        raise AssertionError("Boundary-age identity failed")
    def mean(xs):
        return sum(xs, F(0)) / len(xs) if xs and None not in xs else None
    success_known = [v for v in successful if v is not None]
    involved = len(initial) + incoming
    return {"T": b-a, "initial_count": len(initial), "final_count": len(active),
            "incoming": incoming, "outgoing": outgoing, "successful": success,
            "non_success_exits": outgoing-success, "H_event": area, "H_items": total,
            "L": area/(b-a), "Q_exit": q, "B_start": ba, "B_end": bb,
            "all_exit_mean": mean(complete), "success_mean": mean(successful),
            "known_success_durations": success_known,
            "S": involved, "window_visit_mean": area/involved if involved else None,
            "per_item": per_item, "segments": segments, "events": events}


def variants(data):
    rows = data["flows"]
    older = copy.deepcopy(rows)
    next(r for r in older if r["id"] == "A-1")["start"] = -96
    missing = copy.deepcopy(rows)
    for row in missing:
        if row["id"] in ["A-1", "B-1"]:
            row["start"] = None
    no_exit = [{"id": "B-only", "start": -6, "end": None, "outcome": None, "open_confirmed_at": 48}]
    # Same case, split at a time with simultaneous arrival and departure.
    left = analyze(rows, 0, 30)
    right = analyze(rows, 30, 48)
    # A genuine exit at 0 is already absent from the post-event initial snapshot.
    start_exit = [{"id": "X", "start": -12, "end": 0, "outcome": "success"},
                  {"id": "Y", "start": 0, "end": 12, "outcome": "success"},
                  {"id": "Z", "start": 12, "end": None, "outcome": None, "open_confirmed_at": 24}]
    # Deliberately wrong semantics: merge cancelled and reopened C into one visit.
    merged = [copy.deepcopy(r) for r in rows if r["id"] != "C-2"]
    c = next(r for r in merged if r["id"] == "C-1")
    c.update(end=None, outcome=None, open_confirmed_at=48)
    # Only initial/final snapshots cannot distinguish these two histories.
    sparse_a = [{"id": "P", "start": -1, "end": 24, "outcome": "success"},
                {"id": "Q", "start": 24, "end": None, "outcome": None, "open_confirmed_at": 48}]
    sparse_b = copy.deepcopy(sparse_a)
    sparse_b[0]["end"], sparse_b[1]["start"] = 6, 42
    extended = copy.deepcopy(rows)
    for r in extended:
        if r["end"] is None:
            r.update(end=60, outcome="success")
    results = {
        "older_A_same_window_events": analyze(older, 0, 48),
        "unknown_initial_entry_times": analyze(missing, 0, 48, data["initial_snapshot"], data["final_snapshot"]),
        "zero_exits": analyze(no_exit, 0, 48), "empty": analyze([], 0, 48),
        "split_left_0_30": left, "split_right_30_48": right,
        "start_and_end_events_0_12": analyze(start_exit, 0, 12),
        "adjacent_events_12_24": analyze(start_exit, 12, 24),
        "wrong_merged_C": analyze(merged, 0, 48),
        "same_sparse_snapshots_history_A": analyze(sparse_a, 0, 48),
        "same_sparse_snapshots_history_B": analyze(sparse_b, 0, 48),
        "later_observed_exits_extend_to_60": analyze(extended, 0, 60)
    }
    base = analyze(rows, 0, 48, data["initial_snapshot"], data["final_snapshot"])
    for key in ["H_event", "incoming", "outgoing", "successful"]:
        if base[key] != left[key] + right[key]:
            raise AssertionError("Adjacent windows do not add: " + key)
    rejected = {}
    bads = {"duplicate_id": rows + [copy.deepcopy(rows[0])],
            "missing_recorded_exit": copy.deepcopy(rows)}
    bads["missing_recorded_exit"][0].update(end=None, outcome=None, open_confirmed_at=48)
    for name, bad in bads.items():
        try:
            analyze(bad, 0, 48, data["initial_snapshot"], data["final_snapshot"])
        except ValueError as error:
            rejected[name] = str(error)
        else:
            raise AssertionError("Invalid authored case was not rejected: " + name)
    results["rejected_inputs"] = rejected
    return results


def svg_base(title, width, height):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img">',
            f'<title>{escape(title)}</title>',
            '<rect width="100%" height="100%" fill="#fff"/>',
            '<g font-family="Noto Sans CJK SC, sans-serif" font-size="17" fill="#182b3a">',
            f'<text x="32" y="36" font-size="24" font-weight="bold">{escape(title)}</text>']


def make_svgs(data, result):
    x = lambda t: 110 + float(t) * 16
    y = lambda n: 325 - n * 54
    out = svg_base("同一记录的在途数量与时间面积", 1000, 450)
    out.append('<text x="32" y="67">在途数量（次流转）</text>')
    for n in range(5):
        out.append(f'<line x1="110" y1="{y(n)}" x2="878" y2="{y(n)}" stroke="#dde3e8"/>')
        out.append(f'<text x="80" y="{y(n)+6}">{n}</text>')
    for seg in result["segments"]:
        left, right, count = float(seg["from"]), float(seg["to"]), seg["count"]
        out.append(f'<rect x="{x(left)}" y="{y(count)}" width="{x(right)-x(left)}" height="{325-y(count)}" fill="#d7e9f2"/>')
        out.append(f'<line x1="{x(left)}" y1="{y(count)}" x2="{x(right)}" y2="{y(count)}" stroke="#17648b" stroke-width="4"/>')
        out.append(f'<text x="{(x(left)+x(right))/2}" y="{y(count)+28}" text-anchor="middle">{seg["area"]}</text>')
    for t, n in [(0,3),(6,4),(12,3),(18,2),(30,2),(36,3),(48,3)]:
        out.append(f'<line x1="{x(t)}" y1="100" x2="{x(t)}" y2="325" stroke="#aab8c2" stroke-dasharray="3 4"/>')
        out.append(f'<circle cx="{x(t)}" cy="{y(n)}" r="5" fill="#17648b"/>')
        out.append(f'<text x="{x(t)}" y="351" text-anchor="middle">{t}</text>')
    out.append('<text x="900" y="351">小时</text>')
    out.append('<text x="110" y="391">浅蓝块中的数字为流转·小时；总面积 132，时间平均 132 ÷ 48 = 2.75。</text>')
    out.append('<text x="110" y="421">30 与 48 小时都有一进一出，数量不跳变，但两个事件仍分别登记。</text>')
    out.append('</g></svg>')
    residence = svg_base("逐项只累计落在观察窗口内的部分", 1000, 565)
    residence.append('<text x="32" y="68">蓝色横条：本窗口停留；虚线：窗口前已发生的部分；→：截至 48 仍在途。</text>')
    # In this figure -24..48 uses ten pixels per natural hour.
    xr = lambda t: 360 + float(t) * 10
    for t in [-24,-6,0,6,12,18,30,36,48]:
        residence.append(f'<line x1="{xr(t)}" y1="96" x2="{xr(t)}" y2="452" stroke="#e0e5e9"/>')
        residence.append(f'<text x="{xr(t)}" y="481" text-anchor="middle">{t}</text>')
    for idx, row in enumerate(data["flows"]):
        yy = 122 + idx*49
        s, e = row["start"], row["end"]
        end = 48 if e is None else e
        residence.append(f'<text x="32" y="{yy+6}">{row["id"]}</text>')
        if s < 0:
            residence.append(f'<line x1="{xr(s)}" y1="{yy}" x2="{xr(0)}" y2="{yy}" stroke="#8997a3" stroke-width="8" stroke-dasharray="5 5"/>')
        if end > max(s,0):
            residence.append(f'<line x1="{xr(max(s,0))}" y1="{yy}" x2="{xr(end)}" y2="{yy}" stroke="#17648b" stroke-width="13"/>')
        residence.append(f'<circle cx="{xr(max(s,0))}" cy="{yy}" r="5" fill="#17648b"/>')
        if e is not None:
            residence.append(f'<circle cx="{xr(e)}" cy="{yy}" r="6" fill="#fff" stroke="#17648b" stroke-width="2"/>')
        else:
            residence.append(f'<text x="{xr(48)+4}" y="{yy+6}">→</text>')
        residence.append(f'<text x="900" y="{yy+6}">{result["per_item"][idx]["window_hours"]} 小时</text>')
    residence.append('<line x1="360" y1="89" x2="360" y2="455" stroke="#b66422" stroke-width="2"/>')
    residence.append('<line x1="840" y1="89" x2="840" y2="455" stroke="#b66422" stroke-width="2"/>')
    residence.append('<text x="354" y="518" text-anchor="end">窗口开始 0</text>')
    residence.append('<text x="845" y="518">窗口结束 48</text>')
    residence.append('<text x="32" y="550">圆点为本窗片段起点，空心点为退出；F-1 在 48 进入，本窗贡献为 0。横轴：小时。</text>')
    residence.append('</g></svg>')
    return {"flow-timeline.svg": "\n".join(out), "flow-residence.svg": "\n".join(residence)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--svg-dir", type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    data = json.loads(Path(__file__).with_name("case.json").read_text(encoding="utf-8"))
    w = data["window"]
    result = analyze(data["flows"], w["start"], w["end"], data["initial_snapshot"], data["final_snapshot"])
    by_id = {r["id"]: r for r in data["flows"]}
    for event in data["internal_events"]:
        visit = by_id[event["flow"]]
        if not (F(visit["start"]) <= F(event["time"]) and
                (visit["end"] is None or F(event["time"]) < F(visit["end"]))):
            raise ValueError("Internal state change outside its visit")
    labor = sum((F(x["to"])-F(x["from"]) for x in data["labor"]), F(0))
    # The explicit input uses complete per-person intervals, without overlaps.
    for entry in data["labor"]:
        if not (F(w["start"]) <= F(entry["from"]) < F(entry["to"]) <= F(w["end"])):
            raise ValueError("Labor interval outside observation window")
        visit = by_id[entry["flow"]]
        if F(entry["from"]) < F(visit["start"]) or (visit["end"] is not None and F(entry["to"]) > F(visit["end"])):
            raise ValueError("Labor interval outside its visit")
    by_person = defaultdict(list)
    for entry in data["labor"]:
        by_person[entry["person"]].append((F(entry["from"]), F(entry["to"])))
    for intervals in by_person.values():
        intervals.sort()
        if any(left[1] > right[0] for left,right in zip(intervals,intervals[1:])):
            raise ValueError("Overlapping labor intervals for the same person")
    report = {"scope": "原创教学输入的算术复算，不是独立审稿或真实团队/软件验证", "main": result,
              "recorded_person_hours": labor, "variants": variants(data)}
    if args.svg_dir:
        figures = make_svgs(data, result)
        targets = [args.svg_dir / name for name in figures]
        if not args.overwrite and any(p.exists() for p in targets):
            raise FileExistsError("Refusing to overwrite an SVG; choose another directory or use --overwrite")
        args.svg_dir.mkdir(parents=True, exist_ok=True)
        for name, value in figures.items():
            (args.svg_dir / name).write_text(value+"\n", encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2, default=serial))


if __name__ == "__main__":
    main()
