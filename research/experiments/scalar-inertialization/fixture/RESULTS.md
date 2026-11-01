# Numerical results — author run

2026-11-01 UTC. Two processes: normal Python and `-O`; each executed 8 unittest methods successfully, not 16 distinct scenarios. No failures observed in these first runs. Full component-wise values/errors are in JSON; no tolerance revisions.

| Case | Max coarse absolute error | Max fine absolute error | Coarse/fine | Interpretation |
|---|---:|---:|---:|---|
| Z | 0 | 0 | n/a | Small/zero: ratio not used |
| P | 1.48580614e-09 | 9.21104304e-11 | 16.13070461648609 | Refinement observed |
| V | 9.28026212e-10 | 5.75502033e-11 | 16.12550710151233 | Refinement observed |
| G | 3.34185823e-09 | 2.07210915e-10 | 16.127809836100706 | Refinement observed |
| X | 2.22629848e-09 | 1.38090539e-10 | 16.1220203423516 | Refinement observed |
| N | 5.5540017e-12 | 3.46833673e-13 | 16.013444302176698 | Small/zero: ratio not used |
| F | 2.74902018e-07 | 1.66217542e-08 | 16.538688678574072 | Refinement observed |

This maximum combines numeric errors of position and velocity for the predeclared refinement check; their units remain different. Each component and its units are represented separately by array position in raw tables: [position L, velocity L/s]. Two resolutions are not an asymptotic order proof.

## Expected counterexamples (not contract failures)

- `position_only_velocity_jump`: `0.3292627983322971`
- `raw_only_value_velocity_jumps`: `[0.9326096119087369, 0.8882555147755387]`
- `initial_growth`: `[1.1682011746071073, 0.7788007830714049]`
- `position_crossing_not_settled`: `[0.0, -0.7357588823428847]`
- `after_crossing`: `[-0.1353352832366127, 0.0]`
- `half_parameter_result`: `[0.5965735902799727, -0.9609060278364028]`
- `half_parameter_distance_from_half`: `0.0965735902799727`

- First switch acceleration jump: `1.4829488066708114` L/s².
- Guard rejection cases: `139` per process.
- Direct final state: `[0.38919911521562955, -0.10063863125189981]`.

Numeric payloads identical normal/-O: True. Interpreter/source/protocol identities are recorded separately.

These are scalar numerical results, not engine, animation-quality, contact, quaternion or performance results.
