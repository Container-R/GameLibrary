import json,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parent

def need(x,s):
 if not x:raise RuntimeError(s)
a=json.loads((ROOT/'normal.json').read_text());b=json.loads((ROOT/'optimized.json').read_text())
need(a.pop('optimization')==0 and b.pop('optimization')==1,'optimization flags');need(a==b,'mode mismatch')
need(a['enumerated_inputs']==12 and a['next_tick_checks']==4,'counts')
seen=set()
for row in a['traces']:
 key=(row['case'],tuple(row['actor_insertion_order']),tuple(tuple(x) for x in row['command_order']))
 need(key not in seen,'duplicate input');seen.add(key)
 if row['case']=='both-alive':
  expected={'hp':{'A':0,'B':0},'events':[[7,'damage','A','hit-A','B'],[7,'damage','B','hit-B','A'],[7,'death','A'],[7,'death','B']]}
  first=row['command_order'][0][0];target='B' if first=='A' else 'A'
  need(row['immediate']['hp']=={first:1,target:0},'sequentialwinner')
  need(row['canonical_immediate']=={'hp':{'A':1,'B':0},'events':[[7,'damage','A','hit-A','B'],[7,'death','B']]},'sortedpolicy')
 else:
  expected={'hp':{'A':0,'B':1} if row['case']=='A-already-dead' else {'A':1,'B':0},'events':[]}
  need(row['immediate']==expected and row['canonical_immediate']==expected,'deadcontrols')
 need(row['simultaneous']==expected,'literal policy')
need(len(seen)==12,'uniqueinputs')
for f,h in a['source_sha256'].items():need(hashlib.sha256((ROOT/'fixture'/f).read_bytes()).hexdigest()==h,'sourcehash')
print(json.dumps({'status':'PASS','unique_inputs':12,'normal_optimized_identical_except_flag':True,'oracle':'independent literal values, no model import'},indent=2))
