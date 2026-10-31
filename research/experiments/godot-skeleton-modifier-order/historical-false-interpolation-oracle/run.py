import hashlib
import json
import math
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import uuid
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parent
FILES = ['run.py', 'main.gd', 'project.godot', 'contract.json', 'isolation.py']
I = [[1,0,0],[0,1,0],[0,0,1]]
Y = [[0,0,-1],[0,1,0],[1,0,0]]

def require(ok, message):
    if not ok: raise RuntimeError(message)

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def near(a,b):
    if isinstance(b,list):
        require(type(a) is list and len(a)==len(b),'shape mismatch')
        for x,y in zip(a,b): near(x,y)
    else:
        require(type(a) in (int,float) and math.isfinite(a) and abs(a-b)<=1e-5, f'numeric {a} != {b}')

def transform(t, basis, origin):
    near(t['basis'],basis); near(t['origin'],origin)
    cols=t['basis']
    for i in range(3):
        for j in range(3): near(sum(x*y for x,y in zip(cols[i],cols[j])), int(i==j))

def poses(data,p,c):
    require(len(data)==2,'bone count')
    transform(data[0]['global'],p,[0,0,0]);transform(data[1]['global'],c,[0,1,0])

def ident(x): require(type(x) is int and x!=0,'invalid exact instance ID')

def check(data):
    es=data['evaluations'];require(len(es)==2,'evaluation count')
    first=es[0]['before']; ids=[m['id'] for m in first['modifiers']]
    all_ids=[first['skeleton_id']]+ids+[t['id'] for t in first['targets']]
    for n in all_ids: ident(n)
    require(len(set(all_ids))==5,'identity overlap')
    expected=[[(Y,Y),(Y,I)],[(I,I),(Y,Y)]]
    for k,e in enumerate(es):
        require(e['index']==k,'index')
        order=[0,1] if k==0 else [1,0]
        for label in ('before','restored'):
            s=e[label];require(s['skeleton_id']==all_ids[0] and s['callback_mode']==2 and s['interpolation_mode']==2,'skeleton configuration')
            transform(s['world'],I,[0,0,0])
            require([n['id'] for n in s['children']]==[ids[i] for i in order],'actual children order')
            require([n['name'] for n in s['children']]==[['P','C'][i] for i in order],'child names')
            poses(s['poses'],I,I)
            for i,b in enumerate(s['bones']):
                require(b['name']==['P','C'][i] and b['parent']==[-1,0][i],'bone binding')
                transform(b['rest'],I,[[0,0,0],[0,1,0]][i])
                transform(s['poses'][i]['local'],I,[[0,0,0],[0,1,0]][i])
            for i,t in enumerate(s['targets']):
                require(t['id']==all_ids[3+i],'target identity')
                transform(t['world'],I,[[10,0,0],[0,1,10]][i])
            for i,m in enumerate(s['modifiers']):
                require(m['id']==ids[i] and m['bone']==i and m['bone_name']==['P','C'][i] and m['target_id']==all_ids[3+i],'modifier binding')
                for key,value in dict(forward_axis=4,primary_rotation_axis=1,relative=False,origin_from=0,duration=0,influence=1,active=True,use_angle_limitation=False,use_secondary_rotation=True).items(): require(m[key]==value,'modifier '+key)
                near(m['origin_offset'],[0,0,0]);near(m['origin_safe_margin'],.1)
                require(m['interpolating'] is False,'unexpected interpolation');near(m['interpolation_remaining'],0)
        require(len(e['stages'])==2,'stage count')
        for j,s in enumerate(e['stages']):
            require(s['phase']=='armed' and s['evaluation']==k and s['emitter']==ids[order[j]] and s['bone']==order[j],'stage emitter/order')
            poses(s['poses'],*expected[k][j])
        require(e['final']['phase']=='armed' and e['final']['evaluation']==k,'final phase')
        poses(e['final']['poses'],*expected[k][-1])
        direction=e['final']['poses'][1]['global']['basis'][2]
        near(sum(a*b for a,b in zip(direction,[0,0,1])),1 if k==0 else 0)
    trace=data['trace']
    for k,e in enumerate(es):
        selected=[x for x in trace if x.get('evaluation')==k and x.get('phase') not in ('setup','reconfigure')]
        require([x['kind'] for x in selected]==['advance_call','advance_return','stage','stage','skeleton_updated','deferred_restored'],'armed trace ordering')
        require(selected[2:4]==e['stages'] and selected[4]==e['final'],'trace association')
        require(selected[5]['poses']==e['restored']['poses'],'restore association')
    require(sum(x['kind']=='advance_call' for x in trace)==2,'advance count')
    require(sum(x['kind']=='drain_marker' for x in trace)==2,'drain count')
    for x in trace:
        require(x['kind'] in ('stage','skeleton_updated','drain_marker','advance_call','advance_return','deferred_restored'),'unknown event')
        if x.get('phase') in ('setup','reconfigure'): require(x['kind'] in ('stage','skeleton_updated','drain_marker'),'invalid setup event')

