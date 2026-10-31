"""Portable archive-only checks; no engine/runner launch or installed binary read.
Imports the hash-pinned reviewer's pure oracle under a non-main module name.
"""
import sys
sys.dont_write_bytecode = True
import hashlib,importlib.util,json,math
from pathlib import Path,PurePosixPath
R=Path(__file__).resolve().parents[1]
def require(v,msg):
 if not v:raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def pairs(items):
 d={}
 for k,v in items:
  require(k not in d,'duplicate JSON key');d[k]=v
 return d
def bad(v):raise ValueError('nonfinite JSON')
def number(v):
 n=float(v);require(math.isfinite(n),'nonfinite float');return n
def parse(s):return json.loads(s,object_pairs_hook=pairs,parse_constant=bad,parse_float=number)
def read(p):return parse(p.read_text())
PURE='864d3aa06bd2c550042e183f851c5127121762f531b4c2a0d567fadfd9e74f04'
require(sha(R/'review/check.py')==PURE,'pure oracle source changed')
spec=importlib.util.spec_from_file_location('reviewed_static_pose_oracle',R/'review/check.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
PINS={'run.py':'eeacbeff431533918d472ff5804eb0efe222e91503402bb86e56c425f04f8ef1','main.gd':'82fb68849d8b33dc35f20d3e633a7e9b7a5f40593731241f5fcbcc66bc6c77ca','project.godot':'e3704b740fff68371005d081e55401e0c59af26be5e76a7dbf4a3eb5b670c28b','contract.json':'46d4965fb6b945e9acc0f5d41118747525a2545180af9181874933e6eb95ea65','isolation.py':'bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970'}
BINARY='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3'
OLD='898905d9beec2c9e215b7fb6d0e330c3a0a896b2e6b155050fd77206c89ca565'
CASES=[('results/d950544e-f0af-4068-aa0f-780ede638355','historical-false-interpolation-oracle','FAIL'),('results/94105a77-e9f7-4367-ba9e-dfd4802f1224','.','PASS'),('review/evidence/6703fd88-731a-4879-8a5d-6f2ac968b3e2','review/fixture','PASS')]
records=[]
for out,src,status in CASES:
 p=R/out;r=read(p/'receipt.json');pins=dict(PINS)
 if status=='FAIL':pins['run.py']=OLD
 require(r['invocation_id']==p.name and r['status']==status,'receipt identity/status')
 require(r['source_sha256']==pins,'declared source pins')
 require({n:sha(R/src/n) for n in pins}==pins,'actual source pins')
 require(r['binary_sha256']==BINARY and r['version']=='4.6.3.stable.official.7d41c59c4','archived binary metadata')
 require([c['name'] for c in r['commands']]==['version','behavior'],'process list')
 for c in r['commands']:
  require(type(c['returncode'])is int and c['returncode']==0 and c['timed_out'] is False and c['timeout_seconds']==30,'native outcome')
  require(c['argv'][0]=='/opt/godot/4.6.3/Godot_v4.6.3-stable_linux.x86_64','binary argv')
 require(r['commands'][0]['argv'][1:]==['--headless','--version'],'version argv')
 require(r['commands'][1]['argv'][1:3]==['--headless','--path'] and r['commands'][1]['argv'][4:]==['--script','main.gd'],'behavior argv')
 keys={'HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR'};env=r['selected_environment_locations'];require(set(env)==keys,'selected env')
 roots=[]
 for k,v in env.items():
  q=PurePosixPath(v);require(q.is_absolute() and '..' not in q.parts and q.name==k,'location');roots.append(q.parent)
 require(len(set(roots))==1 and str(roots[0])==r['commands'][1]['argv'][3],'environment/work root')
 require(set(r['outputs_sha256'])=={'version.stdout','version.stderr','behavior.stdout','behavior.stderr','behavior.json'},'output inventory')
 for n,h in r['outputs_sha256'].items():require(sha(p/n)==h,'output hash')
 require((p/'version.stdout').read_text()=='4.6.3.stable.official.7d41c59c4\n','version stream')
 require((p/'version.stderr').read_bytes()==(p/'behavior.stderr').read_bytes()==b'','stderr')
 lines=(p/'behavior.stdout').read_text().splitlines();payload=[x[12:] for x in lines if x.startswith('RESULT_JSON=')]
 require(len(payload)==1,'single result')
 require(all(not x or x.startswith('Godot Engine v4.6.3.stable.official.7d41c59c4') or x.startswith('RESULT_JSON=') for x in lines),'stdout envelope')
 require(not any('ERROR' in x or 'WARNING' in x for x in lines),'diagnostic')
 d=parse(payload[0]);require(d==read(p/'behavior.json'),'raw parsed binding');module.oracle(d)
 if status=='FAIL':require(r['error']=="RuntimeError('unexpected interpolation')",'retained failure reason')
 else:require(r['behavior_observations']=={'evaluations':2,'setup_events':5},'accepted observation count')
 values=[m['interpolating'] for e in d['evaluations'] for label in ('before','restored') for m in e[label]['modifiers']]
 records.append({'uuid':r['invocation_id'],'original_full_oracle_status':status,'geometry_archive_consistent':True,'observed_interpolating_values':values,'manual_evaluations':2})
require(read(R/'results/summary.json')==read(R/'results/94105a77-e9f7-4367-ba9e-dfd4802f1224/receipt.json'),'author summary')
require(read(R/'review/evidence/summary.json')==read(R/'review/evidence/6703fd88-731a-4879-8a5d-6f2ac968b3e2/receipt.json'),'review summary')
for name in ('mutations.json','mutations-optimized.json'):
 d=read(R/'review'/name);require(d['status']=='PASS' and d['synthetic_records']==6 and d['native_processes']==d['child_processes']==0,'mutation counts')
 require([c['mutation'] for c in d['checks']]==['change_origin','change_order','change_target','change_identity','change_restore','change_basis'],'mutation set')
 require(all(c['rejected_by']==['author','independent'] for c in d['checks']),'mutation outcomes')
require(not (R/'review/optimized-rejection/summary.json').exists(),'stale summary')
require('optimized Python rejected before native execution' in (R/'review/optimized.stderr').read_text(),'startup negative')
print(json.dumps({'status':'PASS','records':records,'historical_behavior_attempts':3,'historical_full_oracle_accepted':2,'historical_version_queries':3,'unique_order_configurations':2,'static_check_native_processes':0,'static_check_child_processes':0,'current_binary_read':False,'pure_reviewer_oracle_sha256':PURE,'limits':'Historical FAIL is not upgraded; metadata is not binary/source authentication; temporary environment directories are not reread; no execution authenticity guarantee'},indent=2))
