"""Independent cloud regression checks; initial draft failures archived separately."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cloud-save-resume'))
from test_cloud_resume import Coordinator, Save

class AdversarialTests(unittest.TestCase):
    def test_same_revision_changed_disk_without_notification_blocks_dispatch(self):
        c=Coordinator(Save('a','',1))
        c.edit(9)
        job=c.queue_save('local')
        corrupt=Save('a','',55)
        c.disk=corrupt
        self.assertFalse(c.dispatch(job), 'dispatch should compare loaded content, not revision alone')
        self.assertEqual(c.disk,corrupt)

    def test_old_revision_identity_not_reused(self):
        c=Coordinator(Save('a','',1))
        c.edit(2);self.assertTrue(c.dispatch(c.queue_save('b')))
        c.edit(3)
        try:
            old_id_job=c.queue_save('a')
        except ValueError:
            return
        self.assertFalse(c.dispatch(old_id_job), 'a was already a different immutable revision')

    def test_same_snapshot_notification_preserves_dirty_memory(self):
        a=Save('a','',1);c=Coordinator(a);c.edit(9)
        token=c.downloaded(a)
        self.assertTrue(c.finish_reload(token,a))
        self.assertTrue(c.dirty)
        self.assertEqual(c.memory.value,9)

    def test_late_conflict_candidate_rejected_after_third_revision(self):
        c=Coordinator(Save('a','',1));c.edit(9)
        b=Save('b','a',2);token=c.downloaded(b)
        self.assertFalse(c.finish_reload(token,b))
        d=Save('d','b',3);newtoken=c.downloaded(d)
        self.assertFalse(c.finish_reload(token,b))
        self.assertFalse(c.finish_reload(newtoken,d))
        self.assertEqual(c.mode,'conflict')
        self.assertEqual(c.memory.value,9)
        self.assertEqual(c.disk,d)

    def test_dirty_deletion_does_not_recreate(self):
        c=Coordinator(Save('a','',1));c.edit(9)
        token=c.downloaded(None)
        self.assertFalse(c.finish_reload(token,None))
        self.assertEqual(c.mode,'recovery')
        self.assertEqual(c.memory.value,9)
        self.assertIsNone(c.disk)

if __name__=='__main__':unittest.main(verbosity=2)
