"""Deterministic miniature generator, no multiplayer or cross-engine claim."""
import hashlib,json,random

world=20261119
chunks=[(-1,2),(0,2),(1,2)]
assets=["moss","fern","reed","lichen"]

def seed(phase,cx,cy,slot):
    # Internal schema and restricted ASCII names only, fixed UTF-8 serialization.
    record=["game-atlas-v1",world,phase,cx,cy,slot]
    data=json.dumps(record,ensure_ascii=True,separators=(",",":")).encode("utf-8")
    return int.from_bytes(hashlib.sha256(data).digest()[:8],"big")

def shared_chunk(order,extra):
    rng=random.Random(world)
    out={}
    for x,y in order:
        direction=rng.randrange(4)
        for _ in range(extra if x==0 else 0): rng.randrange(100)
        out[f"{x},{y}"]=[direction,rng.randrange(3)]
    return out

def scoped_chunk(order,extra,assets_in=assets):
    out={}
    for x,y in order:
        layout=random.Random(seed("layout",x,y,"turn-and-height"))
        props=random.Random(seed("decoration",x,y,"ground-plant"))
        for _ in range(extra if x==0 else 0): props.randrange(100)
        candidate=sorted(assets_in,key=lambda a:a.encode("ascii"))[props.randrange(len(assets_in))]
        out[f"{x},{y}"]={"layout":[layout.randrange(4),layout.randrange(3)],"ground_plant":candidate}
    return out

orig=shared_chunk(chunks,0)
extra=shared_chunk(chunks,1)
extra3=shared_chunk(chunks,3)
reverse=shared_chunk(chunks[::-1],0)
local=scoped_chunk(chunks,0)
variant=scoped_chunk(chunks[::-1],3,assets[::-1])
assert orig!=extra and orig!=extra3 and orig!=reverse
assert {k:v["layout"] for k,v in local.items()}=={k:v["layout"] for k,v in variant.items()}
# A single draw may happen to select the same asset; choose enough draws to get a
# real behavior difference, not an accidental equality proof.
assert variant["0,2"]["ground_plant"]!=local["0,2"]["ground_plant"]
assert all(variant[k]==local[k] for k in local if k!="0,2")
assert scoped_chunk(chunks[::-1],0,assets[::-1])==local
assert seed("layout",-1,2,"turn-and-height")!=seed("layout",1,2,"turn-and-height")
assert seed("layout",-1,2,"turn-and-height")!=seed("decoration",-1,2,"turn-and-height")
fixed64={"record":["game-atlas-v1",world,"layout",-1,2,"turn-and-height"],
         "u64_hex":f"{seed('layout',-1,2,'turn-and-height'):016x}"}
print(json.dumps({"scope":"synthetic map domain tests using actual stdlib PRNG",
                  "shared_baseline":orig,"shared_extra_draw_one_chunk":extra,
                  "shared_three_extra_draws_one_chunk":extra3,
                  "shared_reversed_load_order":reverse,"scoped_baseline":local,
                  "scoped_with_extra_draw_reversed_order":variant,
                  "canonical_serialization_test_vector":fixed64},sort_keys=True,indent=2))
