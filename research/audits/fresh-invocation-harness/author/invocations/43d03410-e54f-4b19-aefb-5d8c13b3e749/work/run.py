"""Real navigation startup/pending vs reachable vs disconnected path oracles."""
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
if sys.flags.optimize:
    raise RuntimeError('Assertions required; do not run with -O')
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
(OUT/'summary.json').unlink(missing_ok=True)
binary=shutil.which('godot');assert binary
work=Path(tempfile.mkdtemp(prefix='gamelibrary-navigation-'));env=os.environ.copy()
for key in ('HOME','XDG_CACHE_HOME','XDG_DATA_HOME','XDG_CONFIG_HOME'):
    p=work/key;p.mkdir();env[key]=str(p)
env['GODOT_SILENCE_ROOT_WARNING']='1'
def execute(name,args):
    command=[binary,*args]
    (OUT/f'{name}-command.json').write_text(json.dumps({'command':command,'environment':{k:env[k] for k in ('HOME','XDG_CACHE_HOME','XDG_DATA_HOME','XDG_CONFIG_HOME')}},indent=2)+'\n')
    p=subprocess.run(command,env=env,capture_output=True,text=True,timeout=30)
    (OUT/f'{name}.stdout.log').write_text(p.stdout);(OUT/f'{name}.stderr.log').write_text(p.stderr)
    # Actual 4.6.3 initial probe emitted no diagnostic: no expected-error exemption.
    assert p.returncode==0 and not p.stderr and 'ERROR' not in p.stdout,(name,p.returncode,p.stdout,p.stderr)
    return p.stdout
version=execute('version',['--version']).strip()
help_text=execute('help',['--help'])
for flag in ('--headless','--path','--single-threaded-scene'):assert flag in help_text
summary={'date_utc':'2026-10-31','version':version,'platform':platform.platform(),'python':platform.python_version(),
         'binary_sha256':hashlib.sha256(Path(binary).read_bytes()).hexdigest(),
         'source_sha256':{n:hashlib.sha256((ROOT/n).read_bytes()).hexdigest() for n in ('main.gd','main.tscn','project.godot','run.py')},'runs':[]}
def distance(a,b):return math.hypot(a[0]-b[0],a[1]-b[1])
for mode in ('naive','guarded'):
    raw=execute(mode,['--headless','--path',str(ROOT),'--single-threaded-scene','--',mode])
    lines=[s.removeprefix('RESULT_JSON=') for s in raw.splitlines() if s.startswith('RESULT_JSON=')]
    assert len(lines)==1
    r=json.loads(lines[0]);(OUT/f'{mode}.json').write_text(json.dumps(r,indent=2)+'\n')
    assert r['mode']==mode and r['display_server']=='headless' and r['initial_iteration']==0
    assert r['geometry']==[[[0,0],[0,10],[30,10],[30,0]],[[100,0],[100,10],[110,10],[110,0]]]
    assert r['requested_config']=={'map_async':False,'region_async':False,'region_enabled':True,'edge_margin':0.1,'layers':1}
    assert all(q['map_id']==r['map_id'] and q['layers']==1 for q in r['queries'])
    if mode=='naive':
        assert r['current_iteration']==0 and r['registered_regions']==[]
        assert len(r['queries'])==1
        q=r['queries'][0];assert q['label']=='pre_sync_reachable' and q['path']==[] and q['iteration']==0
        classification='pending_navigation; naive empty=>unreachable would be premature'
    else:
        assert r['current_iteration']!=0 and r['current_iteration']!=r['initial_iteration']
        assert r['async_iterations'] is False and abs(r['edge_margin']-0.1)<1e-6 and r['links_count']==0
        assert len(r['registered_regions'])==2 and len(set(r['registered_regions']))==2
        assert len(r['region_config'])==2
        for region in r['region_config']:
            assert region['enabled'] and not region['async_iterations'] and region['layers']==1
            assert region['iteration']!=0 and region['connections']==0 and region['map_id']==r['map_id']
        matching=[i for i,e in enumerate(r['trace']) if e['kind']=='matching_map_changed' and e['map_id']==r['map_id'] and e['iteration']!=0]
        ready=[i for i,e in enumerate(r['trace']) if e['kind']=='ready_predicate']
        assert matching and len(ready)==1 and min(matching)<ready[0]
        assert len(r['queries'])==2
        reachable,disconnected=r['queries']
        assert reachable['label']=='synced_reachable' and disconnected['label']=='synced_disconnected'
        for q in r['queries']:
            assert q['iteration']==r['current_iteration'] and q['path']
            assert all(len(v)==2 and all(math.isfinite(x) for x in v) for v in q['path'])
            assert distance(q['path'][0],q['start'])<1e-4
            assert distance(q['closest_goal'],q['goal'])<1e-4
            assert q['start_region_id'] in r['registered_regions'] and q['goal_region_id'] in r['registered_regions']
        assert reachable['start_region_id']==reachable['goal_region_id']
        assert distance(reachable['path'][-1],reachable['goal'])<1e-4
        assert disconnected['start_region_id']!=disconnected['goal_region_id']
        assert distance(disconnected['path'][-1],disconnected['goal'])>1
        # Original geometry establishes a disconnected control independently of path output.
        assert all(-1e-4<=p[0]<=30+1e-4 and -1e-4<=p[1]<=10+1e-4 for p in disconnected['path'])
        classification='reachable endpoint + nonempty partial route to disconnected target'
    summary['runs'].append({'mode':mode,'checks':'passed','classification':classification,'diagnostic':'stderr empty; no ERROR exemption'})
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
