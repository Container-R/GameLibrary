#!/usr/bin/env python3
import hashlib,json,pathlib,subprocess,sys
ROOT=pathlib.Path(__file__).resolve().parent
OUT=ROOT/'results';OUT.mkdir(exist_ok=True);(OUT/'summary.json').unlink(missing_ok=True)
if not __debug__:raise SystemExit('Refusing -O')
def check(ok,msg):
    if not ok:raise RuntimeError(msg)
cases=['baseline','naive','literal_only','swapped']; runs=[]; libraries=None
expected={'baseline':['One key','Many keys'],'literal_only':['Óné kéy','Mány kéys'],'swapped':['Many keys','One key']}
for case in cases:
    command=[sys.executable,str(ROOT/'case.py'),case]
    try:r=subprocess.run(command,text=True,capture_output=True,timeout=20)
    except subprocess.TimeoutExpired as e:
        def timeout_text(value):
            if value is None:return ''
            return value.decode('utf-8',errors='replace') if isinstance(value,bytes) else value
        (OUT/(case+'.stdout.txt')).write_text(timeout_text(e.stdout))
        (OUT/(case+'.stderr.txt')).write_text(timeout_text(e.stderr))
        (OUT/(case+'.command.json')).write_text(json.dumps({'command':command,'returncode':None,'timed_out':True,'timeout_seconds':e.timeout},indent=2)+'\n')
        (OUT/(case+'.timeout.txt')).write_text(str(e));raise
    (OUT/(case+'.stdout.txt')).write_text(r.stdout);(OUT/(case+'.stderr.txt')).write_text(r.stderr)
    (OUT/(case+'.command.json')).write_text(json.dumps({'command':command,'returncode':r.returncode},indent=2)+'\n')
    check(r.returncode==0 and not r.stderr.strip(),'subprocess failure: '+case)
    lines=[x.removeprefix('RESULT_JSON=') for x in r.stdout.splitlines() if x.startswith('RESULT_JSON=')]
    check(len(lines)==1,'payload count');data=json.loads(lines[0]);(OUT/(case+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n')
    check(data['case']==case and data['version']==[76,1,0,0] and data['locale']=='en','identity')
    if libraries is None:libraries=data['libraries']
    check(libraries==data['libraries'],'library identity consistency')
    if case=='naive':
        check(data['open']['code']>0 and not data['open']['success'] and data['format_calls']==[],'negative parse evidence')
    else:
        check(data['open']['success'] and data['open']['handle_nonnull'],'valid parse')
        check([x['number'] for x in data['format_calls']]==[1.0,2.0],'numeric inputs')
        check([x.get('output') for x in data['format_calls']]==expected[case],'actual output')
        check(all(x['status']['code']<=0 and 0<=x['returned_length']<x['capacity_utf16'] for x in data['format_calls']),'format status/size')
    runs.append({'case':case,'command':command,'exit_code':r.returncode,'checks':'passed'})
summary={'status':'PASS','version':[76,1,0,0],'libraries':libraries,'source_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ['case.py','run.py']},'runs':runs}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print('PASS four finite ICU subprocess cases; no arbitrary pattern API')