def main():
    output=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'results'
    output.mkdir(parents=True,exist_ok=True)
    (output/'summary.json').unlink(missing_ok=True)
    require(not sys.flags.optimize,'optimized Python rejected before native execution')
    from isolation import prepare_environment, validate_environment
    require(sha(ROOT/'isolation.py')=='bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970','helper identity')
    out=output/str(uuid.uuid4());out.mkdir()
    rec=dict(invocation_id=out.name,status='STARTED',started_utc=datetime.now(timezone.utc).isoformat(),python=sys.version,platform=platform.platform(),source_sha256={f:sha(ROOT/f) for f in FILES},commands=[])
    def save(): (out/'receipt.json').write_text(json.dumps(rec,indent=2)+'\n')
    save()
    try:
        engine=Path('/usr/local/bin/godot').resolve();rec['binary_sha256']=sha(engine)
        require(rec['binary_sha256']=='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3','binary changed; stop')
        with tempfile.TemporaryDirectory(prefix='skeleton-order-') as tmp:
            work=Path(tmp)
            for f in ('main.gd','project.godot'): shutil.copy2(ROOT/f,work/f)
            env,locations=prepare_environment(os.environ,work)
            env['GODOT_SILENCE_ROOT_WARNING']='1'
            rec['selected_environment_locations']=locations
            for name,cmd in [('version',[str(engine),'--headless','--version']),('behavior',[str(engine),'--headless','--path',str(work),'--script','main.gd'])]:
                validate_environment(env,work)
                entry=dict(name=name,argv=cmd,timeout_seconds=30);rec['commands'].append(entry);save()
                try:
                    p=subprocess.run(cmd,capture_output=True,env=env,timeout=30)
                    stdout,stderr=p.stdout,p.stderr;entry.update(returncode=p.returncode,timed_out=False)
                except subprocess.TimeoutExpired as exc:
                    stdout=exc.stdout or b'';stderr=exc.stderr or b''
                    if isinstance(stdout,str):stdout=stdout.encode()
                    if isinstance(stderr,str):stderr=stderr.encode()
                    (out/(name+'.stdout')).write_bytes(stdout);(out/(name+'.stderr')).write_bytes(stderr)
                    entry.update(timed_out=True);raise
                (out/(name+'.stdout')).write_bytes(stdout);(out/(name+'.stderr')).write_bytes(stderr)
                require(p.returncode==0,name+' nonzero')
                require(stderr==b'',name+' unexpected stderr')
                lines=stdout.decode('utf-8').splitlines()
                require(not any('ERROR' in line or 'WARNING' in line for line in lines),'diagnostic in stdout')
                if name=='version':
                    require(lines==['4.6.3.stable.official.7d41c59c4'],'version text');rec['version']=lines[0]
                else:
                    payload=[s[len('RESULT_JSON='):] for s in lines if s.startswith('RESULT_JSON=')]
                    require(len(payload)==1,'result payload count')
                    require(all(not line.strip() or line.startswith('Godot Engine v4.6.3.stable.official.7d41c59c4') or line.startswith('RESULT_JSON=') for line in lines),'unexpected stdout')
                    data=json.loads(payload[0]);(out/'behavior.json').write_text(json.dumps(data,indent=2)+'\n');check(data)
                    rec['behavior_observations']=dict(evaluations=2,setup_events=sum(e.get('phase') in ('setup','reconfigure') for e in data['trace']))
        require(rec['source_sha256']=={f:sha(ROOT/f) for f in FILES},'source modified')
        rec['status']='PASS'
    except BaseException as exc:
        rec['status']='FAIL';rec['error']=repr(exc);raise
    finally:
        rec['outputs_sha256']={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='receipt.json'}
        save();print(json.dumps({'status':rec['status'],'evidence':str(out)}),flush=True)
        if rec['status']=='PASS':(output/'summary.json').write_text(json.dumps(rec,indent=2)+'\n')

if __name__=='__main__':main()
