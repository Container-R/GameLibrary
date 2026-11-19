"""Synthetic regional daily reset policy verified with real ZoneInfo."""
from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo
import json
z=ZoneInfo("America/Los_Angeles")
utc=timezone.utc
def wall(d,h,m):
    return datetime(d.year,d.month,d.day,h,m)
def candidates(t):
    values=set()
    for fold in (0,1):
        v=t.replace(tzinfo=z,fold=fold).astimezone(utc)
        if v.astimezone(z).replace(tzinfo=None)==t:
            values.add(v)
    return sorted(values)
def choose(t):
    # Sample minute-resolution calendar: earliest ambiguous instant,
    # nonexistent input -> first later valid minute, determined in advance.
    for delta in range(181):
        a=candidates(t+timedelta(minutes=delta))
        if a:
            return a[0]
    raise ValueError("policy cannot resolve gap within three hours")

spring=date(2026,3,8)
autumn=date(2026,11,1)
def sample(d):
    a=wall(d-timedelta(days=1),5,0).replace(tzinfo=z)
    b=wall(d,5,0).replace(tzinfo=z)
    start,end=[i.astimezone(utc) for i in (a,b)]
    return {"start":start.isoformat(),"end":end.isoformat(),
            "elapsed_hours":(end-start).total_seconds()/3600,
            "python_same_zone_delta_hours":(b-a).total_seconds()/3600,
            "wrong_24h_local_time":(start+timedelta(hours=24)).astimezone(z).isoformat()}
s,t=sample(spring),sample(autumn)
assert s["elapsed_hours"]==23 and t["elapsed_hours"]==25
assert s["python_same_zone_delta_hours"]==t["python_same_zone_delta_hours"]==24
gap=wall(spring,2,30)
amb=wall(autumn,1,30)
assert candidates(gap)==[]
g=choose(gap); assert g.astimezone(z).hour==3 and g.astimezone(z).minute==0
a=candidates(amb)
assert len(a)==2 and (a[1]-a[0]).total_seconds()==3600
assert choose(amb)==a[0]
print(json.dumps({"scope":"actual zoneinfo conversion; sample policy choices, not server runtime",
 "zone":z.key,"spring_05_to_05":s,"autumn_05_to_05":t,
 "nonexistent_0230":{"candidates":len(candidates(gap)),"selected_utc":g.isoformat(),
                   "selected_local":g.astimezone(z).isoformat()},
 "repeated_0130":{"candidates_utc":[i.isoformat() for i in a],
                 "selected_utc":choose(amb).isoformat()}},indent=2))
