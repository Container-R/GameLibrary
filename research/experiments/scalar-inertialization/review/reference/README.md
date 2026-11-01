# Protocol-only independent reference

Prepared and source-hashed 2026-11-01 02:08 UTC BEFORE inspecting author implementation or numerical results. Input is accepted protocol `b39a921ebd231066e3d31ea2e52b3193212255210a63feb94c9ef1c016784c27` and the preceding independent algebra/source review only.

`reference.py` SHA256 `0399074e7da9ba454d05b1e08282a876364270b198aac50dff6013f3fba18ab8` is an independently written classical RK4 integrator of the two-state ODE. It imports no author code, uses no exponential closed form, and does not read author outputs. Both step sizes independently restart from initial states; each requested endpoint is integrated independently, rather than taken from a shared author trajectory. Target sine/ramp functions and transition timestamps are the protocol's specified inputs, not independently invented cases. Their analytic derivatives are used only for target state/acceleration, not as a substitute for integrating the residual.

Executed exactly one pure Python command:

```
python research-drafts/deep-qa/animation-smoothing/reference/reference.py
```

stdout archived as `reference-output.json`; stderr empty; exit 0 in `process.txt`. No engine, external native probe or installation; the Python standard-library runtime is used. `SHA256SUMS` was written before execution. This output is independent reference data, NOT a claim that author code passed or that finite agreement proves global numerical correctness. No author code/result has been inspected at this stage.

The fine reference observes first-switch acceleration jump 1.4829488066708116, surviving second-switch residual (-0.9326096118732802, 0.8882555146817298), and final composed state (0.3891991152070571, -0.10063863122901345). These are numerical ODE-reference results, not exact closed-form literals or animation measurements. Both lost-state components materially discriminate the raw-target-only interrupted rebase. The full coarse/fine tables remain available for later comparison under the protocol's already frozen tolerances.
