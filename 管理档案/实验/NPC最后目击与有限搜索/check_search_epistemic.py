"""Two toy replays for a fictional hide-and-seek game's NPC (no engine)."""
import json

def goals(observations, hidden_world=None, *, inject_bad_read=False):
    last_seen = None
    emitted = []
    for tick, event, point in observations:
        if event == "see":
            last_seen = point
            emitted.append(["check_visible", last_seen])
        elif event == "loss":
            # The deliberately wrong comparison injects world data absent from observations.
            emitted.append(["check_last_seen", hidden_world[tick] if inject_bad_read else last_seen])
        elif event == "noise":
            # Policy in this fixture: route check finished, then inspect unrelated noise.
            emitted.append(["inspect_noise", point])
    return emitted

events = [(2, "see", "junction"), (3, "loss", None),
          (7, "noise", "service entry")]
route_a = {3: "loading bay", 4: "locker"}
route_b = {3: "stairs", 4: "upper room"}
correct = [goals(events, route) for route in (route_a, route_b)]
broken = [goals(events, route, inject_bad_read=True) for route in (route_a, route_b)]
assert correct[0] == correct[1] == [
    ["check_visible", "junction"], ["check_last_seen", "junction"],
    ["inspect_noise", "service entry"],
]
assert broken[0][1][1] == "loading bay" and broken[1][1][1] == "stairs"

adjacent = {"storage": {"junction"}, "junction": {"storage", "alcove"},
            "alcove": {"junction"}}

def advance(previous, observed_empty):
    later = previous.union(*(adjacent[space] for space in previous))
    return later - observed_empty

zones = {"storage", "junction", "alcove"}
candidates = [zones - {"junction", "alcove"}]
candidates.append(advance(candidates[-1], {"junction"}))
candidates.append(advance(candidates[-1], set()))
candidates.append(advance(candidates[-1], set()))
assert candidates == [{"storage"}, {"storage"}, {"storage", "junction"}, zones]
no_reentry = [candidates[0]]
for _ in range(3):
    no_reentry.append(advance(no_reentry[-1], {"junction","alcove"}))
assert all(x == {"storage"} for x in no_reentry)

# The two paths below are synthetic planner statuses, not simulated path queries.
checks = [("adjacent closed door", 1, False, True),
          ("mezzanine", 2, True, False), ("junction overlook", 5, True, True)]
chosen = min((x for x in checks if x[2] and x[3]), key=lambda x: x[1])[0]
assert chosen == "junction overlook"
print(json.dumps({"committed_trace_unchanged":correct[0],
                  "wrong_loss_goals":[g[1][1] for g in broken],
                  "candidate_timeline":[sorted(x) for x in candidates],
                  "permanent_clearance_timeline":[sorted(x) for x in no_reentry],
                  "observation_post_reach_and_view":chosen},indent=2))
