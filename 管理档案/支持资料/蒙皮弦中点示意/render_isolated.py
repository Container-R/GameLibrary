#!/usr/bin/env python3
"""Reviewed finite POSIX wrapper; separate authorization required to execute."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import signal
import subprocess

INPUTS={'generate.py','RENDER-PROTOCOL.md','render_isolated.py'}
def sha(b):return hashlib.sha256(b).hexdigest()
def no_links(p):
    if any(q.is_symlink() for q in (p,*p.parents)):
        raise ValueError('symlink_rejected')
def directory(p,existing=False):
    no_links(p);p.mkdir(mode=0o700,exist_ok=existing)
    if not p.is_dir() or p.stat().st_mode & 0o777 != 0o700:
        raise ValueError('directory_mode_rejected')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--run-name',required=True);a=ap.parse_args()
    if os.name!='posix' or not re.fullmatch('[a-z][a-z0-9-]{0,39}',a.run_name):
        raise SystemExit('unsupported_platform_or_name')
    script=Path(os.path.abspath(__file__));no_links(script);root=script.parent
    mp=root/'render-manifest.json';no_links(mp);raw=mp.read_bytes();m=json.loads(raw)
    if set(m['inputs'])!=INPUTS:raise SystemExit('input_set_mismatch')
    originals={}
    for name,digest in m['inputs'].items():
        p=root/name;no_links(p)
        if not p.is_file():raise SystemExit('input_type_mismatch')
        originals[name]=p.read_bytes()
        if sha(originals[name])!=digest:raise SystemExit('input_hash_mismatch')
    directory(root/'isolated-runs',True)
    run=root/'isolated-runs'/a.run_name;directory(run)
    result={'status':'failed','stage':'preparation','manifest_sha256':sha(raw),
            'input_sha256':m['inputs'],'copied_inputs_verified':False,
            'generation_returncode':None,'render_returncode':None,'outputs':{},
            'scope':'original mathematical SVG and raster rendering only; not skinning execution'}
    def save():(run/'result.json').write_text(json.dumps(result,indent=2)+'\n')
    save()
    try:
        work=run/'work';logs=run/'private-logs';envdir=run/'environment'
        for p in (work,logs,envdir):directory(p)
        for name,data in originals.items():(work/name).write_bytes(data)
        if any(sha((work/n).read_bytes())!=h for n,h in m['inputs'].items()):raise ValueError('copy_hash_mismatch')
        result['copied_inputs_verified']=True
        env={'PATH':'/usr/bin:/bin','LANG':'C.UTF-8','LC_ALL':'C.UTF-8','TZ':'UTC'}
        for key in ('HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','XDG_CACHE_HOME','XDG_STATE_HOME','XDG_RUNTIME_DIR','XDG_CONFIG_DIRS','XDG_DATA_DIRS','TMPDIR','TMP','TEMP'):
            p=envdir/key.lower();directory(p)
            # Demonstrate writability before any rendering/generator child starts.
            probe=p/'write-check';probe.write_bytes(b'check');probe.unlink()
            env[key]=str(p)
        result['environment_prepared']=True;save()
        def invoke(command,label,timeout):
            with (logs/(label+'-stdout.txt')).open('wb') as out,(logs/(label+'-stderr.txt')).open('wb') as err:
                process=subprocess.Popen(command,cwd=work,env=env,stdin=subprocess.DEVNULL,stdout=out,stderr=err,start_new_session=True)
                try:code=process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    try:os.killpg(process.pid,signal.SIGKILL)
                    except ProcessLookupError:pass
                    finally:process.wait()
                    raise
            result[label+'_stdout_empty']=(logs/(label+'-stdout.txt')).stat().st_size==0
            result[label+'_stderr_empty']=(logs/(label+'-stderr.txt')).stat().st_size==0
            return code
        result['stage']='generation';save()
        result['generation_returncode']=invoke(['python3','generate.py'],'generation',10)
        if result['generation_returncode']!=0:return 1
        for name in ('skinning-chord.svg','geometry.json'):
            p=work/name;no_links(p)
            if not p.is_file() or p.stat().st_size==0:raise ValueError('missing_generated_output')
        result['stage']='render';save()
        result['render_returncode']=invoke(['inkscape','skinning-chord.svg','--export-type=png','--export-filename=skinning-chord.png'],'render',30)
        if result['render_returncode']!=0:return 1
        p=work/'skinning-chord.png';no_links(p)
        if not p.is_file() or not p.read_bytes().startswith(b'\x89PNG\r\n\x1a\n'):raise ValueError('missing_png')
        result['outputs']={n:sha((work/n).read_bytes()) for n in ('skinning-chord.svg','geometry.json','skinning-chord.png')}
        result['status']='passed';result['stage']='complete'
        return 0
    except subprocess.TimeoutExpired:result['failure_kind']='timeout';return 1
    except Exception:result['failure_kind']='preparation_or_output_error';return 1
    finally:save()
if __name__=='__main__':raise SystemExit(main())
