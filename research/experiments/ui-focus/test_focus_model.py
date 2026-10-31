"""Original policy model only: not Unity events, rendering, input, or accessibility APIs."""
from dataclasses import dataclass
import unittest

@dataclass
class Node:
    scope: str
    generation: int = 1
    live: bool = True
    enabled: bool = True
    visible: bool = True
    focusable: bool = True

class FocusModel:
    def __init__(self):
        self.nodes = {'open': Node('page'), 'safe': Node('page'),
                      'a': Node('dialog-a'), 'a-next': Node('dialog-a'), 'b': Node('dialog-b')}
        self.defaults = {'page': 'safe', 'dialog-a': 'a', 'dialog-b': 'b'}
        self.stack = [('page', None, 0)]
        self.next_frame_token = 1
        self.focus = ('open', 1)
        self.revision = 0

    def eligible(self, ref):
        n = self.nodes.get(ref[0]) if ref else None
        return bool(n and n.generation == ref[1] and n.scope == self.stack[-1][0]
                    and n.live and n.enabled and n.visible and n.focusable)

    def resolve(self, preferred=None):
        name = self.defaults.get(self.stack[-1][0])
        default = (name, self.nodes[name].generation) if name in self.nodes else None
        self.focus = next((r for r in (preferred, default) if self.eligible(r)), None)
        return self.focus

    def open(self, scope):
        if any(frame[0] == scope for frame in self.stack):
            raise ValueError('model forbids concurrent reuse of a scope name')
        token = self.next_frame_token
        self.next_frame_token += 1
        self.stack.append((scope, self.focus, token))
        self.revision += 1
        self.resolve()
        return token

    def close(self, token):
        if len(self.stack) == 1 or self.stack[-1][2] != token:
            return False  # late/double/out-of-order close cannot pop another scope
        _, opener, _ = self.stack.pop()
        self.revision += 1
        self.resolve(opener)
        return True

    def user_focus(self, ref):
        if not self.eligible(ref):
            return False
        self.revision += 1  # newer intent invalidates pending requests in the same scope
        self.focus = ref
        return True

    def deferred_focus(self, revision, ref):
        if revision != self.revision or not self.eligible(ref):
            return False
        self.focus = ref
        return True

class Tests(unittest.TestCase):
    def test_same_scope_reentry_rejected_without_mutation(self):
        m = FocusModel(); m.open('dialog-a')
        before = (list(m.stack), m.revision, m.focus, m.next_frame_token)
        with self.assertRaises(ValueError): m.open('dialog-a')
        self.assertEqual((m.stack,m.revision,m.focus,m.next_frame_token),before)

    def test_nested_restore(self):
        m = FocusModel(); a_token = m.open('dialog-a'); b_token = m.open('dialog-b')
        m.close(b_token); self.assertEqual(m.focus, ('a', 1))
        m.close(a_token); self.assertEqual(m.focus, ('open', 1))

    def test_opener_removed(self):
        m = FocusModel(); a_token = m.open('dialog-a'); del m.nodes['open']
        m.close(a_token); self.assertEqual(m.focus, ('safe', 1))

    def test_each_invalid_flag_falls_back(self):
        for flag in ('live', 'enabled', 'visible', 'focusable'):
            with self.subTest(flag=flag):
                m = FocusModel(); a_token = m.open('dialog-a'); setattr(m.nodes['open'], flag, False)
                m.close(a_token); self.assertEqual(m.focus, ('safe', 1))

    def test_recycled_id_is_not_old_opener(self):
        m = FocusModel(); a_token = m.open('dialog-a'); m.nodes['open'] = Node('page', generation=2)
        m.close(a_token); self.assertEqual(m.focus, ('safe', 1))

    def test_no_background_focus(self):
        m = FocusModel(); a_token = m.open('dialog-a')
        self.assertFalse(m.deferred_focus(m.revision, ('open', 1)))
        self.assertEqual(m.focus, ('a', 1))

    def test_stale_callback_cannot_steal_focus(self):
        m = FocusModel(); a_token = m.open('dialog-a'); old = m.revision
        m.close(a_token); b_token = m.open('dialog-b')
        self.assertFalse(m.deferred_focus(old, ('a', 1)))
        self.assertEqual(m.focus, ('b', 1))

    def test_out_of_order_close_is_rejected(self):
        m = FocusModel(); a_token = m.open('dialog-a'); b_token = m.open('dialog-b')
        self.assertFalse(m.close(a_token)); self.assertEqual(m.focus, ('b', 1))

    def test_user_navigation_supersedes_pending_focus(self):
        m = FocusModel(); m.open('dialog-a'); old = m.revision
        self.assertTrue(m.user_focus(('a-next', 1)))
        self.assertFalse(m.deferred_focus(old, ('a', 1)))
        self.assertEqual(m.focus, ('a-next', 1))

    def test_old_close_cannot_close_reopened_same_scope(self):
        m = FocusModel(); old_token = m.open('dialog-a')
        self.assertTrue(m.close(old_token))
        new_token = m.open('dialog-a'); revision = m.revision
        self.assertNotEqual(old_token, new_token)
        self.assertFalse(m.close(old_token))
        self.assertEqual(m.revision, revision)
        self.assertEqual(m.focus, ('a', 1))
        self.assertEqual(m.stack[-1][2], new_token)
        self.assertTrue(m.close(new_token))
        self.assertEqual(m.focus, ('open', 1))

    def test_no_candidate_does_not_escape_scope(self):
        m = FocusModel(); m.nodes['a'].visible = False; a_token = m.open('dialog-a')
        self.assertIsNone(m.focus); self.assertEqual(m.stack[-1][0], 'dialog-a')

if __name__ == '__main__':
    unittest.main(verbosity=2)
