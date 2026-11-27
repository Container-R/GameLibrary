"""Application contract only; no Unity APIs, layout, or input device."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Request:
    intent: int
    data: int
    item: str

@dataclass(frozen=True)
class Row:
    item: str
    data: int
    bound: int
    visible: bool

class Menu:
    def __init__(self):
        self.items = ["A", "B", "C", "D"]
        self.wanted = "B"
        self.intent = 1
        self.data = 1

    def request(self):
        return Request(self.intent, self.data, self.wanted)

    def issue(self, r):
        if r != self.request():
            return None
        # A missing ID must not become -1 (a real scroll command in Unity).
        return self.items.index(r.item) if r.item in self.items else None

    def can_handoff(self, r, row, current, actual_focus):
        return (r == self.request() and r.item in self.items
                and row is not None and row == current and row.visible
                and row.item == r.item and row.data == r.data
                and actual_focus == row)

m = Menu()
old = m.request()
old_index = m.issue(old)
assert old_index == 1
m.items = ["A", "D", "C", "B"]
m.data += 1
assert m.items[old_index] == "D" and m.issue(old) is None
now = m.request()
assert m.issue(now) == 3
print("reorder: replayed index 1 addresses D; current B resolves to 3")

visible = Row("B", m.data, 7, True)
clipped = Row("B", m.data, 7, False)
assert not m.can_handoff(now, clipped, clipped, clipped)
assert not m.can_handoff(now, visible, visible, None)
rebound = Row("B", m.data, 8, True)
assert not m.can_handoff(now, visible, rebound, rebound)
assert m.can_handoff(now, rebound, rebound, rebound)
print("handoff: clipping, focus mismatch and a stale binding all reject")

m.intent += 1
m.wanted = "A"
assert m.issue(now) is None and not m.can_handoff(now, rebound, rebound, rebound)
print("new navigation intent: older request cannot scroll or take focus")

m.wanted = "B"
m.data += 1
m.items.remove("B")
assert m.issue(m.request()) is None
assert m.items[-1] == "C"
print("removed B: no command; -1 would scroll to the last item C")
