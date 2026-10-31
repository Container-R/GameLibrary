"""Original discrete protocol model. No networking, physics, or engine integration."""
from dataclasses import dataclass
import unittest

@dataclass(frozen=True)
class Command:
    epoch: int
    seq: int
    axis: int

@dataclass(frozen=True)
class Snapshot:
    epoch: int
    tick: int
    ack: int
    x: int

class Server:
    def __init__(self, epoch=1):
        self.epoch, self.tick, self.ack, self.x = epoch, 0, 0, 0
        self.pending = {}
    def receive(self, c):
        if not isinstance(c, Command):
            return False
        if (type(c.epoch) is not int or c.epoch <= 0
                or type(c.seq) is not int or c.seq <= 0):
            return False
        if c.epoch != self.epoch or c.seq <= self.ack or c.seq > self.ack + 32:
            return False
        self.pending.setdefault(c.seq, c)  # duplicate: first accepted payload wins
        return True
    def step(self):
        self.tick += 1
        c = self.pending.pop(self.ack + 1, None)
        if c is not None:
            # Fixed displacement quantum, no client-supplied duration/position.
            self.x += c.axis if type(c.axis) is int and c.axis in (-1, 0, 1) else 0
            self.ack = c.seq  # invalid payload is finalized as no-op
        return Snapshot(self.epoch, self.tick, self.ack, self.x)

class Client:
    def __init__(self, epoch=1, history_limit=32):
        self.epoch, self.seq, self.last_tick, self.ack, self.x = epoch, 0, -1, 0, 0
        self.pending, self.effects = [], set()
        self.history_limit = history_limit
    def issue(self, axis):
        if len(self.pending) >= self.history_limit:
            raise BufferError('history full: pause prediction, request resync')
        if type(axis) is not int or axis not in (-1, 0, 1):
            raise ValueError('invalid local axis')
        self.seq += 1
        c = Command(self.epoch, self.seq, axis)
        self.pending.append(c)
        self.x += axis
        self.effects.add((c.epoch, c.seq, 'step'))
        return c
    def reconcile(self, s):
        if not isinstance(s, Snapshot):
            raise ValueError('invalid snapshot envelope')
        if (type(s.epoch) is not int or s.epoch <= 0
                or type(s.tick) is not int or s.tick < 0
                or type(s.ack) is not int or s.ack < 0
                or type(s.x) is not int):
            raise ValueError('invalid snapshot envelope')
        if s.epoch != self.epoch or s.tick <= self.last_tick:
            return False
        if not self.ack <= s.ack <= self.seq:
            raise ValueError('invalid acknowledged prefix')
        self.last_tick, self.ack = s.tick, s.ack
        self.pending = [c for c in self.pending if c.seq > s.ack]
        self.x = s.x + sum(c.axis for c in self.pending)
        # Replaying simulation never emits one-shot presentation effects.
        return True

