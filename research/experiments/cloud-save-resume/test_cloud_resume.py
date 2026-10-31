"""Original serialized pre-dispatch model; not a filesystem or Steam simulation."""
from dataclasses import dataclass
import unittest

@dataclass(frozen=True)
class Save:
    rev: str
    parent: str
    value: int
    schema: int = 1

@dataclass(frozen=True)
class Job:
    epoch: int
    base: str
    save: Save

class Coordinator:
    def __init__(self, save):
        self.disk = self.memory = self.loaded = save
        self.base = save.rev
        self.epoch = 0
        self.mode = 'ready'
        self.dirty = False
        self.recovery = []
        self.known_ids = {save.rev}
        if save.parent:
            self.known_ids.add(save.parent)
        self.id_limit = 256  # finite teaching registry; production identity is external

    def edit(self, value):
        if self.mode != 'ready':
            raise RuntimeError('write gate closed')
        self.memory = Save(self.memory.rev, self.memory.parent, value)
        self.dirty = True

    def queue_save(self, rev):
        if self.mode != 'ready':
            raise RuntimeError('write gate closed')
        if type(rev) is not str or not rev or rev in self.known_ids:
            raise ValueError('new, nonempty string revision required')
        if len(self.known_ids) >= self.id_limit:
            raise RuntimeError('identity registry exhausted')
        self.known_ids.add(rev)  # reserve even if the queued job is later invalidated
        return Job(self.epoch, self.base, Save(rev, self.base, self.memory.value))

    def dispatch(self, job):
        # Guard and assignment are one serialized abstract operation, NOT disk CAS.
        if (self.mode != 'ready' or job.epoch != self.epoch
                or job.base != self.base or self.disk is None
                or self.disk != self.loaded or self.disk.rev != self.base or job.save.value != self.memory.value):
            return False
        self.disk = self.memory = self.loaded = job.save
        self.base = job.save.rev
        self.dirty = False
        self.epoch += 1  # reject other jobs prepared from the same state
        return True

    def invalidate(self):
        self.mode = 'reload'
        self.epoch += 1
        return self.epoch

    def downloaded(self, save):
        # Abstract harness delivers notification before any further dispatch.
        self.disk = save
        return self.invalidate()

    def finish_reload(self, token, candidate):
        if token != self.epoch or self.mode != 'reload':
            return False
        # A newer disk image with no notification also invalidates this read.
        if candidate != self.disk:
            self.invalidate()
            return False
        if (not isinstance(candidate, Save) or candidate.schema != 1
                or type(candidate.schema) is not int or type(candidate.rev) is not str
                or not candidate.rev or type(candidate.parent) is not str
                or type(candidate.value) is not int):
            self.mode = 'recovery'
            return False
        # A known noncurrent identity cannot become a new child of the baseline.
        # Conservative: repeated conflict candidates also remain recovery-only.
        if candidate.rev in self.known_ids and candidate.rev != self.base:
            self.mode = 'recovery'
            return False
        seen = {candidate.rev} | ({candidate.parent} if candidate.parent else set())
        if len(self.known_ids | seen) > self.id_limit:
            self.mode = 'recovery'
            return False
        self.known_ids.update(seen)
        if candidate.rev == self.base:
            # Same identity with different bytes is corruption, not a winner.
            if candidate != self.loaded:
                self.mode = 'recovery'
                return False
            self.mode = 'ready'
            return True
        if self.dirty or candidate.parent != self.base:
            self.recovery.append((self.memory, candidate))
            self.mode = 'conflict'
            return False
        self.memory = self.loaded = candidate
        self.base = candidate.rev
        self.mode = 'ready'
        return True

