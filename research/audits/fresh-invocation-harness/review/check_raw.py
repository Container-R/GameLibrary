import json,sys,hashlib
from pathlib import Path
if sys.flags.optimize:raise RuntimeError('assertions required')
r=Path(__file__).resolve().parent;p=json.loads((r/'positive.json').read_text());inv=Path(p['directory']);receipt=json.loads((inv/'receipt.json').read_text())
assert receipt['status']=='ACCEPTED' and receipt['invocation_id']==p['invocation_id'] and receipt['process']['exit_code']==0 and not receipt['process']['timed_out']
for rel,d in receipt['artifacts'].items():assert hashlib.sha256((inv/rel).read_bytes()).hexdigest()==d
for mode in ['gate','naive','guarded']:
 lines=(inv/'work/results'/(mode+'.log')).read_text().splitlines();rs=[json.loads(x[12:]) for x in lines if x.startswith('RESULT_JSON=')];assert len(rs)==1
 a=rs[0];assert a==json.loads((inv/'work/results'/(mode+'.json')).read_text())
 trace=a['trace'];one=lambda k:next(x for x in trace if x['kind']==k)
 assert a['mode']==mode and a['display_server']=='headless'
 assert one('initial_focus')['owner_id']==a['old_id'] and one('dialog_focus')['owner_id']==a['close_id']
 if mode=='gate':assert a['restore_count']==0 and one('process_observation')['owner_id']==a['close_id']
 else:
  assert a['restore_count']==1 and a['new_id']!=a['old_id']
  assert one('replacement_ready')['new_path']==one('initial_focus')['path']
  request=one('restore_started');assert request['candidate_id']==a['new_id'] and request['expected_id']==a['old_id']
  expected=a['new_id'] if mode=='naive' else a['safe_id']
  for k in ['restore_returned','deferred_observation','process_observation']:assert one(k)['owner_id']==expected
  assert len([x for x in trace if x['kind']=='identity_mismatch'])==(mode=='guarded')
 print(mode,'independent raw focus identity/outcome PASS')
