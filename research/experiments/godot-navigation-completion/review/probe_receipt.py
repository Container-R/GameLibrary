"""Synthetic portable receipt consistency checks; no engine imports/launches."""
import sys,json,tempfile,uuid,copy,hashlib
from pathlib import Path
src=Path(sys.argv[1]).resolve();sys.path.insert(0,str(src))
import consumer,test_pure
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
with tempfile.TemporaryDirectory() as temp:
 out=Path(temp)/str(uuid.uuid4());out.mkdir();d=test_pure.fixture();original='/synthetic/source';inv=original+'/evidence/'+out.name
 (out/'version.stdout').write_text('4.6.3.stable.official.7d41c59c4\n');(out/'version.stderr').write_bytes(b'')
 (out/'behavior.stdout').write_text('Godot Engine v4.6.3.stable.official.7d41c59c4 - https://godotengine.org\nRESULT_JSON='+json.dumps(d)+'\n');(out/'behavior.stderr').write_bytes(b'');(out/'behavior.json').write_text(json.dumps(d))
 sources={n:sha(src/n) for n in consumer.SOURCES}
 r={'status':'PASS','uuid':out.name,'source_sha256':sources,'source_after':sources,'binary_before':'f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3','binary_after':'f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3','original_source_directory':original,'original_process_directory':inv,'base_environment':{'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'},'selected_environment':{k:inv+'/environment/'+k for k in ['HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR']},'behavior_processes':1,'version_processes':1,'processes':[],'parsed_sha256':sha(out/'behavior.json'),'oracle':consumer.check(d)}
 for i,name in enumerate(['version','behavior']):
  argv=['/usr/local/bin/godot','--version'] if i==0 else ['/usr/local/bin/godot','--headless','--path',original,'--single-threaded-scene','--script',original+'/main.gd']
  r['processes'].append({'name':name,'argv':argv,'timeout_seconds':[10,20][i],'status':'RETURNED','attempted_utc':f'2026-11-01T00:00:0{i*2}+00:00','returned_utc':f'2026-11-01T00:00:0{i*2+1}+00:00','pid':100+i,'returncode':0,'stdout_sha256':sha(out/(name+'.stdout')),'stderr_sha256':sha(out/(name+'.stderr'))})
 for label in ['control','timeout_flag','argv','environment','source','count_bool','reverse_time','parsed_hash']:
  x=copy.deepcopy(r)
  if label=='timeout_flag':x['processes'][1]['timeout']=True
  if label=='argv':x['processes'][1]['argv'][0]='/different/godot'
  if label=='environment':x['selected_environment']['HOME']='/outside'
  if label=='source':x['source_after']['main.gd']='0'*64
  if label=='count_bool':x['behavior_processes']=True
  if label=='reverse_time':x['processes'][1]['returned_utc']='2026-11-01T00:00:00+00:00'
  if label=='parsed_hash':x['parsed_sha256']='0'*64
  (out/'receipt.json').write_text(json.dumps(x))
  try:consumer.verify(src,out);print(label,'ACCEPTED')
  except Exception as e:print(label,'REJECTED',str(e))
