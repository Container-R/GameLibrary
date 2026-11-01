"""Synthetic arithmetic checks, not observed pixels or engine tests."""
import math
import unittest
from fractions import Fraction

from hud_contrast import (srgb_decode, srgb_luminance, panel_luminance,
                          white_text_contrast, minimum_panel_alpha)


class ContrastMathTests(unittest.TestCase):
    def test_hand_calculated_contrasts(self):
        # Independent rational expectations, not a second copy of implementation.
        for alpha, background, expected in [
            (0.5, 0.1, Fraction(21, 2)),
            (0.5, 1, Fraction(21, 11)),
            (0.85, 1, Fraction(21, 4)),
        ]:
            with self.subTest(alpha=alpha, background=background):
                self.assertAlmostEqual(white_text_contrast(alpha, background),
                                       float(expected), places=13)

    def test_analytic_minimum(self):
        self.assertAlmostEqual(minimum_panel_alpha(4.5, 1),
                               float(Fraction(49, 60)), places=15)
        self.assertEqual(minimum_panel_alpha(4.5, 0.1), 0)
        self.assertAlmostEqual(minimum_panel_alpha(7, 0.5), 0.8, places=15)

    def test_endpoints(self):
        for background in (0, 0.1, 1):
            self.assertEqual(panel_luminance(1, background), 0)
            self.assertEqual(white_text_contrast(1, background), 21)
            self.assertEqual(panel_luminance(0, background), background)
            self.assertEqual(minimum_panel_alpha(1, background), 0)
        self.assertEqual(white_text_contrast(0, 1), 1)
        self.assertEqual(white_text_contrast(0, 0), 21)
        self.assertEqual(minimum_panel_alpha(21, 0), 0)
        self.assertEqual(minimum_panel_alpha(21, 1), 1)

    def test_srgb_decode(self):
        self.assertEqual(srgb_decode(0), 0)
        self.assertEqual(srgb_decode(1), 1)
        self.assertEqual(srgb_decode(0.04045), 0.04045 / 12.92)
        self.assertAlmostEqual(srgb_decode(0.5), 0.21404114048223255, places=15)
        self.assertNotEqual(srgb_decode(0.5), 0.5)
        self.assertAlmostEqual(srgb_luminance(0.5, 0.5, 0.5),
                               0.21404114048223255, places=15)

    def test_luminance_primary_weights(self):
        self.assertEqual(srgb_luminance(1, 0, 0), 0.2126)
        self.assertEqual(srgb_luminance(0, 1, 0), 0.7152)
        self.assertEqual(srgb_luminance(0, 0, 1), 0.0722)
        self.assertEqual(srgb_luminance(0, 0, 0), 0)
        self.assertEqual(srgb_luminance(1, 1, 1), 1)

    def test_no_threshold_rounding(self):
        # Close but below 4.5: display rounding must not turn it into >= 4.5.
        value = white_text_contrast(49 / 60 - 1e-10, 1)
        self.assertLess(value, 4.5)
        self.assertEqual(round(value, 2), 4.5)

    def test_domains_at_every_argument(self):
        calls = [lambda x: srgb_decode(x),
                 lambda x: srgb_luminance(x, 0, 0),
                 lambda x: srgb_luminance(0, x, 0),
                 lambda x: srgb_luminance(0, 0, x),
                 lambda x: panel_luminance(x, 1),
                 lambda x: panel_luminance(1, x),
                 lambda x: white_text_contrast(x, 1),
                 lambda x: white_text_contrast(1, x),
                 lambda x: minimum_panel_alpha(4.5, x)]
        for call in calls:
            for bad in (True, False, '0.5', None, complex(0.5), Fraction(1, 2)):
                with self.subTest(call=calls.index(call), kind=type(bad).__name__):
                    with self.assertRaises(TypeError):
                        call(bad)
            for bad in (-0.01, 1.01, math.nan, math.inf, -math.inf, 10**1000):
                with self.assertRaises(ValueError):
                    call(bad)
        for bad in (True, '4.5', None):
            with self.assertRaises(TypeError):
                minimum_panel_alpha(bad, 1)
        for bad in (0, 0.999, 21.001, math.nan, math.inf, -math.inf, 10**1000):
            with self.assertRaises(ValueError):
                minimum_panel_alpha(bad, 1)


if __name__ == '__main__':
    unittest.main()
