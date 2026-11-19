from fractions import Fraction as F
import json

# Staged, immutable root/hand samples on one horizontal axis, metres.
contact_root, local_hand, end_root = F(2,5), F(1,2), F(1)
hand_anchor, end_target = F(11,10), F(13,10)
# Comparison algorithms are original, not Epic Skew Warp or IK.
end_residual = end_target-end_root
contact_residual = hand_anchor-(contact_root+local_hand)
t = F(1,2)
options = {'unwarped': (F(0),F(0)),
           'end_only': (t*end_residual,end_residual),
           'two_constraints': (contact_residual,end_residual)}
rows={name:{'contact_error_cm':str(100*(contact_root+local_hand+a-hand_anchor)),
            'end_error_cm':str(100*(end_root+b-end_target))}
      for name,(a,b) in options.items()}
assert rows=={'unwarped': {'contact_error_cm':'-20','end_error_cm':'-30'},
              'end_only': {'contact_error_cm':'-5','end_error_cm':'0'},
              'two_constraints': {'contact_error_cm':'0','end_error_cm':'0'}}
print(json.dumps(rows,indent=2))
