"""Additional pure finite mutations; no subprocess or network entry points."""
import sys,copy,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parent/'final-code'))
from oracle import payload,expected_server,expected_client,check_payloads
s=payload('server',17,expected_server(17));c=payload('client',17,expected_client(17))
# Independent table values, not computed from expected-state constants.
def row(x,kind,n=0):return [r for r in x['trace'] if r['kind']==kind][n]
for i,(a,b,g) in enumerate(((1,0,1),(1,1,1),(10001,1,1))):
 d=row(s,'DECISION',i)
 if d['naive']!={'A':a,'B':b} or d['guarded']!={'A':g,'B':0}:raise ValueError('literal policy table')
mutations={
 'lost_capture':lambda a,b:row(a,'ENQUEUED',1).__setitem__('captured_sender',0),
 'forged_owner':lambda a,b:row(a,'DEFERRED',1)['owners'].__setitem__('B',17),
 'context_substitution':lambda a,b:row(a,'DEFERRED',2).__setitem__('fresh_sender',17),
 'wrong_prior_state':lambda a,b:row(a,'DECISION',1)['before_guarded'].__setitem__('A',2),
 'foreign_actor_applied':lambda a,b:row(a,'DECISION',1)['guarded'].__setitem__('B',1),
 'false_terminal_sender':lambda a,b:row(a,'SERVER_FINISH_CONFIRMED').__setitem__('sender',1),
 'client_crossbound_id':lambda a,b:b.__setitem__('client_id',18),
 'client_outcome_forged':lambda a,b:row(b,'OUTCOME',2)['naive'].__setitem__('A',999),
 'bool_axis':lambda a,b:row(a,'ENQUEUED').__setitem__('axis',True),
 'bool_version':lambda a,b:b['version'].__setitem__('major',True),
}
print('synthetic literal control',check_payloads(s,c))
for name,mutate in mutations.items():
 a,b=copy.deepcopy(s),copy.deepcopy(c);mutate(a,b)
 try:check_payloads(a,b)
 except ValueError:print(name,'REJECTED')
 else:raise RuntimeError('false accept '+name)
