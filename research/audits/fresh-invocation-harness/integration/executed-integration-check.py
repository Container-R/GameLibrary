import json,sys,subprocess,hashlib,importlib.util
from pathlib import Path
root=Path('gamelibrary-publish-fresh').resolve();audit=root/'research/audits/fresh-invocation-harness';out=audit/'integration';h=root/'scripts/evidence/fresh/harness.py'
rows=[]
for side in ('author','review'):
 for item in json.loads((audit/side/'public-invocations.json').read_text()):
  inv=audit/item['relative_directory'];cmd=[sys.executable,'-B',str(h),'consume',str(inv),'--expected-id',item['id']];p=subprocess.run(cmd,text=True,capture_output=True,timeout=10)
  expected=0 if item['status']=='ACCEPTED' else 1
  if p.returncode!=expected:raise RuntimeError((item,p.stdout,p.stderr))
  rows.append(dict(side=side,id=item['id'],expected_status=item['status'],command=cmd,exit_code=p.returncode,stdout=p.stdout,stderr=p.stderr))
(out/'relocated-consumption.json').write_text(json.dumps(rows,indent=2)+'\n')
before=json.loads((audit/'author/original-before.json').read_text());dirs={Path(x).parts[2] for x in before};actual={str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for d in dirs for p in (root/'research/experiments'/d).rglob('*') if p.is_file()}
if actual!=before:raise RuntimeError('original archives differ')
(out/'original-preservation.json').write_text(json.dumps({'files':len(before),'full_file_set_equal':True,'all_sha256_equal':True,'directories':sorted(dirs)},indent=2)+'\n')
registry=root/'scripts/evidence/registry.json';reg=json.loads(registry.read_text());reg['checks']=[c for c in reg['checks'] if not c['id'].startswith('fresh-invocation/')]
for side in ('author','review'):
 for item in json.loads((audit/side/'public-invocations.json').read_text()):
  inv=audit/item['relative_directory'];rec=json.loads((inv/'receipt.json').read_text());base=str(inv.relative_to(root));doc=base+'/receipt.json';prefix='fresh-invocation/'+side+'/'+item['id']
  for field,offset in [('artifacts',''),('source_sha256','work/')]:
   reg['checks'].append({'kind':'manifest','id':prefix+'/'+field,'document':doc,'field':[field],'files':{k:base+'/'+offset+k for k in rec[field]}})
  for field,target in [('harness_sha256','harness.py'),('registry_sha256','registry.json')]:
   reg['checks'].append({'kind':'hash','id':prefix+'/'+field,'document':doc,'field':[field],'target':'scripts/evidence/fresh/'+target})
  if rec['status']=='ACCEPTED':
   for mode in ('gate','naive','guarded'):reg['checks'].append({'kind':'log','id':prefix+'/'+mode,'log':base+'/work/results/'+mode+'.log','parsed':base+'/work/results/'+mode+'.json'})
registry.write_text(json.dumps(reg,indent=2)+'\n')
print('relocated consumers: 2 accepted, 12 rejected; original',len(before),'files unchanged; registry',len(reg['checks']))
