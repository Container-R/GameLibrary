# Pre-native code review

2026-10-31 22:43 UTC. Initial source manifest SHA256 `213d74ed8351521f8096b83a3af93e7b164c151f3be4cd9851cf60cd28194daf`; exact reviewed Python sources and manifest retained in `initial-code/`. No native calls or CDLL loads occurred. Pure imports exercised `validate_report` only; raw constructed records and actual accepted classifications are in `initial-code-false-acceptance.json`.

## Hold before native execution

1. Consumer permits `ENUMERATION_FAILED` without a native call, ABI failure without ABI evidence, and successful zero enumeration with wrong ABI/loader metadata. Categories require phase-specific validation, not merely matching a supplied category string.
2. `destroy` result must be exactly `None`; current trace validator accepts integers. Constructed integer 123 still accepted as completed zero enumeration.
3. Parent independently identified missing environment/argv invariants, startup terminal handling, post-run source/loader identity and loading the resolved hashed library path. These must be checked in the revision; archive consistency is not execution authentication.
4. Timeout loop stops when leader exits after TERM, potentially skipping KILL for owned descendants. Record/handle the distinction between leader completion and remaining process group; no actual timeout was exercised here.

Child structure layout, fixed C signatures, binding all symbols before creation, initial zero fields, bounded array allocation, bounds check before array indexing, SUCCESS/INCOMPLETE distinction, and finally destruction after successful nonnull creation are consistent with the gate by source inspection. This is not native outcome evidence or final code acceptance.
