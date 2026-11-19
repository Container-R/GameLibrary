"""Synthetic policy test, not SDL/API or physical-controller evidence.

Policy: collect UI-confirmed claims for a frame; validate identities and epochs,
then reject ALL contenders for a shared seat or connection. No arrival-order
winner. Serialize validate+commit with loss handling in one state owner. A UI
request is bound to seat epoch and connection incarnation, not device index.
Claims consume the confirmation and create a disarmed owner. Actual neutral/
fresh-edge gameplay gating is outside this test (see check_seat_resume.py).
Run: python check_seat_contention.py. Only stdout is written.
"""
from dataclasses import dataclass
from collections import Counter, defaultdict
import json

@dataclass(frozen=True)
class Claim:
    request: str
    seat: str
    seat_epoch: int
    device: tuple

class Model:
    def __init__(self):
        self.seats={s:dict(epoch=0,owner=None,armed=False,move=0) for s in ['P1','P2','P3']}
        self.seats['P3'].update(owner=('incumbent',1),armed=True,move=7)
        self.live={('incumbent',1),('pad',1),('other',1)}
        self.pending={}
        self.serial=0
    def ui(self,seat,device):
        self.serial+=1
        c=Claim(f'ui-{self.serial}',seat,self.seats[seat]['epoch'],device)
        self.pending[c.request]=c
        return c
    def invariant(self):
        owners=[v['owner'] for v in self.seats.values() if v['owner'] is not None]
        assert len(owners)==len(set(owners)) and set(owners)<=self.live
        assert self.seats['P3']==dict(epoch=0,owner=('incumbent',1),armed=True,move=7)
    def lose(self,device):
        self.live.discard(device)
        for s in self.seats.values():
            if s['owner']==device:s.update(owner=None,epoch=s['epoch']+1,armed=False,move=0)
        self.pending={k:c for k,c in self.pending.items() if c.device!=device}
        self.invariant()
    def frame(self,claims):
        # A real implementation must not yield between validation and commit.
        results={};valid=[];owners={s['owner'] for s in self.seats.values()}
        byrequest=defaultdict(set)
        for claim in claims:
            byrequest[claim.request].add(claim)
        for request, copies in byrequest.items():
            if len(copies)!=1:
                results[request]='conflicting_payload_for_same_ui_request'
                continue
            c=next(iter(copies))
            if self.pending.get(c.request)!=c:reason='unknown_consumed_or_invalidated_ui_request'
            elif c.device not in self.live:reason='connection_gone'
            elif self.seats[c.seat]['epoch']!=c.seat_epoch:reason='stale_seat_epoch'
            elif self.seats[c.seat]['owner'] is not None:reason='seat_occupied'
            elif c.device in owners:reason='device_occupied'
            else:reason=None
            if reason:results[c.request]=reason
            else:valid.append(c)
        byseat=Counter(c.seat for c in valid);bydevice=Counter(c.device for c in valid)
        for c in valid:
            if byseat[c.seat]>1 or bydevice[c.device]>1:
                results[c.request]='ambiguous_frame_rejected'
            else:
                s=self.seats[c.seat]
                s.update(owner=c.device,epoch=s['epoch']+1,armed=False,move=0)
                results[c.request]='claimed_confirmation_consumed'
        # Even rejected requests require new explicit UI confirmation.
        for request in byrequest:self.pending.pop(request,None)
        self.invariant()
        return results
    def gameplay(self,seat,device,epoch):
        s=self.seats[seat]
        return 'reject' if device not in self.live or s['owner']!=device or s['epoch']!=epoch or not s['armed'] else 'allow'
    def snapshot(self):
        return {k:dict(v) for k,v in self.seats.items()}

m=Model();trace=[]
def record(name,result):trace.append(dict(case=name,result=result,seats=m.snapshot()))
a=m.ui('P1',('pad',1));b=m.ui('P2',('pad',1))
r=m.frame([a,b]);assert set(r.values())=={'ambiguous_frame_rejected'}
assert m.seats['P1']['owner'] is m.seats['P2']['owner'] is None
record('same_connection_two_vacant_seats_same_frame',r)
# Both orderings must reject identically, not steal based on iteration order.
a=m.ui('P1',('pad',1));b=m.ui('P2',('pad',1));assert set(m.frame([b,a]).values())=={'ambiguous_frame_rejected'}
a=m.ui('P1',('pad',1));b=m.ui('P1',('other',1));r=m.frame([a,b]);assert set(r.values())=={'ambiguous_frame_rejected'}
record('one_seat_two_connections_same_frame',r)
a=m.ui('P1',('incumbent',1));b=m.ui('P3',('pad',1));r=m.frame([a,b]);assert set(r.values())=={'device_occupied','seat_occupied'}
record('incumbent_device_and_seat_cannot_be_stolen',r)
a=m.ui('P1',('pad',1));bad=Claim(a.request,'P2',0,a.device)
r=m.frame([a,bad]);assert r[a.request]=='conflicting_payload_for_same_ui_request'
assert m.seats['P1']['owner'] is m.seats['P2']['owner'] is None
record('same_request_key_different_payloads_fail_closed',r)
a=m.ui('P1',('pad',1));r=m.frame([a,a]);assert r[a.request]=='claimed_confirmation_consumed'
epoch=m.seats['P1']['epoch'];assert m.gameplay('P1',('pad',1),epoch)=='reject'
record('duplicate_confirmations_in_same_frame_are_one_claim',r)
baseline=m.snapshot()
replay=m.frame([a]);assert replay[a.request]=='unknown_consumed_or_invalidated_ui_request'
assert m.snapshot()==baseline
record('same_request_replayed_next_frame_does_not_change_binding',replay)
m.lose(('pad',1));m.live.add(('pad',2))
r=m.frame([a]);assert r[a.request]=='unknown_consumed_or_invalidated_ui_request'
assert m.gameplay('P1',('pad',1),epoch)=='reject'
record('accepted_claim_replayed_after_first_loss_and_replacement',r)
b=m.ui('P1',('pad',2));m.frame([b]);second_epoch=m.seats['P1']['epoch']
m.lose(('pad',2));m.live.add(('pad',3))
r=m.frame([b]);assert m.gameplay('P1',('pad',2),second_epoch)=='reject'
assert m.seats['P1']['owner'] is None and m.seats['P1']['epoch']==4
record('second_loss_rejects_second_accepted_claim_and_old_gameplay',r)
# A request can also become stale BEFORE acceptance.
c=m.ui('P1',('pad',3));m.lose(('pad',3));m.live.add(('pad',4));r=m.frame([c])
assert r[c.request]=='unknown_consumed_or_invalidated_ui_request'
record('unaccepted_request_invalidated_by_connection_loss',r)
c=m.ui('P1',('pad',4));d=m.ui('P2',('other',1));r=m.frame([c,d]);assert set(r.values())=={'claimed_confirmation_consumed'}
assert m.seats['P1']['owner']!=m.seats['P2']['owner'];record('independent_claims_can_commit_in_same_frame',r)
print(json.dumps({'scope':'synthetic arbitration policy, no hardware or SDL behavior measured',
 'policy':'reject all ambiguous valid claims per frame; explicit one-use UI identity; serialized atomic commit; connection incarnation and seat epoch checked',
 'invariants':'single owner per connection; no occupied seat theft; incumbent state unchanged; stale claims/gameplay rejected after each loss',
 'trace':trace},indent=2))
