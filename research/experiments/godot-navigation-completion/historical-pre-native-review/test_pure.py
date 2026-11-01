"""Synthetic finite protocol records only; this file never invokes Godot."""
import copy,json,unittest,tempfile,subprocess,sys,shutil
from pathlib import Path
from oracle import check,load,VERSION,SETTINGS,CALLS
ROOT=Path(__file__).resolve().parent

def fixture():
 d={'version':VERSION.copy(),'root_id':100,'geometry':[],'identities':[],'initial_identities':[],'initial_paths':[[[2,0,2],[8,0,2]],[[2,0,2],[10,0,2]]],'events':[],'snapshots':[]}
 d['ready']={'readiness_callbacks':2,'map_id':200,'initial_iteration':0,'iteration':1,'matched':True,'active':True,'async':False,'edge_connections':False,'links':0,'up':[0,1,0],'cell_size':.25,'cell_height':.25,'registered':[201,202],'regions':[{'id':201+i,'iteration':1,'map':200,'enabled':True,'layers':1,'async':False} for i in range(2)],'projections':[{'input':v,'point':v,'owner':o} for v,o in [([2,0,2],201),([8,0,2],201),([22,0,2],202)]]}
 for i in range(2):
  x=20*i;d['geometry'].append({'vertices':[[x,0,0],[x,0,4],[x+10,0,4],[x+10,0,0]],'polygon':[0,1,2,3]})
  a={'label':['Reachable','Partial'][i],'agent_id':10+i,'parent_id':20+i,'actual_parent_id':20+i,'root_id':100,'map_id':200,'settings':SETTINGS.copy()};d['initial_identities'].append(copy.deepcopy(a));a['target']=[[8,0,2],[22,0,2]][i];d['identities'].append(a)
 pos=[[2,0,2],[2,0,2]];done=[False,False]
 def emit(kind,i,step,call='none',phase='queries',**extra):
  e={'kind':kind,'agent':i,'step':step,'frame':step+2,'phase':phase,'call':call,'agent_id':10+i,'parent_id':20+i,'position':pos[i][:]};e.update(extra);d['events'].append(e)
 for step in range(1,18):
  for i in range(2):
   if done[i]:continue
   end=d['initial_paths'][i][-1];finish=pos[i]==end
   emit('before_update',i,step)
   values=[end,finish,i==0,end]
   for c,value in zip(CALLS,values):
    emit('call_enter',i,step,c)
    if c==CALLS[0]:
     if step==1:emit('signal',i,step,c,signal='path_changed');emit('signal',i,step,c,signal='waypoint_reached',waypoint=[2,0,2])
     if finish:
      emit('signal',i,step,c,signal='waypoint_reached',waypoint=end)
      if i==0:emit('signal',i,step,c,signal='target_reached')
      emit('signal',i,step,c,signal='navigation_finished')
    emit('call_return',i,step,c,value=value)
   row={'agent':i,'step':step,'frame':step+2,'parent':pos[i][:],'next':end,'finished':finish,'reachable':i==0,'reached':finish and i==0,'final':end,'path':d['initial_paths'][i],'index':1,'distance':abs(pos[i][0]-d['identities'][i]['target'][0])};d['snapshots'].append(row);emit('after_queries',i,step,snapshot=row);done[i]=finish
  for i in range(2):
   if done[i]:continue
   old=pos[i][:];pos[i]=[pos[i][0]+.5,0,2];emit('position_assigned',i,step,phase='movement',old=old,next=d['initial_paths'][i][-1],computed=pos[i][:])
 d['steps']=17;return d

class Pure(unittest.TestCase):
 def test_control(self):self.assertEqual(check(fixture())['position_assignments'],[12,16])
 def test_semantic_mutations(self):
  for field,value in [('finished',False),('reached',True),('reachable',True)]:
   d=fixture();row=d['snapshots'][-1];row[field]=value
   with self.assertRaises(ValueError):check(d)
  d=fixture();d['events'][-2]['value']=[22,0,2]
  with self.assertRaises(ValueError):check(d)
 def test_identity_geometry_and_phase(self):
  mutations=[lambda d:d['ready'].update(readiness_callbacks=241),lambda d:d['ready'].update(registered=[201,201]),lambda d:d['identities'][1].update(agent_id=True),lambda d:d['initial_identities'][0]['settings'].update(avoidance_enabled=True),lambda d:d['events'][0].update(phase='movement'),lambda d:d['events'][2].update(position=[2.5,0,2])]
  for mutate in mutations:
   d=fixture();mutate(d)
   with self.assertRaises(ValueError):check(d)
 def test_raw_json(self):
  for raw in ['{"x":1,"x":2}','{"x":NaN}','{"x":1e999}']:
   with self.assertRaises(ValueError):load(raw)
 def test_startup_freshness(self):
  for optimize in [True,False]:
   with tempfile.TemporaryDirectory() as tmp:
    p=Path(tmp);shutil.copy(ROOT/'run.py',p/'run.py');(p/'summary.json').write_text('{"status":"PASS","synthetic":true}')
    result=subprocess.run([sys.executable]+(['-O'] if optimize else [])+[str(p/'run.py')],capture_output=True,timeout=5)
    self.assertNotEqual(result.returncode,0);self.assertFalse((p/'summary.json').exists());self.assertFalse((p/'evidence').exists())
    self.assertIn(b'optimized runner rejected' if optimize else b'No module named',result.stderr)
if __name__=='__main__':unittest.main()
