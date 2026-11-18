from itertools import product
import json
# time in 100 ms bins; hard starts supplied by dialog sync windows, not by W3C.
A={"name":"guard","starts":[0],"length":22,"lines":1}
B={"name":"radio","starts":[10,11,12],"length":12,"lines":1}
cases={
  "two_one_line_cues":(A,B),
  "radio_wraps_to_two":(A,dict(B,lines=2)),
  "recorded_radio_moved":(A,dict(B,starts=[22,23],lines=2)),
}
def valid(cues, cap=2):
    out=[]
    for starts in product(*(c["starts"] for c in cues)):
        intervals=[(s,s+c["length"],c["lines"]) for c,s in zip(cues,starts)]
        edges=sorted({t for a,b,_ in intervals for t in (a,b)})
        peak=max(sum(lines for a,b,lines in intervals if a<=t<b) for t in edges)
        out.append({"starts_100ms": starts,"max_visible_lines":peak,"fits":peak<=cap})
    return out
results={k:valid(v) for k,v in cases.items()}
assert [sum(x["fits"] for x in a) for a in results.values()] == [3,0,2]
print(json.dumps(results,indent=2))
