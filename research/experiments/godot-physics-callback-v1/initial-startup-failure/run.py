#!/usr/bin/env python3
"""Two bounded native configurations; no modification of archived invocations."""
import argparse, hashlib, json, os, pathlib, shutil, subprocess, tempfile, uuid, datetime, platform, re
HERE = pathlib.Path(__file__).resolve().parent
FILES = ['run.py','main.gd','project.godot','contract.json']
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def check(r, mode):
    def require(ok, message):
        if not ok: raise ValueError(message)
    require(r['mode']==mode, 'mode')
    require(type(r['body_id']) is int and r['body_id'] != 0, 'signed identity')
    require(r['entries']==(2 if mode=='direct-shape' else 1) and r['exits']==1,'entry/exit counts')
    require(r['immediate_disabled'] is (mode=='direct-shape') and r['marker_disabled'] is True and r['callback_active'] is False,'property timing')
    s=r['settings']
    require(s == {'backend':'GodotPhysics2D','separate_thread':False,'ticks_per_second':60,'sensor_radius':10,'body_radius':5,'sensor_position':[0,0],'sensor_layer':1,'sensor_mask':1,'body_layer':1,'body_mask':1,'monitoring':True}, 'actual settings')
    ev=r['events']; kinds=[e['kind'] for e in ev]
    require(all(e['body_id']==r['body_id'] for e in ev),'identity continuity')
    for key in ['outside_prephysics_boundary','inside_prephysics_boundary','initial_prephysics_boundary']:
        require(kinds.count(key)==4,key)
    ordered=['enter','setter_return','callback_return','marker','move_outside','move_inside','final']
    require([kinds.index(k) for k in ordered]==sorted(kinds.index(k) for k in ordered),'relational order')
    require(kinds.count('setter_return')==1 and kinds.count('marker')==1,'one mutation/marker')
    if mode=='direct-shape':
        ent=[i for i,k in enumerate(kinds) if k=='enter']
        require(ent[0]<kinds.index('exit')<ent[1], 'actual exit between entries')
        require(r['overlap_ids']==[r['body_id']], 'direct physical overlap')
    else: require(r['overlap_ids']==[], 'deferred overlap absent')
    for e in ev:
        if e['kind'] in ['initial_outside','move_outside','outside_prephysics_boundary']:
            require(e['body_position']==[100,0],'outside geometry')
        if e['kind'] in ['enter','move_inside','inside_prephysics_boundary','final']:
            require(e['body_position']==[0,0],'inside geometry')

def errors(stderr,mode):
    lines=stderr.splitlines()
    primary="ERROR: Can't change this state while flushing queries. Use call_deferred() or set_deferred() to change monitoring state instead."
    if mode=='deferred-shape':
        if lines: raise ValueError('Unexpected deferred stderr: '+stderr)
        return
    if lines.count(primary)!=1: raise ValueError('Expected exactly one pinned primary error: '+stderr)
    for line in lines:
        if line==primary: continue
        if re.fullmatch(r'\s+at: area_set_shape_disabled \(modules/godot_physics_2d/godot_physics_server_2d.cpp:\d+\)',line): continue
        if re.fullmatch(r'\s+GDScript backtrace \(most recent call first\):',line): continue
        if re.fullmatch(r'\s+\[0\] entered \(res://main.gd:\d+\)',line): continue
        raise ValueError('Outside restricted error envelope: '+line)
def main():
    ap=argparse.ArgumentParser(); ap.add_argument('--output-root',type=pathlib.Path,default=HERE/'results'); ap.add_argument('--engine',default='/usr/local/bin/godot'); a=ap.parse_args()
    out=a.output_root/str(uuid.uuid4()); out.mkdir(parents=True,exist_ok=False)
    receipt={'invocation':out.name,'started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'STARTED','source_sha256':{f:digest(HERE/f) for f in FILES},'binary_sha256':digest(pathlib.Path(a.engine)),'python':platform.python_version(),'platform':platform.platform(),'commands':[]}
    def save(): (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    save()
    try:
        with tempfile.TemporaryDirectory(prefix='physics-callback-') as temp:
            work=pathlib.Path(temp)
            for f in ['main.gd','project.godot']: shutil.copy2(HERE/f,work/f)
            env=os.environ.copy(); env.update({'HOME':str(work),'XDG_CACHE_HOME':str(work/'cache'),'XDG_CONFIG_HOME':str(work/'config'),'GODOT_SILENCE_ROOT_WARNING':'1'})
            commands=[('version',[a.engine,'--version'])]+[(m,[a.engine,'--headless','--path',str(work),'--script','res://main.gd','--',m]) for m in ['direct-shape','deferred-shape']]
            for name,cmd in commands:
                record={'name':name,'argv':cmd,'timeout_seconds':20}; receipt['commands'].append(record)
                try:
                    p=subprocess.run(cmd,capture_output=True,text=True,env=env,timeout=20)
                    stdout,stderr=p.stdout,p.stderr; record['returncode']=p.returncode; record['timed_out']=False
                except subprocess.TimeoutExpired as e:
                    stdout=e.stdout or b''; stderr=e.stderr or b''
                    if isinstance(stdout,bytes): stdout=stdout.decode(errors='replace')
                    if isinstance(stderr,bytes): stderr=stderr.decode(errors='replace')
                    record.update(returncode=None,timed_out=True)
                (out/(name+'.stdout')).write_text(stdout); (out/(name+'.stderr')).write_text(stderr); save()
                if record['timed_out'] or record['returncode']!=0: raise ValueError(name+' process failed')
                if name=='version':
                    if stderr: raise ValueError('version stderr')
                    continue
                errors(stderr,name)
                matches=[line[len('RESULT_JSON='):] for line in stdout.splitlines() if line.startswith('RESULT_JSON=')]
                if len(matches)!=1: raise ValueError('one result required')
                result=json.loads(matches[0]); (out/(name+'.json')).write_text(json.dumps(result,indent=2)+'\n'); check(result,name)
        if receipt['source_sha256']!={f:digest(HERE/f) for f in FILES}: raise ValueError('source changed')
        receipt['status']='PASS'
    except Exception as e:
        receipt['status']='FAIL'; receipt['failure']=repr(e)
    receipt['output_sha256']={p.name:digest(p) for p in sorted(out.iterdir()) if p.name!='receipt.json'}; save()
    print(json.dumps({'output':str(out),'status':receipt['status'],'failure':receipt.get('failure')}))
    return 0 if receipt['status']=='PASS' else 1
if __name__=='__main__': raise SystemExit(main())
