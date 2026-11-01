"""Independent finite checks; no renderer or compliance verdict."""
import math
from fractions import Fraction as F
import unittest
import hud_contrast as h

class ReviewerChecks(unittest.TestCase):
    def test_rational_feasibility_bisection(self):
        # Solve by exact feasibility inequality and bisection, not author's inverse.
        for t in (1., 1.01, 2., 4.5, 7., 20., 21.):
            for b in (0., math.ulp(0.), 1e-300, .001, .1, .5, 1.):
                T,B=F(t),F(b)
                def feasible(a): return F(21,20) >= T*((1-a)*B+F(1,20))
                if feasible(F(0)): lo=hi=F(0)
                else:
                    lo,hi=F(0),F(1)
                    for _ in range(100):
                        mid=(lo+hi)/2
                        if feasible(mid): hi=mid
                        else: lo=mid
                got=h.minimum_panel_alpha(t,b)
                self.assertTrue(math.isfinite(got))
                self.assertGreaterEqual(got,0);self.assertLessEqual(got,1)
                # Approximation envelope only, deliberately not a safety assertion.
                self.assertLessEqual(abs(F(got)-(lo+hi)/2),F(1,10**14))
        print('49 exact-rational feasibility brackets compared; absolute envelope 1e-14')

    def test_literal_quantization_and_rounding(self):
        # Independent boundary inequality: target4.5, B1 iff 60*a >=49.
        self.assertLess(F(208,255)*60,49)
        self.assertGreater(F(209,255)*60,49)
        self.assertLess(h.white_text_contrast(208/255,1),4.5)
        self.assertGreater(h.white_text_contrast(209/255,1),4.5)
        a=h.minimum_panel_alpha(4.5,1)
        print('minimum alpha float',repr(a),'exact boundary delta',str(F(a)-F(49,60)))
        # No assertion that returned minimum is always on either side.

    def test_finite_edges_and_exact_types(self):
        class I(int): pass
        class D(float): pass
        for x in (I(0),D(.5),True):
            with self.assertRaises(TypeError):h.srgb_decode(x)
            with self.assertRaises(TypeError):h.minimum_panel_alpha(x,1)
        tiny=math.ulp(0.)
        for t in (1,math.nextafter(21.,0.),21):
            for b in (0,tiny,math.nextafter(1.,0.),1):
                a=h.minimum_panel_alpha(t,b)
                self.assertTrue(math.isfinite(a));self.assertGreaterEqual(a,0);self.assertLessEqual(a,1)
        self.assertEqual(h.minimum_panel_alpha(21,tiny),1)
        self.assertEqual(h.minimum_panel_alpha(21,0),0)
        self.assertEqual(h.srgb_decode(tiny),0) # documented finite precision, not exact real decoding
        self.assertEqual(h.white_text_contrast(0,tiny),21) # rounding erases tiny background
        print('subnormal observations: decode rounds to0; contrast rounds to21; not exact-real certificates')

    def test_monotonic_grid_and_decode_boundary(self):
        grid=[i/16 for i in range(17)]
        for b in grid:
            values=[h.white_text_contrast(a,b) for a in grid]
            self.assertEqual(values,sorted(values))
        for a in grid:
            values=[h.white_text_contrast(a,b) for b in grid]
            self.assertEqual(values,sorted(values,reverse=True))
        threshold=.04045
        values=[h.srgb_decode(c) for c in (math.nextafter(threshold,0),threshold,math.nextafter(threshold,1))]
        self.assertEqual(values,sorted(values))
        self.assertEqual(values[1],threshold/12.92)
        print('17x17 contrast monotonic grid; threshold predecessor/equal/successor checked')

if __name__=='__main__':unittest.main(verbosity=2)
