"""Additional isolated input-domain and caller-state checks, not more combat cases."""
import unittest
from model import simultaneous, immediate


class DomainTests(unittest.TestCase):
    def test_invalid_health(self):
        for hp in ({'A': True, 'B': 1}, {'A': -1, 'B': 1}, {'A': 2, 'B': 1}, {'A': 1}):
            for method in (simultaneous, immediate):
                with self.subTest(hp=hp, method=method.__name__), self.assertRaises(ValueError):
                    method(hp, (), 7)

    def test_invalid_tick(self):
        for tick in (True, -1, 7.0):
            with self.subTest(tick=tick), self.assertRaises(ValueError):
                simultaneous({'A': 1, 'B': 1}, (), tick)

    def test_command_domain(self):
        for command in (('A', '', 'B'), ('A', 'hit', 'A'), ('C', 'hit', 'B'), ('A', 'hit')):
            with self.subTest(command=command), self.assertRaises(ValueError):
                simultaneous({'A': 1, 'B': 1}, (command,), 7)

    def test_multiple_commands_per_actor_rejected(self):
        with self.assertRaises(ValueError):
            simultaneous({'A': 1, 'B': 1}, (('A', 'one', 'B'), ('A', 'two', 'B')), 7)

    def test_result_not_alias_caller(self):
        hp = {'A': 1, 'B': 1}
        out = simultaneous(hp, (), 7)
        out['hp']['A'] = 0
        self.assertEqual(hp, {'A': 1, 'B': 1})


if __name__ == '__main__':
    unittest.main(verbosity=2)
