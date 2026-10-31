"""Portable finite archive QA. No engine, current binary access or author imports."""
import hashlib,json,re,sys
from pathlib import Path
BINARY='f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3'
FILES=['run.py','main.gd','project.godot','contract.json']
V2=dict(zip(FILES,['3db75326470b308647e0b5db8174e8858ffb9fa45c7376c9ea1804fc55d13b7f','51b43cf26885774284459aa67d46d603945e389b2b5352bfd760a2b2c5be4d2e','6a6c99fb0351651f8701f07062a0b16a39daa913d6ec098005e753dcee9e896c','26f80627f6afea5413b664c3a4097118c437655b81fdfaa8ec47866b10aa6dde']))
OLD=[('fb43cbe6-ccbd-4507-9e2f-a3d61e2da016','initial-startup-failure',-6),('a51adba6-2f98-4911-849f-a4a4b3831aac','initial-no-entry',2),('1c95ee67-42da-438e-b857-becfdbc2aa10','diagnostic-no-entry',2)]
V1_RUN=['910304159f5240a9307eb4739735a848430a9e117de8cbaaad1622cc337045da','9358abe0860697c52bed7542ba4823abd99b3de7972e28f98e30c58dfa4d736a','fba888945be0a8d1b2b3639d6a8a986a665020d0ca66ba37fb09205fe054a683']
V1_MAIN=['838254eb3ce38d96af86b958e50a07f5dbad04132df19d57adb3f7cdc8ed61e7']*2+['fc687e9cd75f32b69f26378fd5d031c884234961ae15223a7033779a48c2a4f7']
PRIMARY="ERROR: Can't change this state while flushing queries. Use call_deferred() or set_deferred() to change monitoring state instead."
def need(v,msg):
    if not v: raise ValueError(msg)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def read(p):return json.loads(p.read_text())
def envelope(text,mode):
    if mode=='deferred-shape':need(text=='','deferred stderr');return
    lines=text.splitlines();need(len(lines)==4 and lines[0]==PRIMARY,'single ordered primary envelope')
    for line,pattern in zip(lines[1:],[r'   at: area_set_shape_disabled \(modules/godot_physics_2d/godot_physics_server_2d.cpp:\d+\)',r'   GDScript backtrace \(most recent call first\):',r'       \[0\] entered \(res://main.gd:\d+\)']):need(re.fullmatch(pattern,line),'bounded error context')
def bind(source,out,expected_status,runner_override=None):
    r=read(out/'receipt.json');need(r['invocation']==out.name and r['status']==expected_status,'receipt identity/status')
    need(r['source_sha256']=={f:sha(runner_override if f=='run.py' and runner_override else source/f) for f in FILES},'snapshot source hashes')
    need(r['binary_sha256']==BINARY,'recorded binary identity')
    manifest=r['output_sha256'];actual={p.name:sha(p) for p in out.iterdir() if p.is_file() and p.name!='receipt.json'}
    need(actual==manifest,'complete output hash manifest')
    names=[c['name'] for c in r['commands']]
    need(names==(['version','direct-shape','deferred-shape'] if expected_status=='PASS' else ['version','direct-shape']),'attempted commands')
    for c in r['commands']:
        need(c['timed_out'] is False and c['timeout_seconds']==20,'recorded termination')
        a=c['argv'];need(len(a)==2 and a[1]=='--version' if c['name']=='version' else len(a)==8 and a[1:3]==['--headless','--path'] and a[4:]==['--script','res://main.gd','--',c['name']],'recorded command shape')
        # Historical executable/temp paths remain strings; never dereferenced.
        if expected_status=='PASS' or c['name']=='version':need(c['returncode']==0,'successful command code')
    need((out/'version.stdout').read_text().strip()=='4.6.3.stable.official.7d41c59c4' and (out/'version.stderr').read_bytes()==b'','recorded version')
    return r

