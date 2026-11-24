"""Exact-time input bridge model. Not a physics engine."""
from collections import deque

TICK_MS = 20
EVENTS = [(27, "down", 1), (34, "up", 1), (42, "down", 2), (57, "up", 2)]
FRAME_PLANS = {
    "regular": [10, 20, 30, 40, 50, 60, 70, 80],
    "stall": [10, 65, 80],
}

def run(frames):
    pending = deque()
    source = deque(sorted(EVENTS))
    held = False
    end = TICK_MS
    shots = []
    for frame in frames:
        while source and source[0][0] <= frame:
            pending.append(source.popleft())
        frame_downs = [seq for ts, kind, seq in pending if kind == "down"]
        naive_snapshot = bool(frame_downs)
        while end <= frame:
            consumed = []
            while pending and pending[0][0] < end:
                _, edge, seq = pending.popleft()
                held = edge == "down"
                if held:
                    consumed.append(seq)
                    shots.append((seq, end))
            print(f"frame={frame:2} tick=[{end-TICK_MS:2},{end:2}) "
                  f"presses={str(consumed):5} held_at_end={int(held)} "
                  f"naive_frame_press={int(naive_snapshot)}")
            end += TICK_MS
    return shots

for label, plan in FRAME_PLANS.items():
    print(label)
    result = run(plan)
    assert result == [(1,40), (2,60)], result
    print("presses consumed:", result)
