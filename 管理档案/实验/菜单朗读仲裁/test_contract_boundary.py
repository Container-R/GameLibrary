"""Finite contract characterization, not production input validation."""
import json
from pathlib import Path
from causal_freshness_model import Ledger

def ledger():
    a=Ledger();a.choose('subtitle','24');a.begin('r1','subtitle');a.finish('r1','succeeded',10,'24')
    a.choose('subtitle','28');a.begin('r2','subtitle');a.finish('r2','succeeded',11,'28');a.begin('r3','subtitle')
    return a

a=ledger();a.finish('r3','succeeded',10,'24')
assert a.current('subtitle')['last_confirmed'][1]=='28'
b=ledger()
try:b.finish('r3','succeeded',11,'30')
except AssertionError:pass
else:raise AssertionError('latest conflict must be detected')
c=ledger();c.finish('r3','succeeded',10,'30')
assert c.attempts['r1'].accepted_value != c.attempts['r3'].accepted_value
assert c.current('subtitle')['last_confirmed'][1]=='28'
result={'valid_old_reply':'keeps_latest','latest_revision_conflict':'detected','historical_revision_conflict':'outside_contract_not_detected','interpretation':'invalid trace must not certify history or narration','scope':'synthetic application model; no platform, storage or audio test'}
Path(__file__).with_name('contract-boundary-result.json').write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
