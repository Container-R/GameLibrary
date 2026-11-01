import sys,json,tempfile,uuid,copy,hashlib
from pathlib import Path
root=Path(__file__).parent/'final-code';sys.path.insert(0,str(root))
from test_pure import synthetic
from consumer import verify,SOURCES,sha
from oracle import check
with tempfile.TemporaryDirectory() as td:
 out=Path(td)/str(uuid.uuid4());out.mkdir();src=Path('/synthetic/source');old=src/'evidence'/out.name
 obj=synthetic();raw=('Godot Engine v4.6.3.stable.official.7d41c59c4 - https://godotengine.org\nRESULT_JSON='+json.dumps(obj)+'\n').encode()
 blobs={'version.stdout':b'4.6.3.stable.official.7d41c59c4\n','version.stderr':b'','behavior.stdout':raw,'behavior.stderr':b'','behavior.json':json.dumps(obj).encode()}
 for n,b in blobs.items():(out/n).write_bytes(b)
 hashes={n:sha((root/n).read_bytes()) for n in SOURCES}
 r=dict(status='PASS',uuid=out.name,source_sha256=hashes,source_after=hashes.copy(),binary_before='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3',binary_after='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3',original_process_directory=str(old),original_source_directory=str(src),base_environment={'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'},selected_environment={k:str(old/'environment'/k) for k in ('HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR')},behavior_processes=1,version_processes=1,processes=[],parsed_sha256=sha(blobs['behavior.json']),oracle=check(obj))
 for name,args in [('version',['/usr/local/bin/godot','--version']),('behavior',['/usr/local/bin/godot','--headless','--path',str(src),'--single-threaded-scene','--script',str(src/'main.gd')])]:
  r['processes'].append(dict(name=name,argv=args,status='RETURNED',returncode=0,timeout_seconds=20,pid=12,attempted_utc='2026-10-31T23:00:00+00:00',returned_utc='2026-10-31T23:00:00+00:00',stdout_sha256=sha(blobs[name+'.stdout']),stderr_sha256=sha(b'')))
 def call(x):(out/'receipt.json').write_text(json.dumps(x));return verify(root,out)
 print('synthetic control',call(r))
 mutations=[lambda x:x.__setitem__('status','RUNNING'),lambda x:x.__setitem__('behavior_processes',True),lambda x:x['processes'][0].__setitem__('returncode',False),lambda x:x['selected_environment'].__setitem__('HOME','/outside'),lambda x:x['processes'][1]['argv'].append('--extra'),lambda x:x['source_after'].__setitem__('main.gd','0'*64),lambda x:x.__setitem__('uuid',str(uuid.uuid4()))]
 for i,m in enumerate(mutations):
  x=copy.deepcopy(r);m(x)
  try:call(x)
  except (ValueError,KeyError):print('mutation',i,'REJECTED')
  else:raise RuntimeError(('false accept',i))
