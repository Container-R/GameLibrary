"""Literal expected policy transitions, no engine imports."""
import json, math

def need(ok, message):
    if not ok: raise ValueError(message)

def load(raw):
    def unique(pairs):
        out={}
        for k,v in pairs:
            need(k not in out,'duplicate key');out[k]=v
        return out
    def forbidden(value): raise ValueError('nonfinite JSON constant')
    def finite(value):
        number=float(value);need(math.isfinite(number),'nonfinite JSON number');return number
    return json.loads(raw,object_pairs_hook=unique,parse_constant=forbidden,parse_float=finite)

def integer(v): need(type(v) is int,'expected exact int');return v

def check(obj):
    need(type(obj) is dict and obj['display_server']=='headless','headless result')
    expected_version={'build':'official','hash':'7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3','hex':263683,'major':4,'minor':6,'patch':3,'status':'stable','string':'4.6.3-stable (official)','timestamp':0}
    version=obj['version'];need(type(version) is dict and set(version)==set(expected_version),'version schema')
    for key,value in expected_version.items(): need(type(version[key]) is type(value) and version[key]==value,'recorded version field '+key)
    vp=integer(obj['viewport_id']);need(vp!=0 and integer(obj['root_parent_id'])==vp,'viewport ID')
    trace=obj['trace'];need(type(trace) is list and len(trace)==20,'exact trace count')
    names={'fixture':'Fixture','background':'Background','modal':'LogicalModal','opener':'Opener','default':'Default'}
    ids={k:integer(v['id']) for k,v in trace[0]['nodes'].items()}
    need(set(ids)==set(names) and all(ids.values()) and len(set(ids.values())|{vp})==6,'distinct IDs')
    parents={'fixture':vp,'background':ids['fixture'],'modal':ids['fixture'],'opener':ids['background'],'default':ids['modal']}
    markers=['initial','before_baseline_grab','baseline_after_grab','before_parent_disable','after_parent_disable',
             'before_modal_grab','modal_after_grab','before_child_enable','after_child_enable','before_naive_grab','naive_after_grab','deferred_final']
    observed=[]; signals=[]; bymarker={}
    for index,row in enumerate(trace,1):
        need(integer(row['sequence'])==index,'sequence')
        owner=integer(row['owner_id']);need(owner in (0,ids['opener'],ids['default']),'actual owner identity')
        target=integer(row['target_id']);kind=row['kind']
        need(set(row['nodes'])==set(names),'node set')
        for key,n in row['nodes'].items():
            need(integer(n['id'])==ids[key] and n['name']==names[key] and integer(n['parent_id'])==parents[key] and integer(n['viewport_id'])==vp,'actual tree identity')
            for b in ('inside_tree','visible_in_tree','in_modal'): need(type(n[b]) is bool,'boolean field')
            need(n['inside_tree'] and n['visible_in_tree'] and n['in_modal']==(key=='default'),'live visible subtree membership')
            need(integer(n['local_mode'])==(2 if key in ('opener','default') else 0),'unchanged local mode')
            need(integer(n['effective_mode']) in (0,1,2,3) and integer(n['behavior']) in (0,1,2),'enum domains')
            for vector in ('position','size'):
                need(type(n[vector]) is list and len(n[vector])==2 and all(type(x) in (int,float) and math.isfinite(x) for x in n[vector]),'finite vector')
            if key=='opener':need(n['position']==[0,0] and n['size']==[160,40],'opener geometry')
            if key=='default':need(n['position']==[200,0] and n['size']==[160,40],'default geometry')
        if kind in markers:
            need(row['phase']==kind and target==0,'marker phase')
            observed.append(kind);bymarker[kind]=row
        else:
            need(kind in ('focus_entered','focus_exited','gui_focus_changed') and target in (ids['opener'],ids['default']),'signal type/argument')
            need(owner==(0 if kind=='focus_exited' else target),'actual callback owner')
            need(observed and row['phase']==observed[-1],'signal inside actual call markers')
            signals.append((kind,target,row['phase']))
    need(observed==markers,'markers order')
    expected_signals=[('gui_focus_changed',ids['opener'],'before_baseline_grab'),('focus_entered',ids['opener'],'before_baseline_grab'),
        ('focus_exited',ids['opener'],'before_parent_disable'),('gui_focus_changed',ids['default'],'before_modal_grab'),('focus_entered',ids['default'],'before_modal_grab'),
        ('focus_exited',ids['default'],'before_naive_grab'),('gui_focus_changed',ids['opener'],'before_naive_grab'),('focus_entered',ids['opener'],'before_naive_grab')]
    # No cross-signal ordering requirement beyond phase/membership.
    need(sorted(signals)==sorted(expected_signals),'exact passive signal phase/membership')
    gains=[target for kind,target,phase in signals if kind=='gui_focus_changed']
    need(gains==[ids['opener'],ids['default'],ids['opener']],'gain order')
    states=[(0,2,0,2),(0,2,0,2),(ids['opener'],2,0,2),(ids['opener'],2,0,2),
        (0,1,0,0),(0,1,0,0),(ids['default'],1,0,0),(ids['default'],1,0,0),
        (ids['default'],1,2,2),(ids['default'],1,2,2),(ids['opener'],1,2,2),(ids['opener'],1,2,2)]
    for name,(owner,bg,child,effective) in zip(markers,states):
        row=bymarker[name];n=row['nodes']
        need(row['owner_id']==owner and n['background']['behavior']==bg and n['opener']['behavior']==child and n['opener']['effective_mode']==effective,'post-call literal state '+name)
        need(n['fixture']['behavior']==0 and n['modal']['behavior']==2 and n['default']['behavior']==0 and n['default']['effective_mode']==2,'other configuration')
    # Callback eligibility is recorded, deliberately not asserted as post-setter state.
    return {'status':'PASS','markers':12,'signals':8,'behavior_sequences':1}
