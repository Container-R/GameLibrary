import unittest
from sequence_wrap import compare, reliable_window_not_rejected


def piecewise_rfc(candidate, reference, bits):
    """Independent ordinary-integer inequalities from RFC 1982 section 3.2.

    Deliberately no modulo/distance formulation and no call to model helpers.
    This oracle is used only with enumerated in-domain inputs.
    """
    half = 2 ** (bits - 1)
    if candidate == reference:
        return 'equal'
    if (candidate < reference and reference - candidate > half) or (
            candidate > reference and candidate - reference < half):
        return 'forward'
    if (candidate < reference and reference - candidate < half) or (
            candidate > reference and candidate - reference > half):
        return 'backward'
    return 'ambiguous'


class SequenceTests(unittest.TestCase):
    def test_exhaustive_4_and_8_bit_pairs(self):
        reverse = {'equal': 'equal', 'forward': 'backward',
                   'backward': 'forward', 'ambiguous': 'ambiguous'}
        total = 0
        for bits, expected_pairs in ((4, 256), (8, 65536)):
            checked = 0
            counts = dict.fromkeys(reverse, 0)
            for candidate in range(1 << bits):
                for reference in range(1 << bits):
                    got = compare(candidate, reference, bits)
                    self.assertEqual(got, piecewise_rfc(candidate, reference, bits),
                                     (bits, candidate, reference))
                    self.assertEqual(compare(reference, candidate, bits), reverse[got],
                                     (bits, candidate, reference))
                    counts[got] += 1
                    checked += 1
            self.assertEqual(checked, expected_pairs)
            self.assertEqual(counts['equal'], 1 << bits)
            self.assertEqual(counts['ambiguous'], 1 << bits)
            self.assertEqual(counts['forward'], ((1 << bits) * ((1 << (bits-1))-1)))
            self.assertEqual(counts['forward'], counts['backward'])
            total += checked
        self.assertEqual(total, 65792)

    def test_wrap_14_to_1(self):
        self.assertEqual(compare(1, 14, 4), 'forward')
        self.assertEqual(compare(14, 1, 4), 'backward')

    def test_half_circle(self):
        self.assertEqual(compare(8, 0, 4), 'ambiguous')
        self.assertEqual(compare(0, 8, 4), 'ambiguous')

    def test_cycle_not_total_order(self):
        for old, new in ((0, 6), (6, 12), (12, 0)):
            self.assertEqual(compare(new, old, 4), 'forward')
        self.assertEqual(compare(12, 0, 4), 'backward')

    def test_same_wire_value_cannot_recover_generation(self):
        # Absolute labels are invented explanatory metadata, NOT comparator inputs.
        first_generation, next_generation = 1, 17
        self.assertNotEqual(first_generation, next_generation)
        self.assertEqual(first_generation % 16, next_generation % 16)
        self.assertEqual(compare(first_generation % 16, next_generation % 16, 4), 'equal')

    def test_invalid_bits(self):
        for bits in (True, False, 0, 1, 17, -2, 4.0, '4', None):
            with self.subTest(bits=bits), self.assertRaises(ValueError):
                compare(0, 1, bits)

    def test_invalid_values_both_positions(self):
        for value in (True, False, -1, 16, 999, 1.0, '1', None):
            for candidate, reference in ((value, 0), (0, value)):
                with self.subTest(candidate=candidate, reference=reference), self.assertRaises(ValueError):
                    compare(candidate, reference, 4)

    def test_integer_subclasses_rejected(self):
        class OtherInt(int):
            pass
        for args in ((OtherInt(1), 0, 4), (1, OtherInt(0), 4), (1, 0, OtherInt(4))):
            with self.assertRaises(ValueError):
                compare(*args)

    def test_teaching_width_limits(self):
        self.assertEqual(compare(0, 3, 2), 'forward')
        self.assertEqual(compare(0, 65535, 16), 'forward')
        self.assertEqual(compare(32768, 0, 16), 'ambiguous')
        self.assertEqual(compare(1, 1, 16), 'equal')

    def test_half_range_does_not_replace_enet_window(self):
        self.assertEqual(compare(28672, 0, 16), 'forward')
        self.assertFalse(reliable_window_not_rejected(28672, 0))
        self.assertTrue(reliable_window_not_rejected(28671, 0))

    def test_enet_wrap_window_only(self):
        self.assertTrue(reliable_window_not_rejected(1, 65534))
        self.assertTrue(reliable_window_not_rejected(65534, 65534))
        # Equality passes this guard; real reliable processing rejects it later.
        self.assertFalse(reliable_window_not_rejected(65533, 65534))

    def test_window_bad_values_both_positions(self):
        for value in (True, False, -1, 65536, 1.0, '1', None):
            for candidate, current in ((value, 0), (0, value)):
                with self.subTest(candidate=candidate, current=current), self.assertRaises(ValueError):
                    reliable_window_not_rejected(candidate, current)


if __name__ == '__main__':
    unittest.main()
