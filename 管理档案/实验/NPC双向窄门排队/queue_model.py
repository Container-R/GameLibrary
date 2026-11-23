"""Discrete doorway policy illustration; no continuous physics."""
from collections import deque

class Door:
    def __init__(self, limit=2):
        self.limit = limit
        self.queue = [deque(), deque()]
        self.dir = None
        self.inside = set()
        self.admitted = 0
        self.last = 1

    def request(self, side, npc):
        self.queue[side].append(npc)

    def offer(self, exit_free=True):
        if not exit_free:
            return None
        if self.dir is not None and not self.inside:
            # A holder may continue a batch if an opposite waiter is not due.
            if self.admitted >= self.limit or not self.queue[self.dir]:
                self.last, self.dir = self.dir, None
        if self.dir is None:
            order = [1 - self.last, self.last]
            self.dir = next((s for s in order if self.queue[s]), None)
            self.admitted = 0
        if self.dir is None or not self.queue[self.dir]:
            return None
        if self.admitted >= self.limit and self.queue[1-self.dir]:
            return None
        npc = self.queue[self.dir].popleft()
        self.admitted += 1
        self.inside.add(npc)  # assumes offer reserves an actual valid entry slot
        return npc

    def clear(self, npc):
        self.inside.remove(npc)

def main():
    g = Door()
    for side, names in enumerate(("ABC", "xyz")):
        for n in names:
            g.request(side, n)
    assert (g.offer(), g.offer(), g.offer()) == ("A","B",None)
    g.clear("A")
    assert g.offer() is None  # B still occupies; waiting time cannot transfer
    g.clear("B")
    assert g.offer(exit_free=False) is None
    assert (g.offer(),g.offer(),g.offer()) == ("x","y",None)
    g.clear("x")
    g.clear("y")
    assert g.offer() == "C"
    g.clear("C")
    assert g.offer() == "z"
    g.clear("z")
    assert g.offer() is None
    print("3 agents per side, cap 2: AB | xy | C | z")
    print("Partial clearance and blocked exit: no handoff/admission")

if __name__ == "__main__":
    main()
