import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
FILES = ['run.py', 'main.gd', 'project.godot', 'contract.json']

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def require(v, msg):
    if not v:
        raise RuntimeError(msg)

def close(a, b):
    require(len(a) == len(b) and all(type(x) in (int, float) and math.isfinite(x) and abs(x-y) <= 1e-5 for x,y in zip(a,b)), f'{a} != {b}')

def rotation(a, degrees):
    q = [0, math.sin(math.radians(degrees)/2), 0, math.cos(math.radians(degrees)/2)]
    require(len(a) == 4 and all(type(x) in (int,float) and math.isfinite(x) for x in a), 'invalid quaternion')
    require(abs(sum(x*x for x in a)-1) <= 1e-5, 'not unit quaternion')
    require(min(sum((x-y)**2 for x,y in zip(a,q)), sum((x+y)**2 for x,y in zip(a,q))) <= 1e-10, 'rotation mismatch')

def check(data, mode):
    require(data['mode'] == mode and data['manual'] == 2 and data['root_motion_local'] is False, 'config')
    require(data['root_motion_track'] == ('Skeleton:root' if mode == 'extract' else ''), 'root path')
    require(data['calls'] == (['advance(0)', 'advance(0.5)', 'advance(0.25)'] if mode == 'extract' else ['advance(0)', 'advance(0.5)']), 'call order')
    snaps = data['snapshots']
    require([s['label'] for s in snaps] == ['initial','first_read','second_read_no_advance'] + (['next_evaluation'] if mode == 'extract' else []), 'snapshot order')
    for s in snaps:
        close(s['actor']['position'], [0,0,0]); rotation(s['actor']['rotation'], 0)
    first, second = snaps[1:3]
    require(first['delta_position'] == second['delta_position'] and first['delta_rotation'] == second['delta_rotation'], 'read consumed delta')
    if mode == 'pose':
        for s in snaps[1:]:
            close(s['bone_position'], [1,0,0]); rotation(s['bone_rotation'],22.5)
        require(data['receivers'] == [], 'unexpected receivers')
    else:
        for s in snaps:
            close(s['bone_position'],[0,0,0]); rotation(s['bone_rotation'],0)
        for s in snaps[1:3]:
            close(s['delta_position'],[1,0,0]); rotation(s['delta_rotation'],22.5)
        close(snaps[3]['delta_position'],[0.5,0,0]); rotation(snaps[3]['delta_rotation'],11.25)
        require(len(data['receivers']) == 3, 'receiver count')
        for i,r in enumerate(data['receivers']):
            require(r['application_count'] == i, 'application count')
            close(r['pose']['position'],[i,0,0]); rotation(r['pose']['rotation'],22.5*i)

def main():
    output = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'results'
    output.mkdir(parents=True, exist_ok=True)
    out = output/str(uuid.uuid4());out.mkdir()
    rec = dict(invocation_id=out.name,started_utc=datetime.now(timezone.utc).isoformat(),status='STARTED', source_sha256={f:sha(ROOT/f) for f in FILES},commands=[])
    def save(): (out/'summary.json').write_text(json.dumps(rec,indent=2)+'\n')
    save()
    try:
        engine = Path(shutil.which('godot') or '/missing/godot').resolve()
        rec['engine_path']=str(engine);rec['engine_sha256']=sha(engine)
        with tempfile.TemporaryDirectory(prefix='native-root-motion-') as tmp:
            work=Path(tmp)
            for f in ['main.gd','project.godot']: shutil.copy2(ROOT/f,work/f)
            env=os.environ.copy();env['GODOT_SILENCE_ROOT_WARNING']='1'
            for key in ['HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR']:
                p=work/key;p.mkdir();env[key]=str(p)
            for name, command in [('version',[str(engine),'--version'])]+[(mode,[str(engine),'--headless','--path',str(work),'--script','main.gd','--',mode]) for mode in ('pose','extract')]:
                try:
                    proc=subprocess.run(command,capture_output=True,timeout=20,env=env)
                except subprocess.TimeoutExpired as e:
                    (out/(name+'.stdout')).write_bytes(e.stdout or b'');(out/(name+'.stderr')).write_bytes(e.stderr or b'')
                    rec['commands'].append(dict(name=name,argv=command,timed_out=True));raise
                (out/(name+'.stdout')).write_bytes(proc.stdout);(out/(name+'.stderr')).write_bytes(proc.stderr)
                rec['commands'].append(dict(name=name,argv=command,exit_code=proc.returncode,timed_out=False))
                require(proc.returncode==0, name+' exit failure')
                require(b'ERROR:' not in proc.stderr and b'SCRIPT ERROR:' not in proc.stdout, name+' engine errors')
                if name!='version':
                    rows=[line[len('RESULT_JSON='):] for line in proc.stdout.decode().splitlines() if line.startswith('RESULT_JSON=')]
                    require(len(rows)==1,'result count')
                    data=json.loads(rows[0]);(out/(name+'.json')).write_text(json.dumps(data,indent=2)+'\n');check(data,name)
        require({f:sha(ROOT/f) for f in FILES}==rec['source_sha256'],'source changed')
        rec['status']='PASS'
    except BaseException as e:
        rec['status']='FAIL';rec['error']=repr(e);raise
    finally:
        rec['outputs_sha256']={p.name:sha(p) for p in sorted(out.iterdir()) if p.is_file() and p.name!='summary.json'}
        save();print(json.dumps(dict(output=str(out),status=rec['status'])),flush=True)

if __name__=='__main__': main()
