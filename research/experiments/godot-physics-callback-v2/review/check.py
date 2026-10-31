import pathlib,json,hashlib,re
root=pathlib.Path(__file__).resolve().parent;out=pathlib.Path(json.loads((root/'run.stdout').read_text())['output'])
def req(x,m):
 if not x:raise RuntimeError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
r=json.loads((out/'receipt.json').read_text());req(r['status']=='PASS' and r['invocation']==out.name,'terminal');req([x['name'] for x in r['commands']]==['version','direct-shape','deferred-shape'],'calls')
for c in r['commands']:req(c['returncode']==0 and c['timed_out'] is False,'exit')
for f,h in r['source_sha256'].items():req(sha(root/'fixture'/f)==h,'source')
for f,h in r['output_sha256'].items():req(sha(out/f)==h,'output')
req(sha(pathlib.Path(r['commands'][0]['argv'][0]))==r['binary_sha256']=='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3','binary')
for mode in ['direct-shape','deferred-shape']:
 stdout=(out/(mode+'.stdout')).read_text();req('ERROR:' not in stdout,'stdout error');lines=[x[12:] for x in stdout.splitlines() if x.startswith('RESULT_JSON=')];req(len(lines)==1,'result');d=json.loads(lines[0]);req(d==json.loads((out/(mode+'.json')).read_text()),'association')
 err=(out/(mode+'.stderr')).read_text();primary="ERROR: Can't change this state while flushing queries. Use call_deferred() or set_deferred() to change monitoring state instead."
 if mode=='direct-shape':
  el=err.splitlines();req(len(el)==4 and el[0]==primary,'exact error envelope');req(re.fullmatch(r'   at: area_set_shape_disabled \(modules/godot_physics_2d/godot_physics_server_2d.cpp:\d+\)',el[1]),'error origin');req(el[2]=='   GDScript backtrace (most recent call first):' and re.fullmatch(r'       \[0\] entered \(res://main.gd:\d+\)',el[3]),'error caller')
 else:req(err=='','deferred stderr')
 bid=d['body_id'];req(type(bid)is int and bid!=0,'body ID');ev=d['events'];ks=[x['kind'] for x in ev];callbacks=[x for x in ev if x['kind'] in ['enter','exit']];req([x['kind'] for x in callbacks]==(['enter','exit','enter'] if mode=='direct-shape' else ['enter','exit']),'physical trace')
 req(all(x['event_body_id']==bid for x in callbacks),'actual identity');req(all(x['body_id']==bid for x in ev),'intended identity');req(d['entries']==sum(x['kind']=='enter' for x in callbacks) and d['exits']==1,'counts')
 req(d['settings']=={'requested_body_class':'CharacterBody2D','actual_body_class':'CharacterBody2D','body_mode':1,'backend':'GodotPhysics2D','separate_thread':False,'ticks_per_second':60,'sensor_radius':10,'body_radius':5,'sensor_position':[0,0],'sensor_layer':1,'sensor_mask':1,'body_layer':1,'body_mask':1,'monitoring':True},'settings')
 req(d['immediate_disabled'] is (mode=='direct-shape') and d['marker_disabled'] is True and d['callback_active'] is False,'properties');req(d['overlap_ids']==([bid] if mode=='direct-shape' else []),'final physical list')
 seq=['initial_outside','initial_move_inside','enter','setter_return','callback_return','marker','move_outside','move_inside','final'];req([ks.index(x) for x in seq]==sorted(ks.index(x) for x in seq),'ordering');req(ks.count('marker')==ks.count('setter_return')==1,'single mutation')
 for k,start,end in [('initial_prephysics_boundary','initial_outside','initial_move_inside'),('outside_prephysics_boundary','move_outside','move_inside'),('inside_prephysics_boundary','move_inside','final')]:
  inds=[i for i,x in enumerate(ev) if x['kind']==k];req(len(inds)==4 and all(ks.index(start)<i<ks.index(end) for i in inds),'bounded phases');fs=[ev[i]['physics_frame'] for i in inds];req(fs==list(range(fs[0],fs[0]+4)),'four distinct boundaries')
 req(all(ev[i]['physics_frame']<=ev[i+1]['physics_frame'] for i in range(len(ev)-1)),'nondecreasing frames')
 for x in ev:
  if x['kind'] in ['initial_outside','move_outside','outside_prephysics_boundary']:req(x['body_position']==[100,0],'outside')
  if x['kind'] in ['initial_move_inside','enter','move_inside','inside_prephysics_boundary','final']:req(x['body_position']==[0,0],'inside')
 req(ev[ks.index('setter_return')]['disabled'] is (mode=='direct-shape'),'setter readback');req(all(x['disabled'] is True for x in ev[ks.index('marker'):]),'no toggle repair')
print(json.dumps({'status':'PASS','invocation':out.name,'behavior_processes':2,'version_commands':1,'source_sha256':r['source_sha256']},indent=2))
