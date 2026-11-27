"""Synthetic modal routing and compare-and-discard; no real inventory or input device."""
class Store:
    def __init__(self):
        self.rows={'A':1,'B':1}
        self.receipts={}
    def discard(self, token, item, revision):
        request=(item,revision)
        if token in self.receipts:
            prior, result=self.receipts[token]
            if prior != request:
                return 'token-conflict'
            return result
        result='discarded' if self.rows.get(item)==revision else 'stale'
        if result=='discarded':
            del self.rows[item]
        self.receipts[token]=(request,result)
        return result

class Dialog:
    def __init__(self, store):
        self.store=store
        self.current=None
        self.down=False
    def open(self, token, item, revision, pressed):
        self.current=(token,item,revision)
        self.down=pressed
        return 'opened/cancel-focused'
    def cancel(self):
        self.current=None
        return 'cancelled'
    def edge(self, pressed, action='confirm', token=None):
        # A real input router owns the physical state. An explicitly
        # identified old activation is never applied to the new dialog.
        if token is not None and (self.current is None or self.current[0]!=token):
            return 'old-dialog'
        fresh=pressed and not self.down
        self.down=pressed
        if not fresh or self.current is None:
            return 'ignored'
        if action=='cancel':
            return self.cancel()
        if action!='confirm':
            return 'ignored'
        request=self.current
        self.current=None
        return self.store.discard(*request)

s=Store()
d=Dialog(s)
out=[d.open('d1','A',1,True),d.edge(True),d.edge(False),d.edge(True)]
assert out==['opened/cancel-focused','ignored','ignored','discarded'] and s.rows=={'B':1}
assert s.discard('d1','A',1)=='discarded'
assert s.discard('d1','B',1)=='token-conflict' and 'B' in s.rows
print('held opener and retry:',out,'still present',sorted(s.rows))

d.open('d2','B',1,False)
s.rows['B']=2
assert d.edge(True)=='stale' and s.rows['B']==2
assert d.edge(True)=='ignored'
print('same identity but newer version: stale, no discard')

d.open('d3','B',2,True)
d.cancel()
d.open('d4','A',1,True)
assert d.edge(True,token='d3')=='old-dialog'
assert d.edge(True)=='ignored'
assert d.edge(False)=='ignored'
assert d.edge(True,'cancel')=='cancelled' and s.rows['B']==2
print('old dialog rejected; fresh cancel leaves B version 2')

s.rows['A']=1
d.open('d5','A',1,False)
assert d.edge(True)=='discarded'
assert d.edge(True)=='ignored'
assert s.rows=={'B':2}
print('retry-safe and fresh explicit confirm commits only bound A')
