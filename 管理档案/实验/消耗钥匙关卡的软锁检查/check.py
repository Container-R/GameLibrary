"""Small, exhaustive check: one generic consumable key, directed passages."""
from collections import deque, defaultdict
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class State:
    room: str
    keys: int
    opened: frozenset
    collected: frozenset

def inspect(exit_from_vault=False, refund=False, drop_trap=False, gate_return=False):
    start = State("hall",1,frozenset(),frozenset())
    doors = [
        ("hall","vault","vault-door"),
        ("vault","hall","vault-door"),
        ("hall","goal","exit-door"),
    ]
    if gate_return:
        doors.pop()
        doors.extend([("hall","antechamber","exit-door"),
                      ("antechamber","hall","exit-door"),
                      ("antechamber","goal",None)])
    if exit_from_vault:
        doors.append(("vault","goal",None))
    if drop_trap:
        doors.append(("hall","pit",None))
    pickups = {"vault":"vault-refund"} if refund else {}
    pred = {start:None}
    rev = defaultdict(list)
    goal = []
    queue = deque([start])
    while queue:
        st = queue.popleft()
        if st.room == "goal":
            goal.append(st)
            continue
        edges=[]
        if st.room in pickups and pickups[st.room] not in st.collected:
            key = pickups[st.room]
            edges.append((f"take {key}",State(st.room,st.keys+1,st.opened,st.collected|{key})))
        for a,b,lock in doors:
            if a!=st.room:
                continue
            if lock is not None and lock not in st.opened:
                if st.keys:
                    edges.append((f"unlock {lock} and enter {b}",State(b,st.keys-1,st.opened|{lock},st.collected)))
            else:
                edges.append((f"enter {b}",State(b,st.keys,st.opened,st.collected)))
        for label,nxt in edges:
            rev[nxt].append(st)
            if nxt in pred:
                continue
            pred[nxt]=(st,label)
            queue.append(nxt)
    possible=set(goal)
    queue=deque(goal)
    while queue:
        st=queue.popleft()
        for before in rev[st]:
            if before not in possible:
                queue.append(before)
                possible.add(before)
    def trace(st):
        actions=[]
        while pred[st]:
            st,edge=pred[st]
            actions.append(edge)
        return list(reversed(actions))
    bad = [st for st in pred if st not in possible]
    result = {
        "reachable_states":len(pred),
        "completion_exists":bool(goal),
        "success_example":trace(goal[0]) if goal else None,
        "irrecoverable_count":len(bad),
        "first_bad_prefix":trace(bad[0]) if bad else None,
        "why_first_bad": ({"room":bad[0].room,"keys":bad[0].keys,
                           "opened":sorted(bad[0].opened),
                           "collected":sorted(bad[0].collected)} if bad else None)
    }

    if gate_return:
        same = sorted((st for st in pred if st.room == "hall" and st.keys == 0),
                      key=lambda st: tuple(sorted(st.opened)))
        result["same_room_and_key_count"] = [
            {"room": st.room, "keys": st.keys, "opened": sorted(st.opened),
             "can_continue": st in possible, "prefix": trace(st)}
            for st in same
        ]
    return result

r = {"ordinary_optional_vault":inspect(),"refund_in_vault":inspect(refund=True),
     "one_way_escape_from_vault":inspect(exit_from_vault=True),
     "refund_but_one_way_pit":inspect(refund=True,drop_trap=True)}
assert all(s["completion_exists"] for s in r.values())
assert [s["irrecoverable_count"] for s in r.values()]==[2,0,0,3]
assert r["refund_but_one_way_pit"]["first_bad_prefix"]==["enter pit"]
r["position_and_count_are_not_enough"] = inspect(gate_return=True)
a = r["position_and_count_are_not_enough"]["same_room_and_key_count"]
assert [row["can_continue"] for row in a] == [True, False]
print(json.dumps(r,indent=2))
