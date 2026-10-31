#!/usr/bin/env python3
"""Negative tests of copied evidence runner only; no ICU behavior claims."""
import hashlib,json,pathlib,shutil,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent
SOURCE=ROOT/'inputs'
OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
(OUT/'summary.json').unlink(missing_ok=True)
def check(ok,msg):
    if not ok:raise RuntimeError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
original={n:sha(SOURCE/n) for n in ['case.py','run.py']}
runner=(SOURCE/'run.py').read_text()
base=(SOURCE/'results/baseline.json').read_text()
cases={
 'optimized':('raise RuntimeError("CHILD_EXECUTED")\n',False,True),
 'child_nonzero':('raise SystemExit(7)\n',False,False),
 'malformed_payload':('print("RESULT_JSON={broken")\n',False,False),
 'multiple_payload':('print(\'RESULT_JSON={}\');print(\'RESULT_JSON={}\')\n',False,False),
 'wrong_output':('import json\nd=json.loads('+repr(base)+')\nd["format_calls"][0]["output"]="WRONG"\nprint("RESULT_JSON="+json.dumps(d))\n',False,False),
 'timeout':('import time\ntime.sleep(2)\n',True,False),
}
records=[]
for name,(child,shorten,opt) in cases.items():
    folder=OUT/name;folder.mkdir(exist_ok=True)
    (folder/'run.py').write_text(runner.replace('timeout=20','timeout=0.05') if shorten else runner)
    (folder/'case.py').write_text('from pathlib import Path\nPath(__file__).with_name("child-executed.txt").write_text("yes")\n'+child)
    (folder/'child-executed.txt').unlink(missing_ok=True)
    res=folder/'results';res.mkdir(exist_ok=True)
    stale={'status':'PASS','sentinel':'pre-existing stale success'}
    (res/'summary.json').write_text(json.dumps(stale))
    cmd=[sys.executable]+(['-O'] if opt else [])+[str(folder/'run.py')]
    p=subprocess.run(cmd,text=True,capture_output=True,timeout=5)
    (folder/'harness.stdout.txt').write_text(p.stdout);(folder/'harness.stderr.txt').write_text(p.stderr)
    row={'case':name,'command':cmd,'exit_code':p.returncode,'child_executed':(folder/'child-executed.txt').exists(),'summary_exists':(res/'summary.json').exists(),'copied_runner_sha256':sha(folder/'run.py'),'injected_child_sha256':sha(folder/'case.py'),'runner_modified':shorten}
    if row['summary_exists']:row['remaining_summary']=json.loads((res/'summary.json').read_text())
    check(p.returncode!=0,name+' incorrectly accepted')
    if opt:
        check(not row['child_executed'] and 'Refusing -O' in p.stderr,'optimized gate')
    else:
        check(not row['summary_exists'],name+' retained summary')
    records.append(row)
check({n:sha(SOURCE/n) for n in original}==original,'original changed')
(OUT/'observations.json').write_text(json.dumps({'original_source_sha256':original,'checks':records},indent=2)+'\n')
print(json.dumps(records,indent=2))
