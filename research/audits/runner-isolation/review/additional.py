import sys,json,tempfile
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).parent/'fixture'))
from isolation import prepare_environment,KEYS
checks=[]
def rejects(label,fn):
 try:fn()
 except ValueError:checks.append(label)
 else:raise RuntimeError(label+' accepted')
with tempfile.TemporaryDirectory() as t:
 outer=Path(t);real=outer/'real';real.mkdir();root=real/'root';root.mkdir()
 alias=outer/'alias';alias.symlink_to(real,target_is_directory=True)
 rejects('ancestor symlink',lambda:prepare_environment({},alias/'root'))
 rejects('literal parent traversal',lambda:prepare_environment({},real/'..'/'real'/'root'))
 reserved=root/'HOME';reserved.symlink_to(outer/'nonexistent')
 rejects('dangling reserved symlink',lambda:prepare_environment({},root))
 if list(root.iterdir())!=[reserved]:raise RuntimeError('preflight mutated root')
 reserved.unlink()
 original=Path.mkdir
 def fail_later(p,*a,**kw):
  if p.name=='XDG_CONFIG_HOME':raise PermissionError('synthetic creation failure')
  return original(p,*a,**kw)
 base={'HOME':'prior','SECRET_SENTINEL':'not emitted'};before=dict(base)
 try:
  with patch.object(Path,'mkdir',fail_later):prepare_environment(base,root)
 except PermissionError:pass
 else:raise RuntimeError('injected failure swallowed')
 if base!=before or sorted(p.name for p in root.iterdir())!=['HOME','XDG_CACHE_HOME']:raise RuntimeError('partial failure mismatch')
 checks.append('partial creation propagates and remains caller owned; base unchanged')
print(json.dumps({'status':'PASS','checks':checks,'synthetic_children':0,'engine_processes':0},indent=2))
