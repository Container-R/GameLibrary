"""Snapshot baseline dependencies with injected drop/reorder, no real network."""
from dataclasses import dataclass

world = {100:(0,100),101:(3,100),102:(4,100),103:(4,87),104:(6,85),105:(6,84)}
@dataclass(frozen=True)
class Packet:
    snapshot: int
    base: int | None
    fields: dict[int,int]

def packet(target, base=None):
    return Packet(target,base,{i:value for i,value in enumerate(world[target])
                              if base is None or world[base][i]!=value})

class Client:
    def __init__(self):
        self.cache={100:world[100]}
        self.displayed=100
        self.applied_ack=100
    def reset_baseline(self, key):
        del self.cache[key]
    def receive(self, msg):
        if msg.base is None:
            slots=[None,None]
        elif msg.base in self.cache:
            slots=list(self.cache[msg.base])
        else:
            return ('MISSING_BASE',msg.base)
        for index,value in msg.fields.items():
            slots[index]=value
        assert all(value is not None for value in slots)
        actual=tuple(slots)
        assert actual==world[msg.snapshot]
        self.cache[msg.snapshot]=actual
        self.displayed=max(self.displayed,msg.snapshot)
        self.applied_ack=max(self.applied_ack,msg.snapshot)
        return ('DECODED',msg.snapshot,actual)

a=Client()
# Packet 101 is dropped. Encoding 102 against "last sent" makes it unusable.
assert a.receive(packet(102,101))==('MISSING_BASE',101)
assert a.applied_ack==100
print('last-sent baseline after loss:',a.receive(packet(103,102)), 'applied ack:',a.applied_ack)
ok=a.receive(packet(103,100))
assert ok==('DECODED',103,(4,87))
print('same loss with retained applied baseline:',ok)
# A reorder is fine when both are decodable, but cannot rewind presentation.
assert a.receive(packet(102,100))[0]=='DECODED'
assert a.displayed==a.applied_ack==103
print('late old snapshot decoded, latest retained:',a.displayed)
a.reset_baseline(103)
assert a.receive(packet(104,103))==('MISSING_BASE',103)
print('previously acknowledged baseline evicted:',a.receive(packet(104,103)))
assert a.receive(packet(104))==('DECODED',104,(6,85))
assert a.applied_ack==104 and a.receive(packet(105,104))==('DECODED',105,(6,84))
print('full refresh reestablishes baseline: 104 then delta 105',a.cache[105])
