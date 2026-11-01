"""Prospective protocol tests. Explicit unittest checks also operate under -O."""
import argparse
from fractions import Fraction as Q
import hashlib
import json
import math
from pathlib import Path
import platform
import sys
import unittest
from scalar import decay, rebase, compose

CASES = {'Z': (0, 0, 2), 'P': (1, 0, 2), 'V': (0, 1, 2),
         'G': (1, 2, 2), 'X': (1, -4, 2),
         'N': (-0.75, 1.25, 0.5), 'F': (0.25, -0.5, 8)}
TIMES = [Q(0), Q(1, 8), Q(1, 2), Q(1), Q(2)]
REPORT = {}


def derivative(state, rate):
    # Independent ODE reference: deliberately no decay/exp calls.
    r, u = state
    return u, -2 * rate * u - rate * rate * r


def rk4(initial, rate, step):
    state = initial
    results = {Q(0): state}
    n = int(Q(2) / step)
    h = float(step)
    for i in range(1, n + 1):
        k1 = derivative(state, rate)
        k2 = derivative(tuple(a + h*b/2 for a, b in zip(state, k1)), rate)
        k3 = derivative(tuple(a + h*b/2 for a, b in zip(state, k2)), rate)
        k4 = derivative(tuple(a + h*b for a, b in zip(state, k3)), rate)
        state = tuple(a + h*(b+2*c+2*d+e)/6
                      for a, b, c, d, e in zip(state, k1, k2, k3, k4))
        t = i * step
        if t in TIMES:
            results[t] = state
    return results


def target(segment, t):
    t = float(t)
    if segment == 0:
        return 0.4*t, 0.4, 0.0
    if segment == 1:
        return 1 + 0.5*math.sin(2*t), math.cos(2*t), -2*math.sin(2*t)
    return -0.25 + 0.2*t, 0.2, 0.0


def schedules():
    values = {str(fps): [Q(1, fps)]*(2*fps) for fps in (30, 60, 144)}
    values['irregular'] = [Q(1,128), Q(3,128), Q(4,128)]*32
    return values


def direct_events():
    residual = (0.0, 0.0)
    age_start = Q(0)
    events = []
    for segment, t in enumerate((Q(3,4), Q(9,8))):
        residual = decay(*residual, 2, float(t-age_start))
        old = target(segment, t)
        before = compose(*old[:2], *residual)
        new = target(segment+1, t)
        new_residual = rebase(*before, *new[:2])
        after = compose(*new[:2], *new_residual)
        accel_before = old[2] - 4*residual[1] - 4*residual[0]
        accel_after = new[2] - 4*new_residual[1] - 4*new_residual[0]
        events.append({'time': float(t), 'before': before, 'after': after,
                       'old_raw': old[:2], 'new_raw': new[:2],
                       'residual_before': residual, 'residual_after': new_residual,
                       'acceleration_before': accel_before,
                       'acceleration_after': accel_after})
        residual, age_start = new_residual, t
    final = compose(*target(2, 2)[:2], *decay(*residual, 2, float(Q(2)-age_start)))
    return events, final