class Tests(unittest.TestCase):
    def setUp(self):
        self.a = Save('a', '', 1)
        self.b = Save('b', 'a', 2)
        self.c = Coordinator(self.a)

    def test_stale_queued_write_cannot_overwrite_download(self):
        self.c.edit(9); job = self.c.queue_save('local')
        self.c.downloaded(self.b)
        self.assertFalse(self.c.dispatch(job)); self.assertEqual(self.c.disk, self.b)

    def test_clean_fast_forward(self):
        t = self.c.downloaded(self.b)
        self.assertTrue(self.c.finish_reload(t, self.b))
        self.assertEqual(self.c.memory, self.b)

    def test_dirty_divergence_preserves_both(self):
        self.c.edit(9); t = self.c.downloaded(self.b)
        self.assertFalse(self.c.finish_reload(t, self.b))
        self.assertEqual(self.c.mode, 'conflict'); self.assertEqual(len(self.c.recovery), 1)
        self.assertEqual(self.c.memory.value, 9); self.assertEqual(self.c.disk, self.b)

    def test_old_load_completion_rejected(self):
        t = self.c.downloaded(self.b)
        d = Save('d', 'b', 3); self.c.downloaded(d)
        self.assertFalse(self.c.finish_reload(t, self.b)); self.assertEqual(self.c.disk, d)

    def test_missing_file_not_recreated(self):
        t = self.c.downloaded(None)
        self.assertFalse(self.c.finish_reload(t, None)); self.assertEqual(self.c.mode, 'recovery')
        self.assertIsNone(self.c.disk)

    def test_unknown_schema_fails_closed(self):
        bad = Save('b', 'a', 2, 99); t = self.c.downloaded(bad)
        self.assertFalse(self.c.finish_reload(t, bad)); self.assertEqual(self.c.mode, 'recovery')

    def test_no_notification_disk_change_rejects_queued_job(self):
        job = self.c.queue_save('local'); self.c.disk = self.b
        self.assertFalse(self.c.dispatch(job))

    def test_duplicate_notification_does_not_write(self):
        t = self.c.downloaded(self.b); self.c.finish_reload(t, self.b)
        t = self.c.invalidate(); self.assertTrue(self.c.finish_reload(t, self.b))
        self.assertEqual(self.c.disk, self.b)

    def test_sibling_revision_requires_policy(self):
        sibling = Save('other', 'root', 99); t = self.c.downloaded(sibling)
        self.assertFalse(self.c.finish_reload(t, sibling)); self.assertEqual(self.c.mode, 'conflict')

    def test_same_revision_changed_content_is_not_accepted(self):
        self.c.edit(9); corrupt = Save('a', '', 55)
        t = self.c.downloaded(corrupt)
        self.assertFalse(self.c.finish_reload(t, corrupt))
        self.assertEqual(self.c.mode, 'recovery')

    def test_unnotified_same_revision_content_preserved_on_dispatch(self):
        self.c.edit(9); job = self.c.queue_save('local')
        candidate = Save('a', '', 55); self.c.disk = candidate
        before = dict(self.c.__dict__)
        before['known_ids'] = self.c.known_ids.copy()
        before['recovery'] = self.c.recovery.copy()
        self.assertFalse(self.c.dispatch(job))
        self.assertEqual(self.c.__dict__, before)
        self.assertIs(self.c.disk, candidate)

    def test_ancestor_revision_cannot_be_reissued(self):
        self.assertTrue(self.c.dispatch(self.c.queue_save('b')))
        with self.assertRaises(ValueError): self.c.queue_save('a')
        self.assertEqual(self.c.disk.rev, 'b')

    def test_queued_and_observed_ids_cannot_be_reissued(self):
        self.c.queue_save('reserved')
        with self.assertRaises(ValueError): self.c.queue_save('reserved')
        t = self.c.downloaded(self.b); self.c.finish_reload(t, self.b)
        with self.assertRaises(ValueError): self.c.queue_save('a')
        with self.assertRaises(ValueError): self.c.queue_save('b')

    def test_revision_identity_requires_exact_nonempty_string(self):
        for invalid in ('', True, 1, 1.5, None):
            with self.subTest(rev=invalid):
                before = self.c.known_ids.copy()
                with self.assertRaises(ValueError): self.c.queue_save(invalid)
                self.assertEqual(self.c.known_ids, before)

    def test_identity_registry_exhaustion_fails_closed(self):
        self.c.id_limit = len(self.c.known_ids)
        with self.assertRaises(RuntimeError): self.c.queue_save('new')
        self.assertEqual(self.c.disk, self.a)

    def test_incoming_ancestor_id_cannot_form_cycle(self):
        self.assertTrue(self.c.dispatch(self.c.queue_save('b')))
        candidate = Save('a', 'b', 99)
        t = self.c.downloaded(candidate)
        self.assertFalse(self.c.finish_reload(t, candidate))
        self.assertEqual(self.c.mode, 'recovery')
        self.assertEqual(self.c.loaded.rev, 'b')
        self.assertIs(self.c.disk, candidate)

    def test_incoming_reserved_identity_is_recovery_only(self):
        self.c.queue_save('reserved')
        candidate = Save('reserved', 'a', 99)
        t = self.c.downloaded(candidate)
        self.assertFalse(self.c.finish_reload(t, candidate))
        self.assertEqual(self.c.mode, 'recovery')
        self.assertEqual(self.c.loaded, self.a)

    def test_gate_prevents_new_edits(self):
        self.c.invalidate()
        with self.assertRaises(RuntimeError): self.c.edit(4)
        with self.assertRaises(RuntimeError): self.c.queue_save('b')

    def test_duplicate_queued_jobs_only_one_dispatch(self):
        j1 = self.c.queue_save('one'); j2 = self.c.queue_save('two')
        self.assertTrue(self.c.dispatch(j1)); self.assertFalse(self.c.dispatch(j2))

    def test_disk_changed_during_read(self):
        t = self.c.downloaded(self.b); self.c.disk = Save('d', 'b', 3)
        self.assertFalse(self.c.finish_reload(t, self.b)); self.assertEqual(self.c.mode, 'reload')

if __name__ == '__main__':
    unittest.main(verbosity=2)
