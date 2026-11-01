# Graphics-role depth semantics — editorial review

2026-11-01 UTC. Reviewed complete integrated role SHA256 `c650b5a74fa42898a527d2833a2ae926204c58b7f7db0c5c10a9665e9f4cfc17`, source note SHA256 `2c205fb735ab1b4b44cc03a0828010e42c2adb02769c7361bccb10f7f3776314`, baseline diff and independent source review. Independently reopened the official Godot 4.6 Advanced post-processing text at Full screen quad and Depth texture. No shader/model compilation or execution, image inspection, runtime archives or remote writes.

## Verdict

Accept the finite coordinate/quantity argument and original decision table. Recommend adding one premise to inverse projection/division: valid depth input, corresponding invertible projection, nonzero reconstructed w and a finite position; background/degenerate handling remains separately defined. No full shader or threshold recipe is needed.

## Checked substance

The text distinguishes sampled depth, renderer-specific NDC z and homogeneous clip coordinates. The documented d versus 2d−1 mapping is not mistaken for a universal clip.z equality. Homogeneous division is explicit. The note correctly avoids copying the historical migration article's vector/scalar comparison as runnable code.

The three-way decision is practical: raw ordering, signed view-axis separation and a separately defined geometric length are not interchangeable. Source-supported migration semantics do not mean every comparison must invert or every effect must use absolute differences. The mathematical example is exact: −z=4 for (3,0,−4), whereas its Euclidean norm is sqrt(9+16)=5. This is a hand example, not shader output. Perspective depth nonlinearity is not generalized to all projections or promoted into water-thickness evidence.

The employer role and historical Factorio content remain unchanged; the new example supplies a concrete graphics/TA parameter contract, not a universal employer stack. Initial reading and new source dates are distinct; mutable 4.6 documentation is not authenticated implementation code, and the 4.3 migration remains historical. Old adjacent compilation/asset evidence is not transferred to rendering or correctness here. No water effect, visual result, precision/performance gain or full pipeline acceptance is claimed.

Source paraphrase is compact and original analysis is labeled unexecuted. Pending only the bounded reconstruction premise and final role hash. No other correction requested.

## Final acceptance addendum

ACCEPT full role SHA256 `018d277f18458b8190c3959a707478593390eb688be2a90a5445b97bb21eded0` and unchanged source note `2c205fb735ab1b4b44cc03a0828010e42c2adb02769c7361bccb10f7f3776314`. Removing only the agreed finite-reconstruction premise reproduces initially reviewed role `c650b5a74fa42898a527d2833a2ae926204c58b7f7db0c5c10a9665e9f4cfc17`. The added premise closes the division/result domain without adding implementation or runtime claims. No further correction requested.
