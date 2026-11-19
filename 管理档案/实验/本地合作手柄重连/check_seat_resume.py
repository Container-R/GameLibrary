"""Deterministic game-layer reference trace, not an SDL/hardware test."""
import json
from dataclasses import dataclass


@dataclass
class Seat:
    character: str
    connection: int | None
    generation: int = 1
    armed: bool = True
    move: int = 0
    prev_press: bool = False


seats = {"P1": Seat("medic", 0), "P2": Seat("scout", 1, move=1)}
live = {0, 1}
claim_ready = set()
trace = []


def lose(device):
    live.discard(device)
    claim_ready.discard(device)
    for s in seats.values():
        if s.connection == device:
            s.connection = None
            s.generation += 1
            s.armed = False
            s.move = 0
            s.prev_press = False


def sample(name, device, token, pressed=False, axis=0, valid=True, other_pressed=False):
    s = seats["P1"]
    if not valid or device not in live:
        outcome = "invalid_or_gone"
    elif s.connection is None and device not in {v.connection for v in seats.values()}:
        if not pressed and abs(axis) <= 10:
            claim_ready.add(device)
        if pressed and device in claim_ready and token == ("recover-P1", s.generation):
            s.connection = device
            s.generation += 1
            claim_ready.clear()
            outcome = "claimed_consumed"
        else:
            # Track a fresh edge: drifting/pressing before UI confirmation
            # requires returning to neutral rather than claiming on a held button.
            if pressed or abs(axis) > 10:
                claim_ready.discard(device)
            outcome = "waiting_for_claim"
    elif device != s.connection or token != s.generation:
        outcome = "wrong_instance_or_generation"
    elif not s.armed:
        if not pressed and not other_pressed and abs(axis) <= 10:
            s.armed = True
        outcome = "armed_without_action" if s.armed else "waiting_for_release"
    else:
        outcome = "game_press" if pressed and not s.prev_press else "no_game_press"
        s.move = axis if abs(axis) > 10 else 0
        s.prev_press = pressed
    trace.append({"step": name, "outcome": outcome, "owner": s.connection,
                  "p1_move": s.move, "p2_move": seats["P2"].move})


lose(0)
gap = seats["P1"].generation
sample("old_device_queued_press", 0, 1, pressed=True)
live.update({2, 3})
recover = ("recover-P1", gap)
sample("replacement_arrives_held", 2, recover, pressed=True, axis=50)
sample("invalid_zero_cannot_clear", 2, recover, valid=False)
sample("cannot_claim_yet", 2, recover, pressed=True)
sample("replacement_releases", 2, None)
sample("occupied_P2_cannot_claim_P1", 1, recover, pressed=True)
sample("other_device_ready", 3, None)
sample("claim_press_consumed", 2, recover, pressed=True)
sample("other_device_stale_claim", 3, recover, pressed=True)
now = seats["P1"].generation
sample("same_device_wrong_generation", 2, gap, pressed=True)
sample("claim_button_stays_held", 2, now, pressed=True)
sample("button_released_but_axis_still_held", 2, now, axis=70)
sample("other_gameplay_button_still_held", 2, now, other_pressed=True)
sample("release_and_valid_neutral", 2, now)
sample("first_fresh_press", 2, now, pressed=True)
sample("still_held_not_second_edge", 2, now, pressed=True)
assert [n["step"] for n in trace if n["outcome"] == "game_press"] == ["first_fresh_press"]
assert [n["step"] for n in trace if n["outcome"] == "claimed_consumed"] == ["claim_press_consumed"]
assert [n["step"] for n in trace if n["outcome"] == "armed_without_action"] == ["release_and_valid_neutral"]
assert next(n for n in trace if n["step"] == "other_gameplay_button_still_held")["outcome"] == "waiting_for_release"
assert all(n["p2_move"] == 1 for n in trace)
assert seats["P1"].character == "medic" and seats["P2"].character == "scout"
print(json.dumps(trace, indent=2))
