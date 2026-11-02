#!/usr/bin/env python3
"""Run one frozen sequential probe in fresh isolated scratch; no audio setup."""
import hashlib,json,os,signal,subprocess,sys,tempfile,shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parent
H=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()

def invoke(cmd,cwd,env,seconds):
    p=subprocess.Popen(cmd,cwd=cwd,env=env,stdin=subprocess.DEVNULL,
                       stdout=subprocess.PIPE,stderr=subprocess.PIPE,start_new_session=True)
    timeout=False
    try:out,err=p.communicate(timeout=seconds)
    except subprocess.TimeoutExpired:
        timeout=True;os.killpg(p.pid,signal.SIGKILL);out,err=p.communicate()
    return p.returncode,out,err,timeout

def main():
    if len(sys.argv)!=2:raise SystemExit('usage: run_probe.py NEW_RESULT_DIRECTORY')
    dest=Path(sys.argv[1]);dest.mkdir(parents=True,exist_ok=False)
    record={'status':'NOT_RUN','scope':'Six sequential functional cases; no concurrency, audio device, deadline or sound-quality test.','accepted_cases':0,'not_run_cases':[1,2,3,4,5,6]}
    try:
        manifest=json.loads((ROOT/'INPUTS.json').read_text())
        expected=json.loads((ROOT/'EXPECTED.json').read_text())
        for name,sha in manifest['sha256'].items():
            if H(ROOT/name)!=sha:raise ValueError('INPUT_IDENTITY_MISMATCH')
        record['input_manifest_sha256']=H(ROOT/'INPUTS.json')
        record['inputs']=manifest['sha256']
        with tempfile.TemporaryDirectory(prefix='pa-functional-') as temp:
            work=Path(temp)
            for name in ['home','cache','config','data','tmp']:(work/name).mkdir()
            env={'PATH':os.defpath,'LANG':'C','LC_ALL':'C','HOME':str(work/'home'),
                 'XDG_CACHE_HOME':str(work/'cache'),'XDG_CONFIG_HOME':str(work/'config'),
                 'XDG_DATA_HOME':str(work/'data'),'TMPDIR':str(work/'tmp')}
            for name in ['probe.c','upstream/pa_ringbuffer.c','upstream/pa_ringbuffer.h','upstream/pa_memorybarrier.h']:
                p=work/name;p.parent.mkdir(parents=True,exist_ok=True);shutil.copyfile(ROOT/name,p)
                if H(p)!=manifest['sha256'][name]:raise ValueError('COPIED_INPUT_MISMATCH')
            rc,ver,err,to=invoke(['cc','--version'],work,env,5)
            if rc or to:raise ValueError('COMPILER_VERSION_UNAVAILABLE')
            record['compiler']=ver.decode('utf-8').splitlines()[0]
            cmd=['cc','-std=c11','-O2','-Wall','-Wextra','-Werror','-Iupstream','probe.c','upstream/pa_ringbuffer.c','-o','probe']
            record['compile_command']=cmd
            rc,out,err,to=invoke(cmd,work,env,20)
            # Raw diagnostics remain local; only bounded technical category is public-ready.
            (dest/'compile.stdout.local').write_bytes(out);(dest/'compile.stderr.local').write_bytes(err)
            record['compile_exit']=rc
            if to:raise ValueError('COMPILE_TIMEOUT')
            if rc:raise ValueError('COMPILE_FAILED')
            record['run_command']=['./probe'];record['run_attempted']=True;record['not_run_cases']=None
            rc,out,err,to=invoke(['./probe'],work,env,5)
            (dest/'observed.jsonl').write_bytes(out);(dest/'run.stderr.local').write_bytes(err)
            record['run_exit']=rc;record['output_sha256']=H(dest/'observed.jsonl')
            if to:raise ValueError('RUN_TIMEOUT')
            observed=[json.loads(line) for line in out.decode('utf-8').splitlines()]
            # Each accepted case needs all its expected phases, in the exact overall prefix.
            matched=0
            for actual,wanted in zip(observed,expected):
                if actual!=wanted:break
                matched+=1
            accepted=[]
            for case in range(1,7):
                positions=[i for i,x in enumerate(expected) if x['case']==case]
                if positions and max(positions)<matched:accepted.append(case)
            if rc or err:
                try:
                    failure=json.loads(err.decode('utf-8'))
                    failed_case=failure['case']
                    accepted=[i for i in accepted if i<failed_case]
                except Exception:accepted=[]
            record['accepted_cases']=len(accepted)
            record['observed_cases']=sorted({x['case'] for x in observed if isinstance(x,dict) and 'case' in x})
            record['not_run_cases']=[i for i in range(1,7) if i not in record['observed_cases']]
            record['observed_phases']=len(observed)
            if rc or err or observed!=expected:raise ValueError('PROBE_OR_ORACLE_FAILED')
            record['status']='PASS'
    except Exception as exc:
        record['status']='FAIL'
        record['failure_category']=str(exc) if isinstance(exc,ValueError) and str(exc).isupper() else type(exc).__name__
    (dest/'result.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n')
    print(json.dumps({'status':record['status'],'accepted_cases':record['accepted_cases']}))
    return 0 if record['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
