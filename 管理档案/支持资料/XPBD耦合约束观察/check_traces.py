#!/usr/bin/env python3
"""Check stored synthetic traces only. Never compiles or executes a native solver.

The state, continuity and analytical-oracle checks retain the original validation
logic. This public derivative excludes build commands and host identity metadata.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path

ABS_TOL = 2e-6
MAX_TRACE_BYTES = 128 * 1024

def require(ok, reason):
    if not ok:
        raise RuntimeError(reason)


def near(value, expected, label):
    require(isinstance(value, (int,float)) and not isinstance(value,bool) and math.isfinite(value), label + ': nonfinite/non-number')
    require(abs(value-expected) <= ABS_TOL, label + ': analytical mismatch')


def state(points, lambdas):
    require(isinstance(points,list) and len(points)==3, 'wrong point count')
    require(isinstance(lambdas,list) and len(lambdas)==2, 'wrong lambda count')
    for p in points:
        require(isinstance(p,list) and len(p)==3, 'wrong point shape')
        for x in p:
            require(type(x) in (int,float) and math.isfinite(x), 'nonfinite point')
        require(p[1]==0 and p[2]==0, 'collinearity changed')
    require(points[0]==[0,0,0], 'anchor moved')
    require(points[1][0]-points[0][0]>1e-6 and points[2][0]-points[1][0]>1e-6, 'degenerate distance')
    for x in lambdas:
        require(type(x) in (int,float) and math.isfinite(x), 'nonfinite multiplier')


def validate_trace(trace):
    require(trace.stat().st_size <= MAX_TRACE_BYTES, 'trace exceeds fixed bound')
    rows = [json.loads(s) for s in trace.read_text(encoding='utf-8').splitlines()]
    require(len(rows)==21, 'trace incomplete or contains extra records')
    h = rows[0]
    require(h['record']=='header' and h['real_bytes']==4 and h['real_digits']==24, 'wrong scalar profile')
    require(h['eigen']==[3,4,0], 'wrong Eigen version')
    near(h['stiffness'],100,'stiffness'); near(h['dt'],0.1,'dt'); near(h['rest_length'],1,'rest')
    near(h['scaled_native'],1,'native scaled compliance')
    scaled_diagnostic = 1/(h['stiffness']*h['dt']*h['dt'])
    points,lambdas = h['initial_positions'],h['initial_lambdas']
    state(points,lambdas)
    near(points[1][0],6/5,'initial x1'); near(points[2][0],13/5,'initial x2')
    require(lambdas==[0,0], 'multipliers not initialized once at zero')
    index,calls = 1,0
    observations = []
    call_diagnostics = []
    for sweep in range(1,9):
        for constraint in range(2):
            r = rows[index]; index += 1; calls += 1
            require(r['record']=='call' and r['call']==calls and r['sweep']==sweep and r['constraint']==constraint, 'wrong call sequence')
            require(r['native_return'] is True, 'native return not true')
            require(r['positions_before']==points and r['lambdas_before']==lambdas, 'trajectory or accumulated lambda discontinuity')
            state(r['positions_after'],r['lambdas_after'])
            a,b = constraint,constraint+1
            near(r['distance_before'],points[b][0]-points[a][0], 'distance diagnostic')
            near(r['denominator'],(1 if a==0 else 2)+h['scaled_native'], 'denominator diagnostic')
            require(r['distance_before']>1e-6 and r['denominator']>1e-6,'degenerate early-exit condition')
            corrections = r['corrections']
            require(isinstance(corrections,list) and len(corrections)==2, 'wrong correction count')
            for c in corrections:
                require(isinstance(c,list) and len(c)==3, 'wrong correction shape')
                require(all(type(x) in (int,float) and math.isfinite(x) for x in c), 'nonfinite correction')
                require(c[1]==0 and c[2]==0, 'transverse correction')
            for particle in range(3):
                correction = corrections[0] if particle==a else corrections[1] if particle==b else [0,0,0]
                for axis in range(3):
                    near(r['positions_after'][particle][axis], points[particle][axis]+correction[axis], 'immediate correction application')
            require(r['lambdas_after'][1-constraint]==lambdas[1-constraint], 'untouched multiplier changed')
            points,lambdas = r['positions_after'],r['lambdas_after']
            extension = [points[1][0]-1,points[2][0]-points[1][0]-1]
            residual = [extension[i]+scaled_diagnostic*lambdas[i] for i in range(2)]
            require(all(math.isfinite(v) for v in extension+residual), 'nonfinite diagnostic')
            call_diagnostics.append({'call':calls,'sweep':sweep,'constraint':constraint,
                                     'raw_extensions':extension,'compliant_residuals':residual,
                                     'distance_to_minimizer_linf':max(abs(points[1][0]-6/5),abs(points[2][0]-12/5))})
        if sweep in (1,2,8):
            r = rows[index]; index += 1
            require(r['record']=='checkpoint' and r['sweep']==sweep and r['positions']==points and r['lambdas']==lambdas,'checkpoint mismatch')
            q = 1/(6**sweep)
            expected = [6/5+2*q/5, 12/5+q/5, -1/5+3*q/5, -1/5+q/5]
            actual = [points[1][0],points[2][0],lambdas[0],lambdas[1]]
            for v,e,label in zip(actual,expected,('x1','x2','lambda01','lambda12')):
                near(v,e,'sweep '+str(sweep)+' '+label)
            extension = [points[1][0]-1,points[2][0]-points[1][0]-1]
            residual = [extension[i]+scaled_diagnostic*lambdas[i] for i in range(2)]
            near(residual[0],q,'compliant residual01'); near(residual[1],0,'compliant residual12')
            observations.append({'sweep':sweep,'q_exact_fraction':'1/'+str(6**sweep),
                                 'observed':actual,'analytical_expected':expected,
                                 'raw_extensions':extension,'compliant_residuals':residual,
                                 'distance_to_minimizer_linf':max(abs(actual[0]-6/5),abs(actual[1]-12/5)),
                                 'max_abs_state_error':max(abs(v-e) for v,e in zip(actual,expected))})
    require(index==20 and rows[index]=={'record':'trace_complete','native_calls':16,'sweeps':8}, 'missing or wrong completion record')
    require(calls==16,'wrong call count')
    return {'status':'PASS','scope':'one coupled native-kernel trajectory; analytical oracle, not whole-engine execution',
            'absolute_tolerance':ABS_TOL,'scaled_compliance_diagnostic':scaled_diagnostic,
            'call_diagnostics':call_diagnostics,'observations':observations}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('traces', nargs=2, type=Path, help='Two previously saved JSONL traces')
    args=parser.parse_args()
    reports=[validate_trace(path) for path in args.traces]
    hashes=[hashlib.sha256(path.read_bytes()).hexdigest() for path in args.traces]
    require(hashes[0]==hashes[1], 'Stored repeat traces differ')
    print(json.dumps({'status':'STORED_TRACE_CHECK_PASS',
                      'action':'Rechecked existing traces; no native solver was executed',
                      'same_operator_repeats':2,'native_calls_per_stored_trace':16,
                      'trace_sha256':hashes,'reports':reports},indent=2,allow_nan=False))

if __name__=='__main__':
    main()
