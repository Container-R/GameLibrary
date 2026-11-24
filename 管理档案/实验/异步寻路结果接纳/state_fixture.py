"""Deterministic application test; callbacks are injected, not engine-scheduled."""
from dataclasses import dataclass
from itertools import permutations


@dataclass(frozen=True)
class Ticket:
    life: int
    serial: int
    goal: str
    region: str
    revision: int
    query_start: int


class Actor:
    def __init__(self, guarded=True):
        self.guarded = guarded
        self.region_revision = {"east": 1, "west": 1}
        self.life = 0
        self.spawn()

    def spawn(self):
        self.life += 1
        self.serial = 0
        self.pending = None
        self.route = None
        self.mode = "idle"
        self.x = 0

    def request(self, goal, region="east"):
        self.serial += 1
        self.pending = Ticket(self.life, self.serial, goal, region,
                              self.region_revision[region], self.x)
        if self.route is None:
            self.mode = "waiting"
        return self.pending

    def complete(self, ticket, success):
        # Run validation and state write together on this model's owner thread.
        if self.guarded:
            current = self.pending
            if current is None or (ticket.life, ticket.serial) != (current.life, current.serial):
                return "unowned"
            self.pending = None  # consume this completion exactly once
            if success and ticket.revision != self.region_revision[ticket.region]:
                self.mode = "replan"
                return "replan-revision"
            if success and abs(ticket.query_start - self.x) > 2:
                self.mode = "replan"
                return "replan-start"
        else:
            self.pending = None
        if success:
            self.route, self.mode = ticket.goal, "following"
        else:
            self.route, self.mode = None, "no-path"
        return "applied"

    def state(self):
        pending = None if self.pending is None else self.pending.serial
        return (self.route, self.mode, pending)


def assert_case(name, actor, result, expected):
    got = actor.state()
    if got != expected:
        raise AssertionError((name, got, expected))
    print(f"{name}: {result}, route={got[0]}, movement={got[1]}, pending={got[2]}")


for guarded in (False, True):
    for old_success in (True, False):
        label = f"{'guarded' if guarded else 'naive'} old {'success' if old_success else 'failure'}"
        a = Actor(guarded)
        old, new = a.request("A"), a.request("B")
        if a.complete(new, True) != "applied" or a.state() != ("B", "following", None):
            raise AssertionError("setup B")
        result = a.complete(old, old_success)
        expected = ("B", "following", None) if guarded else (
            ("A", "following", None) if old_success else (None, "no-path", None))
        assert_case(label, a, result, expected)

a = Actor()
old, new = a.request("A"), a.request("B")
a.region_revision["east"] += 1
a.x = 3
assert_case("owned B failure, not stale-path replan", a, a.complete(new, False),
            (None, "no-path", None))

a = Actor()
old = a.request("A")
inbox = [(old, True)]  # received/enqueued, not yet handled by the owner
new = a.request("B")
assert_case("queued A dispatched after B replaces ticket", a, a.complete(*inbox.pop(0)),
            (None, "waiting", 2))
assert_case("B after queued A discard", a, a.complete(new, True), ("B", "following", None))

def complete_single_worker(actor, occupied_slot, completion, success):
    # Only the job owning this physical slot can release it; actor eligibility
    # is a separate check, and can already have been withdrawn by new intent.
    remaining_slot = None if completion == occupied_slot else occupied_slot
    return remaining_slot, actor.complete(completion, success)


a = Actor()
slot = a.request("A")
desired_goal = "B"
a.pending = None  # B supersedes A, but cannot submit while slot is occupied.
completed = slot
slot, outcome = complete_single_worker(a, slot, completed, True)
assert_case("old A frees slot before B can submit", a, outcome, (None, "waiting", None))
if slot is not None:
    raise AssertionError("slot release")
slot = a.request(desired_goal)
slot_after_duplicate, outcome = complete_single_worker(a, slot, completed, True)
if slot_after_duplicate != slot:
    raise AssertionError("duplicate released B's slot")
assert_case("duplicate A cannot release B slot", a, outcome, (None, "waiting", 2))
slot, outcome = complete_single_worker(a, slot, slot, True)
if slot is not None:
    raise AssertionError("B did not release its own slot")
assert_case("B submitted after A frees slot", a, outcome, ("B", "following", None))

a = Actor()
old, new = a.request("B"), a.request("B")
assert_case("same goal, old request first", a, a.complete(old, True), (None, "waiting", 2))
assert_case("same goal, latest request", a, a.complete(new, True), ("B", "following", None))
assert_case("duplicate latest failure", a, a.complete(new, False), ("B", "following", None))

# Split more strongly: old and new serial both 1, lifetimes differ.
b = Actor()
pooled_old = b.request("OLD")
b.spawn()
pooled_new = b.request("NEW")
if pooled_old.serial != pooled_new.serial:
    raise AssertionError("pool reuse setup")
assert_case("object reuse same serial", b, b.complete(pooled_old, True), (None, "waiting", 1))
assert_case("new lifetime result", b, b.complete(pooled_new, True), ("NEW", "following", None))

for changed in ("west", "east"):
    a = Actor()
    new = a.request("E", "east")
    a.region_revision[changed] += 1
    expected = ("E", "following", None) if changed == "west" else (None, "replan", None)
    assert_case(f"{changed} region revision", a, a.complete(new, True), expected)

for x in (2, 3):
    a = Actor()
    new = a.request("E")
    a.x = x
    expected = ("E", "following", None) if x == 2 else (None, "replan", None)
    assert_case(f"start drift {x}", a, a.complete(new, True), expected)

# Every arrival permutation of distinct callbacks A/B/C; once C is applied
# neither old success nor old failure can alter that route.
for order in permutations("ABC"):
    a = Actor()
    tickets = {goal: a.request(goal) for goal in "ABC"}
    for goal in order:
        a.complete(tickets[goal], goal != "B")
    if a.state() != ("C", "following", None):
        raise AssertionError((order, a.state()))
print("all 6 arrival permutations: C remains followed")
