"""Static archival consistency only. No native execution or build authentication."""
import hashlib
import json
import math
from pathlib import Path
import sys

SOURCES = {
'run.py':'d3efc79c6961abfe0d4ff591a30a84a97921a900f77d815909824ebd76d3f7e4',
'main.gd':'128f13687cf4b150707ad23316f1dcc15a8e578d66f1f3d1c16eae5379deea50',
'project.godot':'daf4dbe55e8139a701c0755f4867d911038dc4496227abac185edd624af6d3e5',
'contract.json':'d447aadbd25f21c8e347fdec65e81084bd3b3e9be3a65dbc3164fd3625ac6f55'}
BINARY = 'f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3'
VERSION = '4.6.3.stable.official.7d41c59c4'

def need(value, message):
    if not value:
        raise ValueError(message)

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def read(p):
    return json.loads(p.read_text())

def vector(actual, expected):
    need(isinstance(actual,list) and len(actual)==len(expected), 'vector shape')
    need(all(type(a) in (int,float) and math.isfinite(a) and abs(a-e)<=1e-5 for a,e in zip(actual,expected)), 'numeric vector mismatch')

def yaw(q, degrees):
    # Compare all entries of the rotation matrix; q and -q give the same matrix.
    vector(q, q)
    need(len(q)==4 and abs(sum(v*v for v in q)-1)<=1e-5,'quaternion unit')
    x,y,z,w=q
    matrix=[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w),
            2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w),
            2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]
    c,s=math.cos(math.radians(degrees)),math.sin(math.radians(degrees))
    vector(matrix,[c,0,s,0,1,0,-s,0,c])

def pose(p, position, angle):
    vector(p['position'],position);yaw(p['rotation'],angle)

def oracle(d, mode):
    need(d['mode']==mode and d['manual']==2 and d['root_motion_local'] is False,'configuration')
    need(d['root_motion_track']==('Skeleton:root' if mode=='extract' else ''),'track')
    need(d['calls']==['advance(0)','advance(0.5)']+(['advance(0.25)'] if mode=='extract' else []),'evaluation calls')
    snaps=d['snapshots']
    need([s['label'] for s in snaps]==['initial','first_read','second_read_no_advance']+(['next_evaluation'] if mode=='extract' else []),'snapshot labels')
    for i,s in enumerate(snaps):
        pose(s['actor'],[0,0,0],0)
        vector(s['bone_position'],[1,0,0] if mode=='pose' and i else [0,0,0])
        yaw(s['bone_rotation'],22.5 if mode=='pose' and i else 0)
        delta,angle=([0,0,0],0) if mode=='pose' or i==0 else (([0.5,0,0],11.25) if i==3 else ([1,0,0],22.5))
        vector(s['delta_position'],delta);yaw(s['delta_rotation'],angle)
    need(snaps[1]['delta_position']==snaps[2]['delta_position'] and snaps[1]['delta_rotation']==snaps[2]['delta_rotation'],'repeated getter raw equality')
    need(len(d['receivers'])==(3 if mode=='extract' else 0),'receiver count')
    for i,r in enumerate(d['receivers']):
        need(type(r['application_count']) is int and r['application_count']==i,'receiver application count')
        pose(r['pose'],[i,0,0],i*22.5)
    v=d['version'];need((v['major'],v['minor'],v['patch'])==(4,6,3) and v['hash']=='7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3','recorded version')

def archive(source, evidence):
    need({n:sha(source/n) for n in SOURCES}==SOURCES,'frozen source mismatch')
    directories=sorted(p for p in evidence.iterdir() if p.is_dir())
    need(len(directories)==1,'expected one archived invocation')
    d=directories[0];r=read(d/'summary.json')
    need(r['invocation_id']==d.name and r['status']=='PASS','receipt identity/status')
    need(r['source_sha256']==SOURCES and r['engine_sha256']==BINARY,'receipt source/runtime identity')
    files={m+'.'+ext for m in ['pose','extract'] for ext in ['stdout','stderr','json']}|{'version.stdout','version.stderr'}
    need(set(r['outputs_sha256'])==files,'output manifest set')
    need({n:sha(d/n) for n in files}==r['outputs_sha256'],'output hashes')
    commands=r['commands'];need([c['name'] for c in commands]==['version','pose','extract'],'2 behavior + 1 version commands')
    for c in commands:
        need(c['exit_code']==0 and c['timed_out'] is False,'process result')
        a=c['argv'];need(a[0]==r['engine_path'],'recorded executable association')
        need(a[1:]==['--version'] if c['name']=='version' else len(a)==8 and a[1:3]==['--headless','--path'] and a[4:]==['--script','main.gd','--',c['name']],'command arguments')
        need((d/(c['name']+'.stderr')).read_bytes()==b'','stderr')
    need((d/'version.stdout').read_text().strip()==VERSION,'version stdout')
    for mode in ['pose','extract']:
        raw=(d/(mode+'.stdout')).read_text()
        need('SCRIPT ERROR:' not in raw and 'ERROR:' not in raw,'raw diagnostics')
        rows=[line[12:] for line in raw.splitlines() if line.startswith('RESULT_JSON=')]
        need(len(rows)==1,'raw result count')
        data=json.loads(rows[0]);need(data==read(d/(mode+'.json')),'raw/parsed association');oracle(data,mode)
    return {'invocation_id':d.name,'summary_sha256':sha(d/'summary.json'),'behavior_commands':2,'version_commands':1}

def main():
    need(len(sys.argv)==2,'usage: check_archives.py EXPERIMENT_ROOT')
    root=Path(sys.argv[1])
    author=archive(root,root/'results')
    reviewer=archive(root/'review/fixture',root/'review/evidence')
    need(author['invocation_id']!=reviewer['invocation_id'],'distinct invocation identities')
    print(json.dumps({'status':'PASS','scope':'static two archived invocations; no runtime execution or authenticity guarantee','source_sha256':SOURCES,'recorded_binary_sha256':BINARY,'author':author,'reviewer':reviewer},sort_keys=True))

if __name__=='__main__':
    main()
