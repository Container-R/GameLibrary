"""Independent literal raw RPC observation checker; no author imports/native calls."""
import json,hashlib,sys
from pathlib import Path

def need(x,label):
 if not x:raise ValueError(label)
def check(p):
 r=json.loads((p/'receipt.json').read_text());need(r['status']=='PASS','status')
 need([x['name'] for x in r['processes']]==['version','server','client'],'processes')
 for x in r['processes']:need(x['status']=='RETURNED' and type(x['exit_code']) is int and x['exit_code']==0,'exit')
 for name,h in r['output_sha256'].items():need(hashlib.sha256((p/name).read_bytes()).hexdigest()==h,'output hash')
 need(r['source_before']==r['source_after'] and r['binary_before']==r['binary_after'],'identity agreement')
 data={}
 for role in ('server','client'):
  need((p/(role+'.stderr')).read_bytes()==b'','stderr')
  lines=(p/(role+'.stdout')).read_text().splitlines()
  events=[json.loads(x[11:]) for x in lines if x.startswith('EVENT_JSON=')]
  results=[json.loads(x[12:]) for x in lines if x.startswith('RESULT_JSON=')]
  need(len(results)==1 and results[0]['trace']==events,'raw association');data[role]=results[0]
  need([x['sequence'] for x in events]==list(range(1,len(events)+1)),'sequence')
 s,c=data['server'],data['client'];cid=s['client_id']
 need(type(cid) is int and cid>1 and c['client_id']==c['unique_id']==cid and s['unique_id']==1,'peer binding')
 for x in (s,c):need(x['authority']==1 and x['path']=='/root/Fixture/Endpoint','endpoint')
 def rows(d,kind):return [x for x in d['trace'] if x['kind']==kind]
 for role,d,port in [('server',s,32187),('client',c,32188)]:
  create=rows(d,'CREATE');need(len(create)==1 and create[0]['return_code']==0 and create[0]['requested_bind_ip']=='127.0.0.1' and create[0]['requested_local_port']==port,'bind request')
  bound=rows(d,'READY' if role=='server' else 'CLIENT_BOUND');need(len(bound)==1 and bound[0]['local_port']==port,'port readback')
 enters,enq,ends,deferred,decisions=[rows(s,k) for k in ('RPC_ENTER','ENQUEUED','RPC_END','DEFERRED','DECISION')]
 outcomes=rows(c,'OUTCOME');sends=rows(c,'SUBMIT_SENT')
 need(all(len(x)==3 for x in (enters,enq,ends,deferred,decisions,outcomes,sends)),'three commands')
 naive_before={'A':0,'B':0};guard_before={'A':0,'B':0}
 for i,(actor,axis,reason,naive_after) in enumerate([('A',1,'accepted',{'A':1,'B':0}),('B',1,'ownership',{'A':1,'B':1}),('A',10000,'input_bound',{'A':10001,'B':1})]):
  entry,q,end,d,decision,out,send=[xs[i] for xs in (enters,enq,ends,deferred,decisions,outcomes,sends)]
  need(all(x['index']==i+1 for x in (entry,q,end,d,decision,out,send)),'request association')
  need(entry['sender']==end['sender']==q['captured_sender']==d['captured_sender']==decision['captured_sender']==cid,'captured sender')
  need(d['fresh_sender']==0 and d['owners']=={'A':cid,'B':1},'context/map')
  need(entry['sequence']<q['sequence']<end['sequence']<d['sequence']<decision['sequence'],'deferred ordering')
  need((entry['actor'],entry['axis'])==(actor,axis)==(q['actor'],q['axis'])==(send['actor'],send['axis']),'payload')
  need(entry['naive']==decision['before_naive']==naive_before and entry['guarded']==decision['before_guarded']==guard_before,'prior state')
  need(decision['reason']==out['reason']==reason and decision['naive']==out['naive']==naive_after and decision['guarded']==out['guarded']=={'A':1,'B':0},'policy table')
  need(out['sender']==1 and send['return_code']==0 and send['sequence']<out['sequence'],'actual outcome')
  if i:need(outcomes[i-1]['sequence']<send['sequence'],'stop and wait')
  naive_before=naive_after;guard_before={'A':1,'B':0}
 controls=rows(s,'CONTROL_SENT')+rows(c,'CONTROL_SENT');need(len(controls)==5 and sorted(x['method'] for x in controls)==['finish','outcome','outcome','outcome','welcome'] and all(x['return_code']==0 for x in controls),'control sends')
 finish=rows(s,'SERVER_FINISH_CONFIRMED');need(len(finish)==1 and finish[0]['sender']==cid and finish[0]['last_index']==3 and finish[0]['naive']==naive_before and finish[0]['guarded']==guard_before,'finish received')
 need(len(rows(c,'WELCOME'))==1 and rows(c,'WELCOME')[0]['sender']==1 and rows(c,'CLIENT_RECEIVED_ALL')[0]['outcomes']==3,'client terminal')
 need(r['orchestration'][-2:]==[{'kind':'BOTH_TERMINALS_ACCEPTED'},{'kind':'STOP_CREATED'}],'terminal barrier')
 return {'uuid':r['uuid'],'status':'ACCEPTED_OBSERVATION','client_id':cid,'version_processes':1,'server_processes':1,'client_processes':1,'command_deliveries':3,'control_deliveries':5,'naive':naive_before,'guarded':guard_before,'deferred_getters':[x['fresh_sender'] for x in deferred]}
if __name__=='__main__':print(json.dumps(check(Path(sys.argv[1])),indent=2))
