import itertools
import unittest
from collections import Counter
from model import Adapter, FakePort, Ticket


class LifecycleTests(unittest.TestCase):
    def make(self):
        p = FakePort()
        return p, Adapter(p)

    def test_start_failed_needs_no_stopped(self):
        p, a = self.make()
        g = a.begin('Explore')
        a.ready(g, 'A')
        self.assertEqual(a.state, 'Starting')
        a.outcome(g, 'A', 'start_failed')
        self.assertEqual(a.state, 'Stopped')
        a.outcome(g, 'A', 'stopped')
        self.assertEqual(p.calls, [('mode', g, 'A', 1, 'Explore'),
                                  ('start', g, 'A'), ('release', g, 'A')])

    def test_cancel_before_ready_and_duplicate_completion(self):
        p, a = self.make()
        g = a.begin('Explore')
        a.exit()
        a.ready(g, 'late')
        a.ready(g, 'late')
        self.assertEqual(p.calls, [('release', g, 'late')])

    def test_old_generation_cannot_touch_new_handle(self):
        p, a = self.make()
        old = a.begin('Explore')
        a.exit()
        new = a.begin('Combat')
        a.ready(new, 'B')
        a.ready(old, 'A')
        a.outcome(old, 'A', 'started')
        a.outcome(old, 'A', 'start_failed')
        self.assertEqual(a.handle, 'B')
        self.assertEqual(a.state, 'Starting')
        self.assertEqual(p.calls, [('mode', new, 'B', 2, 'Combat'),
                                  ('start', new, 'B'), ('release', old, 'A')])

    def test_revision_retry_success_cache_and_invalidation(self):
        p, a = self.make()
        g = a.begin('Explore')
        p.fail_next_mode = True
        a.ready(g, 'A')
        self.assertIsNone(a.submitted)
        old = Ticket(g, a.revision)
        current = a.intent('Combat')
        a.retry(old)
        a.retry(current)
        a.intent('Combat')
        a.invalidate_external_write()
        self.assertEqual(p.calls, [('mode', g, 'A', 1, 'Explore'),
                                  ('mode', g, 'A', 2, 'Combat'),
                                  ('start', g, 'A'),
                                  ('mode', g, 'A', 3, 'Combat')])

    def test_failed_same_value_is_retryable(self):
        p, a = self.make()
        g = a.begin('Explore')
        p.fail_next_mode = True
        a.ready(g, 'A')
        a.retry(Ticket(g, 1))
        a.retry(Ticket(g, 1))
        self.assertEqual(p.calls, [('mode', g, 'A', 1, 'Explore'),
                                  ('mode', g, 'A', 1, 'Explore'),
                                  ('start', g, 'A')])

    def test_exit_active_and_late_callbacks_do_not_duplicate_cleanup(self):
        p, a = self.make()
        g = a.begin('Explore')
        a.ready(g, 'A')
        a.outcome(g, 'A', 'started')
        a.exit()
        a.exit()
        a.outcome(g, 'A', 'stopped')
        self.assertEqual(p.calls[-2:], [('stop', g, 'A'), ('release', g, 'A')])
        self.assertEqual(len(p.calls), 4)

    def test_bounded_interleavings(self):
        # 8^4 = 4096 deterministic sequences, no random seeds.
        actions = ('ready', 'exit', 'new', 'intent', 'retry', 'fail', 'started', 'invalidate')
        for sequence in itertools.product(actions, repeat=4):
            p, a = self.make()
            g = a.begin('Explore')
            ticket = Ticket(g, 1)
            for op in sequence:
                if op == 'ready': a.ready(g, 'A')
                elif op == 'exit': a.exit()
                elif op == 'new' and a.state == 'Stopped':
                    a.begin('Combat')
                    a.ready(a.generation, 'new-' + str(a.generation))
                elif op == 'intent' and a.state in ('Starting', 'Active'):
                    p.fail_next_mode = True
                    a.intent('Tension')
                elif op == 'retry': a.retry(ticket)
                elif op in ('fail', 'started') and a.handle in a.started:
                    a.outcome(a.generation, a.handle,
                              'start_failed' if op == 'fail' else 'started')
                elif op == 'invalidate': a.invalidate_external_write()
                counts = Counter((c[0], c[1], c[2]) for c in p.calls)
                for (kind, owner, handle), count in counts.items():
                    self.assertEqual(a.owned[handle], owner, sequence)
                    if kind in ('start', 'release', 'stop'):
                        self.assertLessEqual(count, 1, (sequence, p.calls))
                released = set()
                for c in p.calls:
                    self.assertFalse(c[0] in ('mode', 'start', 'stop') and c[2] in released,
                                     (sequence, p.calls))
                    if c[0] == 'release': released.add(c[2])
                if a.state == 'Stopped': self.assertIsNone(a.handle, sequence)
                if a.handle is not None:
                    self.assertEqual(a.owned[a.handle], a.generation, sequence)
                    self.assertNotIn(a.handle, a.released, sequence)


if __name__ == '__main__':
    unittest.main(verbosity=2)
