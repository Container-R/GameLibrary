"""Synthetic trace mutations only; no engine/version process."""
import copy,json,unittest
from oracle import check,load
from consumer import parse_stdout

def synthetic():
    ids={'fixture':11,'background':12,'modal':13,'opener':-14,'default':15};vp=16
    names={'fixture':'Fixture','background':'Background','modal':'LogicalModal','opener':'Opener','default':'Default'}
    parent={'fixture':vp,'background':11,'modal':11,'opener':12,'default':13}
    rows=[];bg=2;child=0;eff=2;owner=0;phase='setup'
    def row(kind,target=0):
        nodes={}
        for k in ids:
            nodes[k]={'id':ids[k],'name':names[k],'parent_id':parent[k],'viewport_id':vp,'inside_tree':True,'visible_in_tree':True,
              'local_mode':2 if k in ('opener','default') else 0,'effective_mode':eff if k=='opener' else (2 if k=='default' else 0),
              'behavior':bg if k=='background' else child if k=='opener' else 2 if k=='modal' else 0,
              'in_modal':k=='default','position':[200,0] if k=='default' else [0,0],'size':[160,40] if k in ('opener','default') else [0,0]}
        rows.append({'sequence':len(rows)+1,'phase':phase,'kind':kind,'target_id':target,'owner_id':owner,'nodes':nodes})
    def marker(name):
        nonlocal phase
        phase=name;row(name)
    marker('initial');marker('before_baseline_grab');owner=-14
    row('gui_focus_changed',-14);row('focus_entered',-14);marker('baseline_after_grab')
    marker('before_parent_disable');bg=1;owner=0
    row('focus_exited',-14) # Old effective mode deliberately allowed in callback.
    eff=0;marker('after_parent_disable');marker('before_modal_grab');owner=15
    row('gui_focus_changed',15);row('focus_entered',15);marker('modal_after_grab')
    marker('before_child_enable');child=2;eff=2;marker('after_child_enable');marker('before_naive_grab')
    owner=0;row('focus_exited',15);owner=-14;row('gui_focus_changed',-14);row('focus_entered',-14)
    marker('naive_after_grab');marker('deferred_final')
    return {'version':{'string':'synthetic, not an engine run'},'display_server':'headless','viewport_id':vp,'root_parent_id':vp,'trace':rows}
class Pure(unittest.TestCase):
    def test_literal_control(self): self.assertEqual(check(synthetic())['signals'],8)
    def test_callback_mode_not_postsetter(self):
        for mode in (0,2):
            obj=synthetic()
            next(r for r in obj['trace'] if r['kind']=='focus_exited')['nodes']['opener']['effective_mode']=mode
            self.assertEqual(check(obj)['status'],'PASS')
    def test_finite_mutations(self):
        def target(o,kind): return next(r for r in o['trace'] if r['kind']==kind)
        mutations=[lambda o:target(o,'after_parent_disable')['nodes']['opener'].__setitem__('effective_mode',2),
          lambda o:target(o,'after_child_enable').__setitem__('owner_id',-14),
          lambda o:target(o,'deferred_final').__setitem__('owner_id',15),
          lambda o:target(o,'naive_after_grab')['nodes']['opener'].__setitem__('in_modal',True),
          lambda o:target(o,'initial')['nodes']['opener'].__setitem__('id',True),
          lambda o:target(o,'focus_exited').__setitem__('phase','after_parent_disable'),
          lambda o:target(o,'initial')['nodes']['default'].__setitem__('parent_id',12),
          lambda o:o['trace'].pop(),
          lambda o:target(o,'initial')['nodes']['opener'].__setitem__('size',[True,40])]
        for i,mutate in enumerate(mutations):
            obj=synthetic();mutate(obj)
            with self.subTest(i=i),self.assertRaises(ValueError):check(obj)
    def test_stream_and_duplicate_guards(self):
        banner='Godot Engine v4.6.3.stable.official.7d41c59c4 - https://godotengine.org\n'
        raw=(banner+'RESULT_JSON='+json.dumps(synthetic())+'\n').encode()
        self.assertEqual(parse_stdout(raw)['display_server'],'headless')
        for bad in (raw+b'ERROR: injected\n',raw+raw,raw.replace(b'RESULT_JSON=',b'OTHER=')):
            with self.assertRaises(ValueError):parse_stdout(bad)
        with self.assertRaises(ValueError):load('{"x":1,"x":2}')
if __name__=='__main__':unittest.main(verbosity=2)
