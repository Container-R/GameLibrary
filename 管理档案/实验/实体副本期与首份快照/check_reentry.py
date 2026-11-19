import json

# One entity remains born on the server for the entire example. Integers are
# intentionally tiny; messages are defined as local records, not wire packets.
birth_id=('S',7,4)
local={'scope':8,'state':{'lift_height':20,'door':'closed'},'tick':10}
new_full={'scope':9,'state':{'lift_height':72,'door':'open'},'tick':19}
in_flight_old={'scope':8,'base':10,'tick':12,'changes':{'lift_height':30}}
early_new={'scope':9,'base':19,'tick':20,'changes':{'lift_height':75}}

def apply_delta(view,msg,bound=True):
    if view is None or (bound and view['scope']!=msg['scope']):
        return 'no matching view'
    if view['tick']!=msg['base']:
        return 'missing baseline'
    return {'scope':view['scope'],'tick':msg['tick'],'state':view['state']|msg['changes']}

def apply_hide(view, hidden_scope):
    return None if view is not None and view['scope']==hidden_scope else view

rows={'existing_entity_identity':birth_id,
      'apply_new_delta_to_old_cache':apply_delta(local,early_new,False),
      'apply_old_delta_to_old_cache_without_retiring_view':apply_delta(local,in_flight_old,False),
      'apply_old_delta_while_no_view':apply_delta(None,in_flight_old),
      'apply_old_delta_after_full':apply_delta(new_full,in_flight_old),
      'apply_new_delta_after_full':apply_delta(new_full,early_new),
      'apply_late_scope8_hide_after_scope9_full':apply_hide(new_full,8),
      'apply_current_scope9_hide':apply_hide(new_full,9)}
assert rows['apply_new_delta_to_old_cache']=='missing baseline'
assert rows['apply_old_delta_to_old_cache_without_retiring_view']['state']['door']=='closed'
assert rows['apply_old_delta_while_no_view']==rows['apply_old_delta_after_full']=='no matching view'
assert rows['apply_new_delta_after_full']['state']=={'lift_height':75,'door':'open'}
assert rows['apply_late_scope8_hide_after_scope9_full']==new_full
assert rows['apply_current_scope9_hide'] is None
print(json.dumps(rows,indent=2))
