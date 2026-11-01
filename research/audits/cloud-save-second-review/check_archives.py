"""Read-only checks of the published finite filesystem receipts; no replacement calls."""
import hashlib,json,sys
from pathlib import Path

def need(value,message):
 if not value:raise ValueError(message)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def payload(rev):
 text=(rev+':payload:')*1024
 raw=json.dumps({'rev':rev,'payload':text,'digest':hashlib.sha256(text.encode()).hexdigest()},sort_keys=True).encode()
 return {'rev':rev,'bytes':len(raw),'file_sha256':hashlib.sha256(raw).hexdigest()}
def main(root):
 root=Path(root);checks=[]
 for line in (root/'SHA256SUMS').read_text().splitlines():
  digest,name=line.split(maxsplit=1);need(sha(root/name)==digest,'archive manifest '+name);checks.append('manifest:'+name)
 accepted=[]
 for p in [root,root/'review'/'final']:
  r=json.loads((p/'results.json').read_text());need(r['code_sha256']==sha(p/'experiment.py')==sha(root/'experiment.py'),'exact frozen source');need((p/'stderr.txt').read_bytes()==b'','stderr');need(r['multiprocessing_start_method']=='spawn','spawn');need(len(r['traces'])==2,'trace count')
  for i,t in enumerate(r['traces']):
   need(t['case']==['stale_replace_counterexample','arranged_presyscall_recheck'][i],'case');need(t['filesystem']=='tmpfs','recorded filesystem');need(t['after_B_publication']==payload('B'),'B digest');need(t['final']==payload('A' if i==0 else 'B'),'final bytes digest');need(t['expected_final']==('A' if i==0 else 'B'),'expected label');need(type(t['worker']['published']) is bool and t['worker']['published']==(i==0),'published flag');need(t['worker']['completion_accepted'] is False,'completion flag');need(t['temporary_directory_removed'] is True,'cleanup flag');need(t['barrier_order']==['old_baseline_checked','B_replace_returned_and_read','epoch_invalidated','old_writer_released','worker_joined','final_read'],'declared order')
  accepted.append(r['traces'])
 need(accepted[0]==accepted[1],'author/reviewer traces');print(json.dumps({'status':'PASS','manifest_entries':len(checks),'archived_invocations':2,'archived_traces_per_invocation':2,'new_filesystem_executions':0,'scope':'record consistency plus source inspection, not newly observed scheduling or authenticity'},indent=2))
if __name__=='__main__':
 need(len(sys.argv)==2,'usage: check_archives.py EXPERIMENT_ROOT');main(sys.argv[1])
