"""Bounded default-region readiness diagnostic; does not overwrite main results."""
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
if sys.flags.optimize:
    raise RuntimeError('Assertions required; do not run with -O')
root=Path(__file__).resolve().parent
out=root/'results/default-region-readiness';out.mkdir(exist_ok=True)
(out/'verification.json').unlink(missing_ok=True)
work=Path(tempfile.mkdtemp(prefix='gamelibrary-nav-diagnostic-'));project=work/'project';project.mkdir()
for n in ('project.godot','main.tscn'):shutil.copy2(root/n,project/n)
s=(root/'main.gd').read_text()
for line in ('    NavigationServer2D.region_set_use_async_iterations(region, false)\n',
             '    NavigationServer2D.region_set_enabled(region, true)\n'):
    assert s.count(line)==1
    s=s.replace(line,'')
needle='for region in regions:\n        if NavigationServer2D.region_get_iteration_id(region) == 0:'
assert s.count(needle)==1
s=s.replace(needle,'for region in regions:\n        trace.append({"kind":"region_readiness_observation","region_id":region.get_id(),"region_iteration":NavigationServer2D.region_get_iteration_id(region),"region_async":NavigationServer2D.region_get_use_async_iterations(region),"region_enabled":NavigationServer2D.region_get_enabled(region),"map_iteration":current})\n        if NavigationServer2D.region_get_iteration_id(region) == 0:')
s=s.replace('"region_async":false,"region_enabled":true','"region_async":"default","region_enabled":"default"')
(project/'main.gd').write_text(s);(out/'main.gd.txt').write_text(s)
env=os.environ.copy()
for k in ('HOME','XDG_CACHE_HOME','XDG_DATA_HOME','XDG_CONFIG_HOME'):
    p=work/k;p.mkdir();env[k]=str(p)
env['GODOT_SILENCE_ROOT_WARNING']='1';binary=shutil.which('godot');assert binary
command=[binary,'--headless','--path',str(project),'--single-threaded-scene','--','guarded']
manifest={'command':command,'source_sha256':{n:hashlib.sha256((project/n).read_bytes()).hexdigest() for n in ('main.gd','main.tscn','project.godot')},
          'base_main_sha256':hashlib.sha256((root/'main.gd').read_bytes()).hexdigest(),
          'diagnostic_runner_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
          'binary_sha256':hashlib.sha256(Path(binary).read_bytes()).hexdigest(),
          'environment':{k:env[k] for k in ('HOME','XDG_CACHE_HOME','XDG_DATA_HOME','XDG_CONFIG_HOME')}}
(out/'command.json').write_text(json.dumps(manifest,indent=2)+'\n')
p=subprocess.run(command,env=env,capture_output=True,text=True,timeout=30)
(out/'stdout.log').write_text(p.stdout);(out/'stderr.log').write_text(p.stderr)
assert p.returncode==0 and not p.stderr and 'ERROR' not in p.stdout,(p.returncode,p.stdout,p.stderr)
lines=[s.removeprefix('RESULT_JSON=') for s in p.stdout.splitlines() if s.startswith('RESULT_JSON=')];assert len(lines)==1
r=json.loads(lines[0]);(out/'result.json').write_text(json.dumps(r,indent=2)+'\n')
assert len(r['region_config'])==2
assert all(x['async_iterations'] and x['enabled'] and x['iteration']!=0 for x in r['region_config'])
a,b=r['queries'];assert a['path'] and b['path']
assert math.dist(a['path'][-1],a['goal'])<1e-4 and math.dist(b['path'][-1],b['goal'])>1
observations=[e for e in r['trace'] if e['kind']=='region_readiness_observation']
assert observations
early=[e for e in observations if e['map_iteration']!=0 and e['region_iteration']==0]
# Scheduling may complete region tasks before observation on another run. Record,
# but do not require an intermediate state to fabricate a universal timing rule.
verification={'exit_code':p.returncode,'checks':'passed','map_ready_region_pending_observations':len(early),
              'final_map_iteration':r['current_iteration'],'reachable_path':a['path'],'partial_path':b['path']}
(out/'verification.json').write_text(json.dumps(verification,indent=2)+'\n')
print(json.dumps(verification,indent=2))
