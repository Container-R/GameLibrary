"""Original, engine-free scheduling contract model. Python standard library only.
Uses exact fractions for scheduler tests, not a claim of float/physics determinism.
"""
from fractions import Fraction as F
import unittest

class Runner:
    def __init__(self, inputs=None):
        self.tick = 0
        self.accumulator = F(0)
        self.position = 0
        self.previous = 0
        self.events = []
        self.inputs = inputs or {}

    def frame(self, elapsed, budget=8):
        if isinstance(budget, bool) or not isinstance(budget, int) or budget <= 0:
            raise ValueError('budget must be a positive integer')
        if elapsed < 0:
            raise ValueError('elapsed must be nonnegative')
        self.accumulator += elapsed * 60  # time expressed in simulation ticks
        steps = 0
        while self.accumulator >= 1 and steps < budget:
            self.previous = self.position
            # tick is the next command slot; each slot is consumed exactly once.
            self.position += self.inputs.get(self.tick, 0)
            if self.inputs.get(self.tick, 0):
                self.events.append((self.tick, self.inputs[self.tick]))
            self.tick += 1
            self.accumulator -= 1
            steps += 1
        # Keep backlog; show latest state while behind, never extrapolate accidentally.
        alpha = min(self.accumulator, F(1))
        view = self.previous * (1-alpha) + self.position * alpha
        return steps, alpha, view

class ContractTests(unittest.TestCase):
    def test_render_partitions_replay_same_tick_inputs(self):
        results = []
        for hz in (30, 60, 144):
            r = Runner({0: 1, 10: 3, 59: -2})
            for _ in range(hz): r.frame(F(1, hz))
            results.append((r.tick, r.position, r.events))
        self.assertTrue(all(x == results[0] for x in results))
        self.assertEqual(results[0], (60, 2, [(0,1),(10,3),(59,-2)]))

    def test_short_frame_keeps_fraction(self):
        r = Runner()
        self.assertEqual(r.frame(F(1,120))[0], 0)
        self.assertEqual(r.frame(F(1,120))[0], 1)
        self.assertEqual(r.accumulator, 0)

    def test_stall_budget_preserves_debt(self):
        r = Runner()
        steps, alpha, _ = r.frame(F(1), budget=4)
        self.assertEqual((steps, r.tick, r.accumulator, alpha), (4,4,56,1))
        for _ in range(14): r.frame(F(0), budget=4)
        self.assertEqual((r.tick, r.accumulator), (60,0))

    def test_catchup_consumes_edge_once(self):
        r = Runner({1: 1})
        r.frame(F(3,60))
        self.assertEqual(r.events, [(1,1)])

    def test_render_has_no_authoritative_write(self):
        r = Runner({0:10})
        r.frame(F(1,60))
        before = (r.tick, r.position, list(r.events))
        _, alpha, view = r.frame(F(1,120))
        self.assertEqual(view, 5)
        self.assertEqual(alpha, F(1,2))
        self.assertEqual((r.tick,r.position,r.events), before)

    def test_negative_clock_rejected(self):
        with self.assertRaises(ValueError): Runner().frame(F(-1))

    def test_input_sampling_is_not_render_invariant(self):
        # Same physical arrival time can be observed on different frames.
        # Replay guarantee therefore requires a canonical tick-input stream.
        arrival = F(1,50)  # one physical edge at exactly 20 ms
        def poll_and_assign(hz):
            # Poll after draining completed fixed ticks at each render boundary.
            # Earliest observed frame >= the shared arrival time wins.
            r = Runner()
            for frame in range(1, hz + 1):
                r.frame(F(1,hz))
                observed = F(frame,hz)
                if observed >= arrival:
                    command = {'target_tick':r.tick, 'sequence':0, 'pressed':True}
                    return observed, command
            raise AssertionError('edge never sampled')
        at_30, cmd_30 = poll_and_assign(30)
        at_144, cmd_144 = poll_and_assign(144)
        self.assertEqual((at_30, cmd_30['target_tick']), (F(1,30),2))
        self.assertEqual((at_144, cmd_144['target_tick']), (F(3,144),1))
        self.assertNotEqual(cmd_30['target_tick'],cmd_144['target_tick'])

    def test_invalid_step_budget_rejected(self):
        for budget in (0, -1, F(1,2), True):
            with self.subTest(budget=budget):
                with self.assertRaises(ValueError): Runner().frame(F(1),budget)

if __name__ == '__main__': unittest.main(verbosity=2)
