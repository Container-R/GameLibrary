from pathlib import Path
import sys
sys.path.insert(0,str((Path(__file__).parent/'initial-code').resolve()))
from test_pure import fixture
from oracle import check
for label in ['control','test_only','resource_as_node','early_move_frame','endpoint_occupied','travel_not_transform','open_incomplete','bool_query_index']:
 d=fixture()
 if label=='test_only':d['trace'][5]['arguments']['test_only']=True
 if label=='resource_as_node':d['trace'][6]['collision']['local_shape_node_id']=d['initial']['actors'][0]['shape_resource_id']
 if label=='early_move_frame':d['trace'][5]['frame']=4
 if label=='endpoint_occupied':d['trace'][2]['hits']=d['trace'][0]['hits']
 if label=='travel_not_transform':d['trace'][6]['collision']['travel']=[.5,0,0]
 if label=='open_incomplete':d['trace'][8]['transform']['origin']=[3,0,4]
 if label=='bool_query_index':d['trace'][0]['hits'][0]['shape_index']=False
 try:check(d);print(label,'ACCEPTED')
 except Exception as e:print(label,'REJECTED',str(e))
