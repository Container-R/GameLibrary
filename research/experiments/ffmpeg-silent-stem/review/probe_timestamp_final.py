"""Pure synthetic archive probe; never launches FFmpeg or another subprocess."""
import sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'final-code-copy'))
import test_pure as t
import consumer as c
with tempfile.TemporaryDirectory() as td:
 root=Path(td);r,out=t.synthetic(root)
 for p in r['processes']:
  for key in ('attempted_utc','returned_utc'):p[key]=p[key].replace('+00:00','+01:00')
 t.bind(root,r)
 try:
  c.verify(root);print('ACCEPTED synthetic non-UTC offsets despite UTC timestamp contract')
 except Exception as e:print('REJECTED',repr(e))
