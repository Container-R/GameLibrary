import json,hashlib,subprocess,sys,shutil
from fractions import Fraction
from pathlib import Path
ROOT=Path(__file__).resolve().parent
s=json.loads((ROOT/'fixture/results/summary.json').read_text())
def need(ok,why):
 if not ok:raise RuntimeError(why)
def half_up(f):return (f.numerator*2+f.denominator)//(f.denominator*2)
straight=[240,120,60,85];associated=[80,40,20,85]
correct=[half_up(Fraction(x,3)) for x in straight[:3]]+[255]
wrong=[half_up(Fraction(x,3)) for x in associated[:3]]+[255]
expected=[('associate','RGBA',straight,'RGBa',associated),('unassociate-exact-selected-tuple','RGBa',associated,'RGBA',straight),('correct-straight','RGBA',straight,'RGBA',correct),('correct-converted','RGBA',straight,'RGBA',correct),('misinterpreted-associated-bytes-as-straight','RGBA',associated,'RGBA',wrong),('opaque-associate','RGBA',[240,120,60,255],'RGBa',[240,120,60,255]),('opaque-over','RGBA',[240,120,60,255],'RGBA',[240,120,60,255]),('transparent-associate','RGBA',[240,120,60,0],'RGBa',[0,0,0,0]),('transparent-unassociate','RGBa',[0,0,0,0],'RGBA',[0,0,0,0]),('transparent-original-over','RGBA',[240,120,60,0],'RGBA',[0,0,0,255]),('transparent-converted-over','RGBA',[0,0,0,0],'RGBA',[0,0,0,255])]
need(len(s['operations'])==11,'count')
for row,(name,im,ib,om,ob) in zip(s['operations'],expected,strict=True):
 need((row['name'],row['input_mode'],row['input_bytes'],row['output_mode'],row['output_bytes'])==(name,im,ib,om,ob),name)
 if row['operation']=='alpha_composite':need(row['background_bytes']==[0,0,0,255],'background')
need((s['groups'],s['conversion_calls'],s['composite_calls'])==(5,5,6),'counts')
for f,h in s['source_sha256'].items():need(hashlib.sha256((ROOT/'fixture'/f).read_bytes()).hexdigest()==h,'sourcehash')
for f,h in s['runtime_files'].items():need(hashlib.sha256(Path(f).read_bytes()).hexdigest()==h,'runtimehash')
neg=[]
for kind in ['optimized','dependency-import-failure']:
 d=ROOT/kind;d.mkdir();shutil.copy2(ROOT/'fixture/run.py',d/'run.py');shutil.copy2(ROOT/'fixture/contract.md',d/'contract.md');(d/'results').mkdir();(d/'results/summary.json').write_text('{"status":"PASS","seed":"stale"}')
 if kind=='dependency-import-failure':(d/'PIL.py').write_text("raise ImportError('synthetic failure before numeric operations')\n")
 cmd=[sys.executable]+(['-O'] if kind=='optimized' else [])+[str(d/'run.py')]
 p=subprocess.run(cmd,capture_output=True,timeout=10);(d/'stdout.txt').write_bytes(p.stdout);(d/'stderr.txt').write_bytes(p.stderr)
 need(p.returncode!=0 and not (d/'results/summary.json').exists(),'freshness '+kind)
 neg.append(dict(case=kind,command=cmd,exit=p.returncode,summary_exists=False))
result=dict(status='PASS',operations_checked=11,independent_rational_correct=correct,independent_rational_wrong=wrong,negatives=neg)
(ROOT/'independent-result.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
