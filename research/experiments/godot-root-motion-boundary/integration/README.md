# Static native root-motion archive integration check

Run `python check_archives.py PATH/TO/research/experiments/godot-root-motion-boundary` after author files/results are at that root and independent archive is at `review/` (including `review/fixture` and `review/evidence`). Only the positional directory is accessed; historical engine/temp paths are compared as recorded strings, never opened. No installed Godot or current binary is required.

The checker pins four original source SHA256 values, binds each author/reviewer UUID summary to actual sources and all eight output files, associates single raw RESULT_JSON with parsed JSON, validates two behavior commands plus one version command per archive, and independently checks literal positions and sign-invariant full rotation matrices at tolerance 1e-5. It does not import author/reviewer implementations. Explicit exceptions remain active under `-O`.

Actual static runs on an isolated assembled copy both exited 0; normal and `-O` stdout were identical and stderr empty. Commands and outputs are retained. Zero engine executions. `old-root-motion-hash-audit.json` independently compares the unchanged original README/test/source files between recovered and publication baselines; no old fixture file was edited or rerun.

PASS means these finite archived receipts and literal numeric observations are internally consistent with the pinned source identity. It is not proof that logs cannot be forged, that the local engine is an authenticated official build, or that unrelated animation/Rig/IK behavior was tested. This checker writes only stdout; a failure does not remove archival evidence and must not be interpreted as a new accepted receipt. Files in assembled/ are temporary test copies, not an additional runtime run.
