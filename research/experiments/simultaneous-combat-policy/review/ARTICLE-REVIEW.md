# Supplemental article editorial review

2026-10-31. Accepted core item 6 addition and section “同 tick 规则补充：可重复结果仍可能实现错了政策” in `solutions/programming/fixed-step-simulation-boundary.md`.

Reviewed staging article SHA256: `60c63eff643e0890ab59e22c9cccc8401d61ee234666730a28e65b553df36dc0`. This identifies the whole file; review scope is only the named new material, not a renewed audit of all older sections.

The text accurately distinguishes reproducible execution order from the explicitly selected simultaneous rule. Both attacker and target must be alive at tick start; two initially living mutual attackers produce two damage and two death records. Canonical immediate ordering consistently favors A in the frozen example but is not mislabeled a universal design defect. Twelve unique inputs, four both-alive disagreements per immediate implementation, eight initially-dead agreements, four next-tick checks, five unittest methods, and the targeted policy-substitution rejection match accepted evidence.

The section correctly limits evidence to a pure Python standard-library model and canonical state/event comparison. It does not claim actual publication ordering, cross-invocation exactly-once effects, engine callback ordering, physics, networking, or universal fairness. It explicitly recognizes intentionally sequential combat policies. No material correction requested. No code changed or new runtime execution performed for this editorial pass; independent execution evidence remains in REVIEW.md.
