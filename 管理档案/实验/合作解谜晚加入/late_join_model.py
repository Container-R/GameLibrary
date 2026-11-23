"""Deterministic protocol model, not a transport/engine test."""
from dataclasses import dataclass, field
from itertools import permutations

@dataclass(frozen=True)
class Message:
    generation: int
    world: int
    sequence: int
    kind: str
    value: object

@dataclass
class Client:
    generation: int = 2
    cursor: int | None = None
    gate: str | None = None
    objective: str | None = None
    hints: list[str] = field(default_factory=list)
    pending: dict[int, Message] = field(default_factory=dict)
    limit: int = 4
    needs_snapshot: bool = False

    def receive(self, msg: Message):
        if msg.generation != self.generation or self.needs_snapshot:
            return
        if msg.kind == "snapshot":
            if self.cursor is not None:  # one immutable baseline per generation
                return
            self.gate, self.objective = msg.value
            self.cursor = msg.sequence
            self.pending = {n: m for n, m in self.pending.items() if n > self.cursor}
        else:
            if self.cursor is not None and msg.sequence <= self.cursor:
                return
            if msg.sequence not in self.pending and len(self.pending) >= self.limit:
                self.gap_deadline()
                return
            self.pending.setdefault(msg.sequence, msg)
        while self.cursor is not None and self.cursor + 1 in self.pending:
            msg = self.pending.pop(self.cursor + 1)
            if msg.kind == "objective":
                self.objective = msg.value
            elif msg.kind == "hint":
                self.hints.append(msg.value)
            else:
                raise AssertionError("unexpected delta")
            self.cursor = msg.sequence

    def gap_deadline(self):
        # Called by an application timer for a known gap or missing baseline.
        self.pending.clear()
        self.needs_snapshot = True

def route(generation, start, updates, player):
    sequence = start
    for revision, audience, kind, data in updates:
        if player in audience:
            sequence += 1
            yield Message(generation, revision, sequence, kind, data)

snapshot = Message(2, 40, 8, "snapshot", ("open", "Align the lenses"))
history = [
    (41, {"A"}, "hint", "A only"),
    (42, {"A", "B"}, "objective", "Light the beacon"),
    (43, {"B"}, "hint", "Follow the beam"),
]
objective, hint = route(2, 8, history, "B")
previous_snapshot = Message(1, 39, 8, "snapshot", ("closed", "Find the door"))
previous_objective = Message(1, 40, 9, "objective", "Old objective")

def exercise():
    count = 0
    for order in permutations([snapshot, objective, hint, previous_snapshot, previous_objective]):
        client = Client()
        for msg in (*order, hint):
            client.receive(msg)
        assert (client.gate, client.objective, client.hints, client.cursor) == (
            "open", "Light the beacon", ["Follow the beam"], 10)
        count += 1
    assert count == 120 and objective.world != snapshot.world + 1
    print(f"{count} delivery orders converge; global-revision adjacency rejects r{objective.world}")

    client = Client()
    for msg in (snapshot, hint, previous_objective):
        client.receive(msg)
    assert client.cursor == 8 and not client.hints
    client.gap_deadline()
    client.receive(objective)  # abandoned generation, even though it would fill the gap
    assert client.needs_snapshot and not client.hints
    replacement = Client(generation=3)
    replacement.receive(Message(3, 43, 0, "snapshot", ("open", "Light the beacon")))
    replacement.receive(hint)
    assert replacement.objective == "Light the beacon" and not replacement.hints
    print("Actual missing seq 9: no early hint, deadline abandons old generation, fresh state recovers")

    # Subscription installed at r42 misses r42 if it only accepts future revisions.
    # Retained-log catch-up instead starts strictly AFTER the captured r40 cut.
    def resulting_objective(subscribe_after_revision):
        subscriber = Client()
        subscriber.receive(snapshot)
        updates = [event for event in history[:2] if event[0] > subscribe_after_revision]
        for msg in route(2, 8, updates, "B"):
            subscriber.receive(msg)
        return subscriber.objective
    assert resulting_objective(42) == "Align the lenses"
    assert resulting_objective(40) == "Light the beacon"
    print("r42 at the join boundary: naive live-only subscription loses it; catch-up keeps it")

if __name__ == "__main__":
    exercise()
