import sys,tempfile,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'final-code-copy'))
from test_pure import write_archive
from consumer import verify,sha
with tempfile.TemporaryDirectory() as t:
 root=Path(t);out,r=write_archive(root)
 verify(root,out)
 p=out/'all.json';d=json.loads(p.read_text());d['stages'][0]['d']['values'][0]['colors'][0][1]=False
 p.write_text(json.dumps(d));r['parsed_sha256']['all']=sha(p.read_bytes());(out/'receipt.json').write_text(json.dumps(r))
 try:
  verify(root,out);print('FALSE_ACCEPT: parsed numeric zero replaced by bool false; raw unchanged')
 except Exception as e:print('REJECTED:',repr(e))