def numeric_result(d,mode):
    ident=d['body_id'];need(type(ident) is int and ident!=0,'signed body identity')
    need(type(d['sensor_id']) is int and d['sensor_id']!=0 and d['sensor_id']!=ident,'sensor identity')
    direct=mode=='direct-shape'
    need(d['mode']==mode and d['entries']==(2 if direct else 1) and d['exits']==1,'counts')
    need(d['immediate_disabled'] is direct and d['marker_disabled'] is True and d['callback_active'] is False,'mutation timing')
    need(d['settings']==dict(requested_body_class='CharacterBody2D',actual_body_class='CharacterBody2D',body_mode=1,backend='GodotPhysics2D',separate_thread=False,ticks_per_second=60,sensor_radius=10,body_radius=5,sensor_position=[0,0],sensor_layer=1,sensor_mask=1,body_layer=1,body_mask=1,monitoring=True),'actual geometry/body/backend')
    ev=d['events'];k=[e['kind'] for e in ev]
    expected={'initial_outside':1,'initial_prephysics_boundary':4,'initial_move_inside':1,'enter':2 if direct else 1,'setter_return':1,'callback_return':2 if direct else 1,'marker':1,'move_outside':1,'exit':1,'outside_prephysics_boundary':4,'move_inside':1,'inside_prephysics_boundary':4,'final':1}
    need({x:k.count(x) for x in set(k)}==expected,'exact event-kind counts')
    def at(x):return k.index(x)
    ordered=['initial_outside','initial_move_inside','enter','setter_return','callback_return','marker','move_outside','move_inside','final']
    need([at(x) for x in ordered]==sorted(at(x) for x in ordered),'causal order')
    for phase,start,end in [('initial','initial_outside','initial_move_inside'),('outside','move_outside','move_inside'),('inside','move_inside','final')]:
        seq=[i for i,e in enumerate(ev) if e['kind']==phase+'_prephysics_boundary']
        need(all(at(start)<i<at(end) for i in seq),'bounded phase window')
        frames=[ev[i]['physics_frame'] for i in seq];need(all(b==a+1 for a,b in zip(frames,frames[1:])),'four consecutive pre-boundaries')
    entries=[i for i,x in enumerate(k) if x=='enter']
    need(entries[0]<at('exit')<at('move_inside'),'exit before re-entry opportunity')
    if direct:need(at('move_inside')<entries[1]<at('final'),'second actual entry')
    need(d['overlap_ids']==([ident] if direct else []),'finite final overlap')
    last=(-1,-1)
    for i,e in enumerate(ev):
        need(e['body_id']==ident,'event body identity')
        if e['kind'] in ['enter','exit']:need(e['event_body_id']==ident,'actual callback identity')
        pf,rf=e['physics_frame'],e['process_frame'];need(type(pf) is int and type(rf) is int and pf>=last[0] and rf>=last[1],'frame observation order');last=(pf,rf)
        outside=e['kind'] in ['initial_outside','initial_prephysics_boundary','move_outside','outside_prephysics_boundary','exit']
        need(e['body_position']==([100,0] if outside else [0,0]),'event geometry')
        want=False if i<at('setter_return') else (True if direct or i>=at('marker') else False)
        need(e['disabled'] is want,'observed node property phase')
    need(d['engine']['hash']=='7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3','runtime self-report')

def successful(source,out,current=False,runner_override=None):
    expected=dict(V2)
    if current: expected['run.py']='2b00a96795564d2dc067928ceaa2f3c541ecc699873c80d9f9ae2d54a54f4803'
    need({f:sha(runner_override if f=='run.py' and runner_override else source/f) for f in FILES}==expected,'pinned v2 source')
    r=bind(source,out,'PASS',runner_override)
    need(set(r['output_sha256'])=={'version.stdout','version.stderr'}|{m+'.'+x for m in ['direct-shape','deferred-shape'] for x in ['stdout','stderr','json']},'v2 output set')
    for mode in ['direct-shape','deferred-shape']:
        envelope((out/(mode+'.stderr')).read_text(),mode)
        raw=(out/(mode+'.stdout')).read_text();need('ERROR:' not in raw,'stdout error')
        payload=[s[12:] for s in raw.splitlines() if s.startswith('RESULT_JSON=')];need(len(payload)==1,'single raw result')
        d=json.loads(payload[0]);need(d==read(out/(mode+'.json')),'raw/parsed association');numeric_result(d,mode)
    return {'uuid':out.name,'receipt_sha256':sha(out/'receipt.json'),'attempted_behavior':2,'accepted_behavior':2,'version_commands':1}

def main():
    need(len(sys.argv)==4,'usage: check_archives.py V1_ROOT V2_ROOT REVIEW_ROOT')
    old,new,review=map(Path,sys.argv[1:]);history=[]
    need({p.name for p in (old/'results').iterdir() if p.is_dir()}=={x[0] for x in OLD},'three failed UUIDs')
    for n,(uid,snapshot,code) in enumerate(OLD):
        out=old/'results'/uid;r=bind(old/snapshot,out,'FAIL')
        need(r['source_sha256']==dict(zip(FILES,[V1_RUN[n],V1_MAIN[n],V2['project.godot'],'68b53b919dbbc200f62b2a28932e8047eabcb03434ce64ff41dbb7812233dd6f'])),'pinned v1 snapshot')
        need(r['commands'][1]['returncode']==code,'historical returncode')
        need(set(r['output_sha256'])=={x+'.'+s for x in ['version','direct-shape'] for s in ['stdout','stderr']},'failed output set')
        need('RESULT_JSON=' not in (out/'direct-shape.stdout').read_text(),'no accepted v1 result')
        history.append({'uuid':uid,'snapshot':snapshot,'receipt_sha256':sha(out/'receipt.json'),'returncode':code})
    old_author='39536c18-7525-4dcc-b264-ca94a2097a2d';new_author='b3e7b2d4-351b-4342-8b6b-a084fda177f8';review_id='a253567d-2230-43ca-9e02-8a8eb8415367'
    need({p.name for p in (new/'results').iterdir() if p.is_dir()}=={old_author,new_author},'two author v2 invocations')
    need({p.name for p in (review/'evidence').iterdir() if p.is_dir()}=={review_id},'one reviewer invocation')
    historical=successful(new,new/'results'/old_author,runner_override=new/'historical-runner-before-stdout-guard/run.py')
    author=successful(new,new/'results'/new_author,current=True)
    other=successful(review/'fixture',review/'evidence'/review_id)
    print(json.dumps({'status':'PASS','scope':'static archive association, not execution/authenticity or v1 causal diagnosis','v1':history,'v1_attempted_behavior':3,'v1_accepted_behavior':0,'v1_version_commands':3,'v2_author_historical':historical,'v2_author_current':author,'v2_review':other,'total_version_commands':6,'v2_accepted_behavior_processes':6,'unique_v2_configurations':2},sort_keys=True))
if __name__=='__main__':main()
