"""Model one segment crossing a repeated material's discontinuous phase wrap."""
import json
from fractions import Fraction as Q

period = Q(3,4)
a, b = Q(47,64), Q(49,64)
wrapped_at_vertices = (a%period,b%period)
wrong_mid = sum(wrapped_at_vertices)/2
correct_mid = ((a+b)/2)%period
wrapped_delta = wrapped_at_vertices[1]-wrapped_at_vertices[0]
assert wrong_mid==Q(3,8) and correct_mid==0
assert b-a==Q(1,32) and wrapped_delta==-Q(23,32)
print(json.dumps({"period":str(period),"unwrapped_endpoints":[str(a),str(b)],
 "wrapped_endpoints":[str(x) for x in wrapped_at_vertices], "wrap_then_interpolate":str(wrong_mid),
 "interpolate_then_wrap":str(correct_mid),"unwrapped_endpoint_delta":str(b-a),
 "wrapped_endpoint_delta":str(wrapped_delta)},indent=2))