class ContractTests(unittest.TestCase):
    def test_ack_replays_only_suffix(self):
        c, s = Client(), Server()
        a, b = c.issue(1), c.issue(1)
        s.receive(a); c.reconcile(s.step())
        self.assertEqual((c.x, len(c.pending)), (2, 1))
        s.receive(b); c.reconcile(s.step())
        self.assertEqual((c.x, len(c.pending)), (2, 0))
    def test_reordered_delivery_cannot_ack_gap(self):
        c, s = Client(), Server()
        a, b = c.issue(1), c.issue(-1)
        s.receive(b)
        self.assertEqual(s.step().ack, 0)
        s.receive(a)
        self.assertEqual(s.step().ack, 1)
        self.assertEqual(s.step().ack, 2)
        self.assertEqual(s.x, 0)
    def test_retry_duplicate_not_extra_movement(self):
        c, s = Client(), Server(); a = c.issue(1)
        s.receive(a); s.receive(a); s.step()
        self.assertFalse(s.receive(a)); s.step()
        self.assertEqual(s.x, 1)
    def test_stale_snapshot_ignored(self):
        c = Client(); c.issue(1)
        c.reconcile(Snapshot(1, 5, 1, 1))
        self.assertFalse(c.reconcile(Snapshot(1, 4, 0, 100)))
        self.assertEqual(c.x, 1)
    def test_new_tick_same_ack_applies_correction(self):
        c = Client(); c.issue(1)
        c.reconcile(Snapshot(1, 5, 1, 1))
        self.assertTrue(c.reconcile(Snapshot(1, 6, 1, -3)))
        self.assertEqual(c.x, -3)
    def test_invalid_input_finalized_without_trust(self):
        s = Server(); s.receive(Command(1, 1, 999)); r = s.step()
        self.assertEqual((r.x, r.ack), (0, 1))
    def test_snapshot_does_not_duplicate_effect(self):
        c = Client(); c.issue(1); c.issue(1)
        c.reconcile(Snapshot(1, 5, 0, 0)); c.reconcile(Snapshot(1, 6, 1, 1))
        self.assertEqual(len(c.effects), 2)
    def test_epoch_rejects_old_life(self):
        c, s = Client(2), Server(2)
        self.assertFalse(s.receive(Command(1, 1, 1)))
        self.assertFalse(c.reconcile(Snapshot(1, 10, 0, 99)))
    def test_history_exhaustion_not_silent_loss(self):
        c = Client(history_limit=2); c.issue(1); c.issue(1)
        with self.assertRaises(BufferError): c.issue(1)
        self.assertEqual(len(c.pending), 2)
    def test_impossible_ack_rejected(self):
        c = Client(); c.issue(1)
        with self.assertRaises(ValueError): c.reconcile(Snapshot(1, 1, 2, 0))
    def test_malformed_command_envelopes_rejected_without_mutation(self):
        s = Server()
        bad = [None, {}, Command(True, 1, 1), Command(0, 1, 1),
               Command(1.0, 1, 1), Command(1, True, 1),
               Command(1, 1.0, 1), Command(1, 0, 1), Command(1, -1, 1)]
        for c in bad:
            with self.subTest(c=c):
                self.assertFalse(s.receive(c))
                self.assertEqual((s.ack, s.x, s.pending), (0, 0, {}))
    def test_command_window_boundaries(self):
        s = Server()
        self.assertTrue(s.receive(Command(1, 32, 1)))
        self.assertFalse(s.receive(Command(1, 33, 1)))
        self.assertEqual(s.ack, 0)
    def test_malformed_snapshot_envelopes_rejected_before_mutation(self):
        c = Client(); c.issue(1)
        baseline = (c.last_tick, c.ack, c.x, list(c.pending))
        bad = [None, {}, Snapshot(True, 1, 0, 0), Snapshot(0, 1, 0, 0),
               Snapshot(1.0, 1, 0, 0), Snapshot(1, True, 0, 0),
               Snapshot(1, 1.0, 0, 0), Snapshot(1, -1, 0, 0),
               Snapshot(1, 1, True, 0), Snapshot(1, 1, 0.0, 0),
               Snapshot(1, 1, -1, 0), Snapshot(1, 1, 0, True),
               Snapshot(1, 1, 0, 1.0)]
        for snapshot in bad:
            with self.subTest(snapshot=snapshot):
                with self.assertRaises(ValueError): c.reconcile(snapshot)
                self.assertEqual((c.last_tick, c.ack, c.x, c.pending), baseline)
    def test_zero_tick_and_ack_valid(self):
        c = Client()
        self.assertTrue(c.reconcile(Snapshot(1, 0, 0, 0)))
    def test_regressed_ack_rejected_before_mutation(self):
        c = Client(); c.issue(1)
        c.reconcile(Snapshot(1, 2, 1, 1))
        with self.assertRaises(ValueError): c.reconcile(Snapshot(1, 3, 0, 9))
        self.assertEqual((c.last_tick, c.ack, c.x), (2, 1, 1))
    def test_rate_budget_one_command_per_server_tick(self):
        s = Server()
        for i in range(1, 21): s.receive(Command(1, i, 1))
        s.step()
        self.assertEqual((s.x, s.ack), (1, 1))

if __name__ == '__main__': unittest.main(verbosity=2)
