"""Generate baseline, then exactly two cache-empty import cases; stdlib only."""
import hashlib
import json
import os
from pathlib import Path
import platform
import re
import shutil
import subprocess
import sys
import tempfile
if sys.flags.optimize:
    raise RuntimeError('Assertions required; do not run with -O')
ROOT=Path(__file__).resolve().parent
OUT=ROOT/'results'; OUT.mkdir(exist_ok=True)
(OUT/'summary.json').unlink(missing_ok=True)
WORK=Path(tempfile.mkdtemp(prefix='gamelibrary-import-'))
BINARY=shutil.which('godot'); assert BINARY

def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def manifest(root):
    return {str(p.relative_to(root)):sha(p) for p in sorted(root.rglob('*')) if p.is_file()}
def environment(name):
    env=os.environ.copy()
    for key in ('HOME','XDG_CACHE_HOME','XDG_DATA_HOME','XDG_CONFIG_HOME'):
        p=WORK/'environments'/name/key; p.mkdir(parents=True); env[key]=str(p)
    env['GODOT_SILENCE_ROOT_WARNING']='1'
    return env

def invoke(label,args,env):
    (OUT/f'{label}-command.json').write_text(json.dumps({'command':[BINARY,*args], 'environment':{k:env[k] for k in ('HOME','XDG_CACHE_HOME','XDG_DATA_HOME','XDG_CONFIG_HOME')}},indent=2)+'\n')
    p=subprocess.run([BINARY,*args],env=env,capture_output=True,text=True,timeout=40)
    (OUT/f'{label}.log').write_text(p.stdout+p.stderr)
    assert p.returncode==0 and not p.stderr and 'ERROR' not in p.stdout,(label,p.returncode,p.stdout,p.stderr)
    return p.stdout

env=environment('baseline')
version=invoke('version',['--version'],env).strip()
help_text=invoke('help',['--help'],env)
for flag in ('--headless','--import','--path'): assert flag in help_text
base=WORK/'baseline'; shutil.copytree(ROOT/'seed',base)
assert not (base/'.godot').exists()
initial=manifest(base)
invoke('baseline-default-import',['--headless','--path',str(base),'--import'],env)
sidecar=base/'asset.svg.import'
original=sidecar.read_text(); (OUT/'baseline-default.svg.import').write_text(original)
assert len(re.findall(r'^svg/scale=1\.0$',original,re.M))==1
changed,n=re.subn(r'^svg/scale=1\.0$','svg/scale=2.0',original,flags=re.M); assert n==1
sidecar.write_text(changed)
(OUT/'baseline-configured-before-reimport.svg.import').write_text(changed)
# Force a genuine clean importer pass; retain metadata, remove only generated baseline cache.
shutil.rmtree(base/'.godot')
invoke('baseline-configured-import',['--headless','--path',str(base),'--import'],env)

def probe(label,path,env):
    raw=invoke(label,['--headless','--path',str(path)],env)
    lines=[l.removeprefix('RESULT_JSON=') for l in raw.splitlines() if l.startswith('RESULT_JSON=')]
    assert len(lines)==1
    r=json.loads(lines[0]); (OUT/f'{label}.json').write_text(json.dumps(r,indent=2)+'\n')
    assert r['display_server']=='headless'
    assert r['direct_type']==r['scene_type']=='CompressedTexture2D'
    assert r['direct_path']==r['scene_path']=='res://asset.svg' and r['same_resource']
    assert r['uid_known'] and r['uid_path']=='res://asset.svg'
    assert any('res://asset.svg' in d for d in r['scene_dependencies'])
    return r

baseline=probe('baseline-probe',base,env)
assert baseline['scale']==2 and baseline['direct_size']==baseline['scene_size']==[32,16]
# Freeze real generated metadata and UID inputs, never copy .godot into either case.
frozen=OUT/'configured-inputs'
if frozen.exists(): shutil.rmtree(frozen)
frozen.mkdir()
for p in base.iterdir():
    if p.is_file(): shutil.copy2(p,frozen/p.name)
assert 'probe.gd.uid' in manifest(frozen)
cases=[]; before={}
for name,keep,size,scale in [('kept',True,[32,16],2),('omitted',False,[16,8],1)]:
    path=WORK/name; shutil.copytree(frozen,path)
    if not keep: (path/'asset.svg.import').unlink()
    assert not (path/'.godot').exists()
    before[name]=manifest(path)
    (OUT/f'{name}-initial-manifest.json').write_text(json.dumps(before[name],indent=2)+'\n')
    case_env=environment(name)
    invoke(f'{name}-import',['--headless','--path',str(path),'--import'],case_env)
    r=probe(f'{name}-probe',path,case_env)
    assert r['scale']==scale and r['direct_size']==r['scene_size']==size
    if keep: assert r['uid']==baseline['uid']
    shutil.copy2(path/'asset.svg.import',OUT/f'{name}-after.svg.import')
    generated=[str(p.relative_to(path)) for p in (path/'.godot/imported').iterdir() if p.is_file()]
    assert any(s.endswith('.ctex') for s in generated)
    cases.append({'name':name,'initial_cache_absent':True,'work_path':str(path),'expected_size':size,
                  'actual_size':r['direct_size'],'generated_import_files':sorted(generated),'checks':'passed'})
assert set(before['kept'])-set(before['omitted'])=={'asset.svg.import'}
assert set(before['omitted'])-set(before['kept'])==set()
assert all(h==before['kept'][n] for n,h in before['omitted'].items())
summary={'date_utc':'2026-10-31','version':version,'platform':platform.platform(),'python':platform.python_version(),
         'binary_sha256':sha(Path(BINARY)),'work_dir':str(WORK),'seed_manifest':initial,
         'source_sha256':{'run.py':sha(ROOT/'run.py'),**{'seed/'+n:h for n,h in initial.items()}},
         'configured_manifest':manifest(frozen),'cases':cases,
         'config_change':{'file':'asset.svg.import','key':'params.svg/scale','from':1.0,'to':2.0},
         'oracle':'Both actual ResourceLoader and instantiated scene textures: kept32x16, omitted16x8; only target sidecar omitted'}
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
