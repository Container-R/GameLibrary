from pathlib import Path
import sys
sys.path.insert(0,str((Path(__file__).parent/'initial-code').resolve()))
from test_pure import fixture
from oracle import check
for label in ['control','all_callbacks_one_frame','polygon_bool','initial_settings_bool']:
 d=fixture()
 if label=='all_callbacks_one_frame':
  for e in d['events']:e['frame']=3
  for s in d['snapshots']:s['frame']=3
 if label=='polygon_bool':d['geometry'][0]['polygon'][1]=True
 if label=='initial_settings_bool':d['initial_identities'][0]['settings']['navigation_layers']=True
 try:print(label,'ACCEPTED',check(d))
 except Exception as e:print(label,'REJECTED',str(e))
