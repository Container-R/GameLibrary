import sys,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'final-code'))
import consumer,test_pure
original=consumer.consume
seen=False
def wrapped(root,out):
 global seen
 if not seen:
  seen=True;p=out/'receipt.json';raw=p.read_bytes();r=json.loads(raw)
  r['processes'][0]['attempted_utc']='2026-11-01T00:00:00+00:00';r['processes'][0]['returned_utc']='2026-11-01T00:00:01+00:00'
  r['processes'][1]['attempted_utc']='2026-11-01T00:00:02+00:00';r['processes'][1]['returned_utc']='2026-11-01T00:00:03+00:00'
  r['processes'][2]['attempted_utc']='2026-11-01T00:00:04+00:00';r['processes'][2]['returned_utc']='2026-11-01T00:00:05+00:00'
  p.write_text(json.dumps(r))
  try:print('server_returned_before_client_launch ACCEPTED',original(root,out)['status'])
  except ValueError as e:print('chronology REJECTED',str(e))
  finally:p.write_bytes(raw)
 return original(root,out)
consumer.consume=wrapped
test_pure.FiniteOracle('test_synthetic_receipt_and_mutations').test_synthetic_receipt_and_mutations()
