"""Asset-pool lifecycle sketch; no actual particle engine."""
from dataclasses import dataclass, field

@dataclass
class Effect:
    lease: int=0
    start: int=0
    active: bool=False
    emitting: bool=False
    alive_until: list=field(default_factory=list)
    def acquire(self,t,clear):
        self.lease+=1
        self.start=t
        self.active=self.emitting=True
        if clear: self.alive_until.clear()
        self.alive_until.append(t+80)
        return self.lease
    def count(self,t):
        return sum(t<end for end in self.alive_until)
    def stop_emission(self):
        self.emitting=False
        return self.lease
    def release_callback(self,tag,guard=True):
        if guard and tag!=self.lease:
            return 'old lifecycle ignored'
        self.active=self.emitting=False
        return 'returned'

a=Effect(); old=a.acquire(0,True);a.stop_emission()
assert a.count(37)==1 and not a.emitting
next_=a.acquire(40,False)
assert a.count(40)==2 and old!=next_
print("stop then immediate reuse without clear: live count",a.count(40))
assert a.release_callback(old,False)=='returned' and not a.active
print("old delayed completion without lease guard: new effect returned")

b=Effect(); old=b.acquire(0,True); b.stop_emission()
next_=b.acquire(40,True)
assert b.count(40)==1 and b.release_callback(old)=='old lifecycle ignored'
assert b.active and b.lease==next_ and b.start==40
print("clear plus fresh lease: one new particle, old completion ignored, start",b.start)
