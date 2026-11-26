"""Rational teaching model; positive constant-BPM segments; not StepMania."""
from fractions import Fraction as F

BPM_BEFORE, BPM_AFTER = 120, 180
BOUNDARY, PAUSE, SAMPLE_RATE = 8, F(2, 5), 48000


def target(beat, event):
    x = F(beat)
    travel = min(x, BOUNDARY) * F(60, BPM_BEFORE)
    travel += max(x - BOUNDARY, 0) * F(60, BPM_AFTER)
    if x > BOUNDARY or (x == BOUNDARY and event == "delay"):
        travel += PAUSE
    return travel


for event in ("stop", "delay"):
    times = [target(b, event) for b in (7, 8, 9)]
    samples = [int(t * SAMPLE_RATE) for t in times]
    assert samples == ([168000, 192000, 227200] if event == "stop" else [168000, 211200, 227200])
    print(event, "beats 7/8/9:", samples)
