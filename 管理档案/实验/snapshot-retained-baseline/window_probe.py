"""Deterministic in-process age, exact-slot, and recovery controls."""
def value(n):
    return n*n + 11*n

class Receiver:
    def __init__(self, newest, count, distance=4, reorder=3, holes=frozenset()):
        self.slots=[None]*count
        self.newest=newest
        self.applied_ack=newest
        self.dist=distance
        self.reorder=reorder
        self.requests=[]
        self.transport_receipt=[]
        for seq in range(newest-count+1,newest+1):
            if seq not in holes:
                self.save(seq,value(seq))

    def save(self,seq,x):
        self.slots[seq%len(self.slots)]=(seq,x)

    def receive(self,seq,base,encoded):
        self.transport_receipt.append(seq)
        if seq < self.newest-self.reorder:
            return ('STALE',)
        if base is not None:
            if not 1<=seq-base<=self.dist:
                return ('BAD_REFERENCE',)
            cached=self.slots[base%len(self.slots)]
            if cached is None or cached[0]!=base:
                if not self.requests:
                    self.requests.append(('REFRESH',seq,base))
                return ('MISSING_BASE',base)
            x=cached[1]+encoded
        else:
            x=encoded
        self.newest=max(self.newest,seq)
        self.applied_ack=self.newest
        self.save(seq,x)
        for i,slot in enumerate(self.slots):
            if slot and slot[0]<self.newest-len(self.slots)+1:
                self.slots[i]=None
        if base is None and self.requests and seq>=self.requests[0][1]:
            self.requests.clear()
        return ('DECODED',seq,x)

def delta(s,b):
    return s,b,value(s)-value(b)

wide=Receiver(107,8)
assert wide.receive(*delta(104,100))==('DECODED',104,11960)
assert wide.newest==wide.applied_ack==107
short=Receiver(107,5)
assert short.receive(*delta(104,100))==('MISSING_BASE',100)
# Slot collision 100 % 5 = 105 % 5. An exact-ID comparison is essential.
assert short.slots[100%5][0]==105
print('H=107 S=104 B=100: 8 slots decode 11960, ACK stays 107; 5 slots sees ID 105 and rejects')
print('using newest by mistake:', value(107)+delta(104,100)[2])
stale=Receiver(108,8)
assert stale.receive(*delta(104,100))==('STALE',) and not stale.requests
print('H=108 S=104: stale drop before baseline lookup, zero recovery requests')
hole=Receiver(107,8,holes={106})
assert hole.receive(*delta(109,106))==('MISSING_BASE',106)
assert hole.receive(*delta(110,106))==('MISSING_BASE',106)
assert hole.transport_receipt==[109,110] and hole.applied_ack==107 and len(hole.requests)==1
print('missing in-window 106: transport saw 109/110, application ACK stays 107, one request')
assert hole.receive(108,None,value(108))==('DECODED',108,value(108)) and hole.requests
assert hole.receive(111,None,value(111))==('DECODED',111,value(111))
assert hole.receive(*delta(112,111))==('DECODED',112,value(112))
assert hole.applied_ack==112 and not hole.requests
print('older full 108 did not clear request; refresh 111 then delta 112 applied')

for d in range(1,9):
    for r in range(0,8):
        h=127
        for s in range(h-r,h+3):
            for b in range(s-d,min(s,h+1)):
                target=Receiver(h,d+r+1,d,r)
                assert target.receive(*delta(s,b))==('DECODED',s,value(s))
        target=Receiver(h,d+r,d,r)
        assert target.receive(*delta(h-r,h-r-d))[0]=='MISSING_BASE'
print('exhaustive age controls for D=1..8 and R=0..7 passed')
