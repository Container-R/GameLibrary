# Main source reading: assignment versus session exposure

2026-11-01. Original source: Yu Zhu, Zehang Richard Li, Yang Su and Zhenyu Zhao, *Treatment Effect Estimation Amidst Dynamic Network Interference in Online Gaming Experiments*, arXiv:2402.05336v1, 2024-02-08. Fixed text: https://arxiv.org/html/2402.05336v1 .

The main integrator directly read HTML sections 1–6, including definitions and formulas, and reopened sections 2–4 during the current review. Images, downloadable data, simulation code and estimator execution were not examined. Author affiliation is not proof of current production implementation or peer review.

Section 2 describes player-level initial assignment and a shared-team activation rule. Section 3 adds exposure-count sufficiency and joint unconfoundedness assumptions; neither follows merely from assignment randomization. Section 4 contains inconsistent wording about the direction of a naive estimate compared with nearby explanations and sections 2/5. Section 6 retains matching and applicability limitations. No bias direction, numerical benefit, estimator unbiasedness or general PvP isolation is accepted here.

Independent method-gate review was read before commissioning the note. Its acceptance is limited to measurement provenance: keep initial assignment, rule-predicted activation and observed delivery distinguishable; missing evidence is unknown. Original finite session traces can show different records and lossy counting, not treatment effects. Session rows are not automatically independent users; assigned users with no sessions need an explicit inclusion policy. Preserved logs do not establish causal identification. Assignment-policy and exposure-specific questions must not be conflated, nor all assignment-based comparisons dismissed indiscriminately.

No user telemetry, experimental deployment or runtime evidence is included. The separate Roblox documentation lead is deferred rather than merged into this source’s mechanism.
