import sys,json,shutil,subprocess
from pathlib import Path
if sys.flags.optimize: raise RuntimeError('run negative harness without -O')
r=Path(__file__).resolve().parent;out=r/'negatives';out.mkdir(exist_ok=False)
results=[]
for name in ['optimized','missing-library','malformed-result']:
 p=out/name;shutil.copytree(r/'fixture',p,ignore=shutil.ignore_patterns('results','__pycache__'))
 o=p/'results';o.mkdir();(o/'summary.json').write_text('{"status":"PASS","old":true}')
 if name=='missing-library':
  c=p/'compile_case.py';s=c.read_text();assert "'/lib/x86_64-linux-gnu/libshaderc.so.1'" in s;c.write_text(s.replace("'/lib/x86_64-linux-gnu/libshaderc.so.1'","'/nonexistent/reviewer-libshaderc.so'"))
 if name=='malformed-result': (p/'compile_case.py').write_text('print("RESULT_JSON={broken")\n')
 cmd=[sys.executable,*(['-O'] if name=='optimized' else []),str(p/'run.py')]
 z=subprocess.run(cmd,capture_output=True,text=True,timeout=10)
 (p/'outer.stdout').write_text(z.stdout);(p/'outer.stderr').write_text(z.stderr)
 receipt=json.loads((o/'invocation.json').read_text())
 assert z.returncode!=0 and receipt['state']=='FAILED' and not (o/'summary.json').exists()
 results.append({'case':name,'command':cmd,'returncode':z.returncode,'receipt':receipt,'old_summary_removed':True,'native_compiles':0})
(out/'observations.json').write_text(json.dumps(results,indent=2)+'\n')
print('PASS three synthetic rejects; zero native compilations')
