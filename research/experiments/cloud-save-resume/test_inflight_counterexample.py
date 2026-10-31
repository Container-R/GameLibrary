"""A counterexample, NOT a safety test or a model of Steam scheduling."""
import unittest
from test_cloud_resume import Coordinator, Save

class InflightCounterexample(unittest.TestCase):
    def test_completion_rejection_cannot_undo_already_issued_write(self):
        old = Save('a', '', 1)
        c = Coordinator(old)
        old_completion_epoch = c.epoch
        # Hypothesis: an external write was already dispatched with old bytes.
        # No call to Coordinator.dispatch: its pre-dispatch guard is too late.
        newer = Save('b', 'a', 2)
        c.downloaded(newer)
        c.disk = old  # external in-flight operation now takes effect
        completion_accepted = old_completion_epoch == c.epoch
        self.assertFalse(completion_accepted)
        self.assertEqual(c.disk, old)
        self.assertNotEqual(c.disk, newer)
        # Therefore merely dropping an obsolete completion does not restore b.

if __name__ == '__main__':
    unittest.main(verbosity=2)
