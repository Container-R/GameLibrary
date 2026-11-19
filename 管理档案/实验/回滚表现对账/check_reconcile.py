"""Synthetic rollback effect reconciliation; no network, middleware, or waveform."""
from dataclasses import dataclass
import json

@dataclass(frozen=True)
class Effect:
    frame: int
    entity: str
    generation: int
    slot: str
    kind: str
    payload: str
    ttl: int = 6

    @property
    def key(self):
        return self.frame,self.entity,self.generation,self.slot,self.kind

class Presenter:
    def __init__(self):
        self.played=set()
        self.loops={}
        self.ops=[]
    def apply(self, events, current, confirmed):
        records={e.key:e for e in events}
        assert len(records)==len(events)
        requested={k:e for k,e in records.items() if e.kind=="loop" and e.frame<=current}
        for k in sorted(self.loops.keys()-requested.keys()):
            self.ops.append(("cancel_loop", k, self.loops.pop(k)))
        for k,e in sorted(requested.items()):
            old=self.loops.get(k)
            if old is None:
                self.ops.append(("start_loop",k,e.payload))
            elif old!=e.payload:
                self.ops.append(("update_loop",k,e.payload))
            self.loops[k]=e.payload
        for k,e in sorted(records.items()):
            if e.kind == "loop" or k in self.played or e.frame>current:
                continue
            if e.kind=="confirmed_one_shot" and e.frame>confirmed:
                continue
            # Old transients don't need piling up in the newest displayed frame.
            if e.kind=="predicted_one_shot" and current-e.frame>e.ttl:
                self.ops.append(("drop_expired",k,e.payload))
            else:
                self.ops.append(("play_one_shot",k,e.payload))
            self.played.add(k)

# A simulated game would rebuild only the rollback suffix then merge it with
# unaffected still-live effects; this fixture supplies fully reconciled records.
spark=Effect(10,"hero",1,"contact","predicted_one_shot","soft_chime")
wind=Effect(11,"kite",4,"flutter","loop","dry")
commit=Effect(12,"hero",1,"ticket","confirmed_one_shot","badge")
glow=Effect(13,"kite",5,"flutter","loop","wet")
second=Effect(10,"hero",1,"contact_right","predicted_one_shot","second_chime")
buried=Effect(8,"hero",1,"landing","predicted_one_shot","past_hop")
obsolete=Effect(2,"hero",1,"ripple","predicted_one_shot","too_old")
hero2=Effect(10,"hero",2,"contact","predicted_one_shot","reused_entity_new_life")
wind_corrected=Effect(11,"kite",4,"flutter","loop","bright")

p=Presenter()
trace=[]
def at(label,events,current,confirmed,expected_ops):
    count=len(p.ops)
    p.apply(events,current,confirmed)
    ops=p.ops[count:]
    assert [(op,x) for op,_,x in ops]==expected_ops, (label,ops)
    trace.append({"case":label,"ops":ops})

at("first_prediction",[spark,wind,commit],12,9,[("start_loop","dry"),("play_one_shot","soft_chime")])
at("same_frames_rebuilt_no_duplicate",[spark,wind,commit],12,9,[])
at("same_loop_corrected_payload",[spark,wind_corrected,commit],12,9,[("update_loop","bright")])
at("one_old_prediction_removed_reused_entity_new_choices",[second,hero2,glow,commit,buried,obsolete],13,10,
   [("cancel_loop","bright"),("start_loop","wet"),("drop_expired","too_old"),("play_one_shot","past_hop"),
    ("play_one_shot","second_chime"),("play_one_shot","reused_entity_new_life")])
at("confirmation_releases_only_waiting_badge",[second,hero2,glow,commit,buried,obsolete],13,12,[("play_one_shot","badge")])
at("shallow_rebuild_no_dup",[second,hero2,glow,commit,buried,obsolete],13,12,[])
late=Effect(14,"hero",1,"quest_map","confirmed_one_shot","map_marker")
at("waiting_confirmed_notice_not_treated_as_old_transient",[late],40,13,[("cancel_loop","wet")])
at("late_confirmation_still_presents_notice_once",[late],40,14,[("play_one_shot","map_marker")])
at("late_confirmation_retry_no_duplicate",[late],40,14,[])
future=Effect(41,"kite",5,"flutter_later","loop","future")
at("future_loop_not_admitted_early",[future],40,14,[])
at("future_loop_starts_when_frame_is_reached",[future],41,14,[("start_loop","future")])
assert [o[2] for o in p.ops if o[0]=="play_one_shot"].count("soft_chime")==1
assert all(o[0]!="cancel_loop" or o[2]!="soft_chime" for o in p.ops)
print(json.dumps({"scope":"synthetic event reconciliation, not replay or engine audio evidence",
                  "trace":trace},ensure_ascii=False,indent=2))
