"""Compare archived author/repeat output to pre-author independent ODE data."""
import json
import math
from pathlib import Path
from fractions import Fraction
import sys

def require(condition, message):
    if not condition: raise ValueError(message)

def pair(value):
    require(type(value) is list and len(value) == 2, 'pair shape')
    require(all(type(x) in (int,float) and math.isfinite(x) for x in value), 'pair scalar')
    return value

def error(a,b):
    return [abs(x-y) for x,y in zip(pair(a),pair(b))]

def main():
    here=Path(__file__).resolve().parent
    independent=json.loads((here/'reference-output.json').read_text())
    report=[]
    for path in map(Path,sys.argv[1:]):
        data=json.loads(path.read_text())
        require(data['outcome']=={'tests_run':8,'failures':0,'errors':0,'successful':True}, 'outcome')
        seen=set(); maxima={}
        for row in data['rk4_rows']:
            key=(row['case'],str(Fraction(row['time'])))
            require(key not in seen,'duplicate row'); seen.add(key)
            for label,step in [('coarse','128'),('fine','256')]:
                expected=independent['steps'][step][key[0]][key[1]]
                # Independent implementations have equivalent RK stages but different grouping.
                require(max(error(row[label],expected)) <= 1e-11, 'reference value mismatch')
                errors=error(row['closed'],expected)
                if label=='fine': require(max(errors)<=1e-7,'closed vs independent fine')
                require(max(error(row[label+'_abs_error'],error(row['closed'],row[label])))<=1e-15,'reported error')
                maxima.setdefault(key[0],{}).setdefault(label,[]).extend(errors)
        require(len(seen)==35,'35 distinct case/time rows')
        for name, errors in maxima.items():
            ec,ef=max(errors['coarse']),max(errors['fine'])
            require(ef <= (ec/8 if ec>=1e-10 else 1e-10),'refinement')
        transition=independent['transition_steps']['256']
        require(len(data['events'])==2,'event count')
        for actual, expected in zip(data['events'],transition['transitions']):
            require(actual['time']==float(Fraction(expected['time'])),'transition time')
            for a,b in [('before','before'),('after','after'),('residual_before','old_residual'),('residual_after','new_residual')]:
                require(max(error(actual[a],expected[b]))<=1e-7,'transition against independent integration')
        final_errors=error(data['direct_final'],transition['final_output'])
        require(max(final_errors)<=1e-7,'final against independent integration')
        report.append({'path':str(path),'status':'PASS','rk4_rows':len(seen),
                       'final_vs_independent_fine_errors':final_errors,
                       'scope':'finite arithmetic comparison; no execution-authenticity claim'})
    print(json.dumps(report,indent=2,allow_nan=False))

if __name__=='__main__': main()
