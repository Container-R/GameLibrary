from collections import deque
import json

edges = {
    "entry": (("hall", False),),
    "hall": (("niche", False), ("landing", True)),
    "niche": (("hall", False),),
    "landing": (("exit", False),),
    "exit": ()
}
def run(key_room, mode):
    path = [("entry", False)]
    q = deque([path])
    seen = {("entry", False) if mode == "full_state" else "entry"}
    blocked = set()
    while q:
        path = q.popleft()
        room, key = path[-1]
        if room == "exit":
            return {"reachable": True, "path": [{"room":r,"key":k} for r,k in path], "blocked_edges_seen": sorted(blocked)}
        for target, requires in edges[room]:
            if mode != "topology" and requires and not key:
                blocked.add(f"{room}->{target}: key missing")
                continue
            nxt = (target, mode != "topology" and (key or target == key_room))
            tag = nxt if mode == "full_state" else target
            if tag not in seen:
                seen.add(tag)
                q.append(path+[nxt])
    return {"reachable": False, "path": None, "blocked_edges_seen": sorted(blocked)}
results = {p:{m:run(p,m) for m in ("topology","room_only_seen","full_state")} for p in ("landing","niche")}
assert [v["reachable"] for v in results["landing"].values()] == [True,False,False]
assert [v["reachable"] for v in results["niche"].values()] == [True,False,True]
assert [x["room"] for x in results["niche"]["full_state"]["path"]] == ["entry","hall","niche","hall","landing","exit"]
print(json.dumps(results,indent=2))
