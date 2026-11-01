"""Synthetic archive-only counterexamples; no child/native imports."""
from pathlib import Path
import sys,json,tempfile,uuid,copy
src=Path(__file__).parent/'initial-code';sys.path.insert(0,str(src.resolve()))
import check,test_pure
with tempfile.TemporaryDirectory() as t:
 rid=str(uuid.uuid4());out=Path(t)/rid;out.mkdir();d,_=test_pure.synthetic()
 (out/'stdout.txt').write_bytes(test_pure.raw(d));(out/'stderr.txt').write_bytes(b'');(out/'result.json').write_text(json.dumps(d))
 original='/synthetic/source';inv=original+'/evidence/'+rid
 sources={n:check.sha(src/n) for n in check.SOURCES}
 r={'status':'PASS','uuid':rid,'original_source':original,'original_invocation':inv,'source_before':sources,'source_after':sources,'library_before':check.LIB_SHA,'library_after':check.LIB_SHA,'base_environment':check.BASE,'selected_environment':{k:inv+'/environment/'+k for k in ['HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR']},'python_path':'/synthetic/python','python_before':'a'*64,'python_after':'a'*64,'process':{'status':'RETURNED','exit_code':0,'pid':123,'argv':['/synthetic/python',original+'/child.py'],'cwd':original,'attempted_utc':'2026-11-01T00:00:00+00:00','returned_utc':'2026-11-01T00:00:01+00:00'},'outputs':{n:check.sha(out/n) for n in ['stdout.txt','stderr.txt','result.json']}}
 for label in ['control','timeout_true','unresolved_drain','invalid_python_hash','reversed_UTC_different_separator']:
  x=copy.deepcopy(r)
  if label=='timeout_true':x['process']['timeout']=True
  if label=='unresolved_drain':x['process']['drain_incomplete']=True
  if label=='invalid_python_hash':x['python_before']=x['python_after']='z'*64
  if label=='reversed_UTC_different_separator':x['process']['attempted_utc']='2026-11-01 00:00:02+00:00';x['process']['returned_utc']='2026-11-01T00:00:01+00:00'
  (out/'receipt.json').write_text(json.dumps(x))
  try:answer=check.consume(src,out);print(label,'ACCEPTED',answer['status'])
  except Exception as e:print(label,'REJECTED',str(e))
