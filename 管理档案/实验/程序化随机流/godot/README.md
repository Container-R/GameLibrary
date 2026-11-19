# Actual Godot RNG ownership fixture

Run `python run.py`. Uses installed Godot, isolated temporary project and XDG paths, 60-second timeout plus engine frame cap. No install or change to other projects. `observed.json` is native engine output parsed and deterministically formatted, verified byte-identical across two executions.

A shared RandomNumberGenerator with seed 424242 makes two initial room decisions. Without decoration, next six decisions are [149008,865485,462888,51428,904232,692613]. An extra decoration randi_range(0,999999) consumes 149008; the room suffix becomes [865485,462888,51428,904232,692613,816460]. All calls intentionally use the same range so the sequence-shift comparison has no range-mapping ambiguity. These integers are synthetic room decisions, not a generated/playtested game map.

Separate layout and decoration RNG objects use explicit fixed seeds 424242 and 701293. Extra decoration returns 821771 without advancing the layout RNG, leaving the original room suffix exactly unchanged. This proves isolation of mutable stream consumption, not statistical independence or nonoverlapping periods. No assertion that nearby seeds are independent, nor recommendation that seed+1 is a production stream derivation scheme. Caller should specify subsystem ownership and stable seed derivation separately.

Same-object checkpoint: save .state after three draws; draw five; assign the previously saved .state and repeat, obtaining identical five integers. Restore happens on the same seeded object in the same build. A state decimal string preserves its signed 64-bit value in JSON without relying on downstream JSON numeric precision.

Version is actual self-report 4.6.3-stable (official), full engine hash recorded. Baseline sequence is explicitly pinned in an assertion to this tested build. A different version/build may fail the pin; do not update it blindly or claim cross-version save/replay compatibility. Thread scheduling, map traversal order, generator algorithm migration, and random draws inside the SAME subsystem remain out of scope: separate streams do not automatically make those stable.
