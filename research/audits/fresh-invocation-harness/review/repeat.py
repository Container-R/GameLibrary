import sys,json,hashlib,subprocess
from pathlib import Path
R=Path(__file__).resolve().parent;repo=Path('gamelibrary-publish-factorio').resolve();tool=R/'tool/harness.py';out=R/'evidence';out.mkdir(exist_ok=False)
reg=json.loads((R/'tool/registry.json').read_text())['fixtures']
def snapshot():
 return {str(p.relative_to(repo)):hashlib.sha256(p.read_bytes()).hexdigest() for e in reg.values() for p in (repo/e['directory']).rglob('*') if p.is_file()}
before=snapshot();results=[]
for name in reg:
 cmd=[sys.executable,'-B',str(tool),'invoke',str(repo),str(out),name,'--optimize-child'];p=subprocess.run(cmd,capture_output=True,text=True,timeout=30)
 (R/(name+'.stdout')).write_text(p.stdout);(R/(name+'.stderr')).write_text(p.stderr)
 assert p.returncode==1;d=json.loads(p.stdout);rec=json.loads((Path(d['directory'])/'receipt.json').read_text());assert rec['status']=='REJECTED' and rec['process']['exit_code']==1
 assert not (Path(d['directory'])/'work/results/summary.json').exists()
 results.append(d)
cmd=[sys.executable,'-B',str(tool),'invoke',str(repo),str(out),'godot-focus-boundary'];p=subprocess.run(cmd,capture_output=True,text=True,timeout=120)
(R/'focus.stdout').write_text(p.stdout);(R/'focus.stderr').write_text(p.stderr);assert p.returncode==0
pos=json.loads(p.stdout);assert pos['status']=='ACCEPTED';(R/'positive.json').write_text(json.dumps(pos,indent=2)+'\n')
c=subprocess.run([sys.executable,'-B',str(tool),'consume',pos['directory'],'--expected-id',pos['invocation_id']],capture_output=True,text=True,timeout=10);assert c.returncode==0
(R/'consume.stdout').write_text(c.stdout);(R/'consume.stderr').write_text(c.stderr)
assert before==snapshot();(R/'original-preservation.json').write_text(json.dumps({'files':len(before),'unchanged':True,'hashes':before},indent=2)+'\n')
(R/'rejections.json').write_text(json.dumps(results,indent=2)+'\n');print('PASS six copied -O rejects, one focus positive, archives unchanged',len(before))
