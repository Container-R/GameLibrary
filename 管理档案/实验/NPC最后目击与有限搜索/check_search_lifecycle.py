"""Finite scripted search in a toy game; navigation results are injected."""
import json

class Search:
    def __init__(self):
        self.search_id = 0
        self.request = None
        self.state = "patrol"
        self.checked = set()
        self.steps_left = 0
        self.command_counter = 0

    def begin(self, steps):
        self.search_id += 1
        self.request = None
        self.state = "search"
        self.steps_left = steps
        self.checked = set()

    def command(self, post, now):
        if self.state != "search" or self.steps_left <= 0 or self.request:
            return None
        self.steps_left -= 1
        self.command_counter += 1
        self.request = (self.search_id, self.command_counter, post, now + 3)
        return self.request

    def tick(self, now):
        if not self.request or now < self.request[-1]:
            return "unchanged"
        self.request = None
        if self.steps_left == 0:
            self.state = "patrol"
        return "expired"

    def see_again(self):
        self.state = "visible"
        self.request = None

    def result(self, request, route, observed_areas, now):
        self.tick(now)
        if self.state != "search" or request != self.request or request is None:
            return "stale"
        self.request = None
        if route == "arrived":
            self.checked.update(observed_areas)
        if self.steps_left == 0:
            self.state = "patrol"
        return "record_observation" if route == "arrived" else "route_incomplete"

s = Search()
s.begin(2)
old = s.command("west entry", 0)
s.see_again()
stale_after_reacquire = s.result(old, "arrived", ["west room"], 1)
s.begin(2)
first = s.command("south entry", 1)
stale_during_new = s.result(old, "arrived", ["west room"], 1)
partial = s.result(first, "partial", ["south room"], 2)
assert not s.checked
second = s.command("north window", 2)
actual_scan = s.result(second, "arrived", ["north visible near half"], 3)
out = {
    "cancelled_during_reacquire": stale_after_reacquire,
    "cancelled_during_new_search": stale_during_new,
    "partial_does_not_clear": partial,
    "next_arrival": actual_scan,
    "cleared": sorted(s.checked),
    "end_state": s.state,
    "third_goal": s.command("another door", 3),
}
assert out == {"cancelled_during_reacquire":"stale","cancelled_during_new_search":"stale",
               "partial_does_not_clear":"route_incomplete","next_arrival":"record_observation",
               "cleared":["north visible near half"],"end_state":"patrol","third_goal":None}
stuck = Search()
stuck.begin(1)
never_returns = stuck.command("unresponsive route", 20)
assert stuck.tick(22) == "unchanged"
assert stuck.tick(23) == "expired" and stuck.state == "patrol"
assert stuck.result(never_returns, "arrived", ["should not clear"], 24) == "stale"
assert not stuck.checked
out["unresponsive_path_deadline"] = {"state":stuck.state,"late_callback":"stale","cleared":[]}
print(json.dumps(out,indent=2))
