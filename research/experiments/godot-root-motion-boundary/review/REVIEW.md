# Independent bounded native root-motion acceptance

Accepted 2026-10-31 21:34 UTC. First read actual canonical-rig-stage article verification_method and old root-motion README; baseline.json records their hashes. Existing evidence was four Python 2D geometry tests, not prior native root motion. New native evidence must be dated and scoped separately; Unity Rig dependency worksheet remains unexecuted.

Read frozen contract before copying code. Exact runner `d3efc79c6961abfe0d4ff591a30a84a97921a900f77d815909824ebd76d3f7e4`, GDScript `128f13687cf4b150707ad23316f1dcc15a8e578d66f1f3d1c16eae5379deea50`, contract `d447aadbd25f21c8e347fdec65e81084bd3b3e9be3a65dbc3164fd3625ac6f55` copied into fixture/. Literal prospective oracle retained before execution.

Executed `python fixture/run.py <absolute review-directory>/evidence` using full source path. New UUID `8f7817ac-8c38-44ed-80a9-b861b168ac3d`: exactly **two behavior processes plus one version command**. All exit 0; current behavior stderr empty. No extra playback, negative injection, optimized fixture or timeout experiment was run.

Independent check.py parses raw RESULT_JSON, verifies parsed associations/source and output hashes, same installed binary hash and actual configuration/call order. Its numeric oracle converts quaternion to rotation matrix (sign invariant), checks unit norm/finite values and compares literal Y-axis rotations, rather than importing author checks. Position/tolerance, normal-pose bone movement, extracted bone/actor identity, repeated nonzero reads, smaller next-evaluation delta and all three explicitly applied receiver outcomes pass. Full observed commands/results remain under evidence/; check.json records exact hashes.

Code inspection confirms manual-only AnimationTree and AnimationPlayer setup, no player.play call, one generated bone, fixed original keys, no await/idle advancement inside the controlled sequence. Receivers translate in parent coordinates and compose same-axis quaternion increments; this is not a general rigid-motion integration algorithm, collision movement, foot-planting or IK result. Calls array records advance sites, not an independent instrumentation count of every getter. Getter calls and receiver application loops are directly visible in source.

Independently reopened Godot 4.6 AnimationMixer and AnimationTree documentation: MANUAL requires advance; linked player supplies animation resources while tree controls playback. Same binary SHA f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3 does not authenticate public source tag or official build provenance.

Runner allocates a new UUID without overwriting old invocations, writes STARTED before engine lookup, and sets PASS only after exit/data/source checks. Handled errors record FAIL, command outputs, and timeout partial output; source-hash errors before initial receipt, process kill or filesystem failure are not covered by a universal receipt guarantee. No assert-dependent acceptance exists, but optimized execution was not tested. Timeout behavior was read, not fault-injected. Source hashes are consistency records, not protection against hostile concurrent modification.

No material issue found; no author/main/remote modifications.