class ScalarTests(unittest.TestCase):
    def finite(self, *values):
        for v in values:
            self.assertTrue(math.isfinite(v), repr(v))

    def close(self, actual, expected):
        self.finite(actual, expected)
        self.assertLessEqual(abs(actual-expected), 1e-11 + 1e-11*abs(expected))

    def close_pair(self, actual, expected):
        for a, b in zip(actual, expected):
            self.close(a, b)

    def test_initial_identity_and_zero_residual_target(self):
        for state in CASES.values():
            self.assertEqual(decay(*state, 0), state[:2])
        for t in TIMES:
            values = (math.sin(float(t)), math.cos(float(t)))
            self.assertEqual(compose(*values, 0, 0), values)
        REPORT['identity_and_clean_target'] = {'cases': list(CASES), 'times': list(map(float, TIMES))}

    def test_independent_rk4(self):
        rows, summary = [], []
        REPORT['rk4_rows'], REPORT['rk4_summary'] = rows, summary
        for name, (r,u,rate) in CASES.items():
            coarse = rk4((r,u), rate, Q(1,128))
            fine = rk4((r,u), rate, Q(1,256))
            ec, ef = [], []
            for t in TIMES:
                exact = decay(r,u,rate,float(t))
                errors_c = tuple(abs(a-b) for a,b in zip(exact, coarse[t]))
                errors_f = tuple(abs(a-b) for a,b in zip(exact, fine[t]))
                self.finite(*exact, *coarse[t], *fine[t], *errors_c, *errors_f)
                rows.append({'case':name,'time':float(t),'closed':exact,
                             'coarse':coarse[t],'fine':fine[t],
                             'coarse_abs_error':errors_c,'fine_abs_error':errors_f})
                if t:
                    ec.extend(errors_c); ef.extend(errors_f)
                for error in errors_f:
                    self.assertLessEqual(error, 1e-7)
                if name == 'Z':
                    self.assertEqual(exact, (0,0)); self.assertEqual(fine[t], (0,0))
                    self.assertEqual(coarse[t], (0,0))
            worst_c, worst_f = max(ec), max(ef)
            meaningful = worst_c >= 1e-10
            summary.append({'case':name,'max_coarse_error':worst_c,'max_fine_error':worst_f,
                            'ratio_coarse_over_fine':worst_c/worst_f if worst_f else None,
                            'refinement_observed':meaningful})
            self.assertLessEqual(worst_f, worst_c/8 if meaningful else 1e-10)

    def test_transitions_c1_and_c2_counterexample(self):
        events, final = direct_events()
        REPORT['events'], REPORT['direct_final'] = events, final
        for event in events:
            self.close_pair(event['after'], event['before'])
            self.finite(event['acceleration_before'],event['acceleration_after'])
        jump = abs(events[0]['acceleration_after']-events[0]['acceleration_before'])
        self.assertGreater(jump, 0.01)

    def test_negative_controls(self):
        events, _ = direct_events()
        e = events[0]
        position_only = compose(*e['new_raw'], e['residual_after'][0], 0)
        self.close(position_only[0],e['before'][0])
        velocity_jump = abs(position_only[1]-e['before'][1])
        self.assertGreater(velocity_jump,0.01)
        e = events[1]
        raw_reset = rebase(*e['old_raw'],*e['new_raw'])
        naive = compose(*e['new_raw'],*raw_reset)
        jumps = tuple(abs(a-b) for a,b in zip(naive,e['before']))
        for jump in jumps:
            self.finite(jump); self.assertGreater(jump,0.01)
        growth = decay(1,2,2,0.125)
        crossing = decay(1,-4,2,0.5)
        beyond = decay(1,-4,2,1)
        self.assertGreater(growth[0],1)
        self.assertLessEqual(abs(crossing[0]),1e-11)
        self.assertLess(beyond[0],0)
        self.assertNotEqual(crossing[1],0)
        h = 0.5
        half = decay(1,0,2*math.log(2)/h,h)
        self.close(half[0],(1+2*math.log(2))/4)
        self.assertGreater(abs(half[0]-0.5),0.05)
        REPORT['expected_counterexamples'] = {'position_only_velocity_jump':velocity_jump,
            'raw_only_value_velocity_jumps':jumps,'initial_growth':growth,
            'position_crossing_not_settled':crossing,'after_crossing':beyond,
            'half_parameter_result':half,'half_parameter_distance_from_half':abs(half[0]-0.5)}

    def test_residual_partitions(self):
        rows=[]; REPORT['partition_rows']=rows
        for name,(r,u,rate) in CASES.items():
            expected=decay(r,u,rate,2)
            for label, steps in schedules().items():
                state=(r,u)
                self.assertEqual(sum(steps),Q(2))
                for step in steps:
                    state=decay(*state,rate,float(step))
                self.close_pair(state,expected)
                rows.append({'case':name,'schedule':label,'result':state,
                    'absolute_error':[abs(a-b) for a,b in zip(state,expected)],
                    'float_interval_sum':sum(map(float,steps))})

    def test_event_split_partitions(self):
        _,expected=direct_events()
        rows=[]; REPORT['event_partition_rows']=rows
        boundaries=[Q(3,4),Q(9,8)]
        for label,steps in schedules().items():
            grid={Q(0),*boundaries}; t=Q(0)
            for step in steps:
                t+=step; grid.add(t)
            grid=sorted(grid); state=(0,0); segment=0; applied=[]
            for left,right in zip(grid,grid[1:]):
                state=decay(*state,2,float(right-left))
                output=compose(*target(segment,right)[:2],*state)
                if right in boundaries:
                    segment+=1
                    state=rebase(*output,*target(segment,right)[:2])
                    self.close_pair(compose(*target(segment,right)[:2],*state),output)
                    applied.append(float(right))
            self.assertEqual(applied,[0.75,1.125])
            final=compose(*target(segment,Q(2))[:2],*state)
            self.close_pair(final,expected)
            rows.append({'schedule':label,'events':applied,'result':final,
                         'absolute_error':[abs(a-b) for a,b in zip(final,expected)]})

    def test_long_samples_and_endpoints(self):
        REPORT['long_samples']={name:decay(*state,8) for name,state in CASES.items()}
        for pair in REPORT['long_samples'].values(): self.finite(*pair)
        valid=[(-100,0,2,0),(100,0,2,0),(0,-100,2,0),(0,100,2,0),
               (0,0,0.125,1),(0,0,16,1),(0,0,2,8),(1,1,2,-0.0)]
        for args in valid: self.finite(*decay(*args))
        for function in (rebase,compose):
            for index in range(4):
                for endpoint in (-100,100):
                    args=[0,0,0,0]; args[index]=endpoint
                    self.finite(*function(*args))
        REPORT['accepted_decay_endpoints']=valid

    def test_rejections_and_no_partial_mutation(self):
        invalid=[True,False,'1',None,1j,float('nan'),float('inf'),-float('inf'),10**1000]
        count=0
        for function,base in [(decay,[1,1,2,1]),(rebase,[1,1,0,0]),(compose,[0,0,1,1])]:
            for index in range(4):
                for value in invalid:
                    args=base.copy(); args[index]=value
                    with self.assertRaises(ValueError): function(*args)
                    count+=1
            indices=range(2) if function is decay else range(4)
            for index in indices:
                for value in (-101,101):
                    args=base.copy(); args[index]=value
                    with self.assertRaises(ValueError): function(*args)
                    count+=1
        for rate in (0,-1,0.124,16.001):
            with self.assertRaises(ValueError): decay(0,0,rate,1)
            count+=1
        for dt in (-0.01,8.001):
            with self.assertRaises(ValueError): decay(0,0,2,dt)
            count+=1
        for function,args in [(rebase,[100,0,-100,0]),(rebase,[0,100,0,-100]),
            (compose,[100,0,100,0]),(compose,[0,100,0,100]),(decay,[100,0,16,0.0625])]:
            before=args.copy()
            with self.assertRaises(ValueError): function(*args)
            self.assertEqual(args,before)
            count+=1
        REPORT['rejected_argument_or_output_cases']=count


if __name__ == '__main__':
    parser=argparse.ArgumentParser(); parser.add_argument('--output',required=True)
    args=parser.parse_args()
    here=Path(__file__).resolve().parent
    sources=[here/'scalar.py',here/'test_scalar.py',here.parent/'protocol.md']
    REPORT['metadata']={'python':sys.version,'executable':sys.executable,
        'platform':platform.platform(),'optimize':sys.flags.optimize,
        'argv':sys.argv,'source_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(ScalarTests))
    REPORT['outcome']={'tests_run':result.testsRun,'failures':len(result.failures),
        'errors':len(result.errors),'successful':result.wasSuccessful()}
    Path(args.output).write_text(json.dumps(REPORT,indent=2,allow_nan=False)+'\n')
    sys.exit(0 if result.wasSuccessful() else 1)
