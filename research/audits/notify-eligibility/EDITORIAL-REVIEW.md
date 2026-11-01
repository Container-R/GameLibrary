# Unreal Notify eligibility — final note editorial review

2026-11-01 UTC. **ACCEPT unchanged.** Reviewed the complete self-contained note against the independently read Epic 5.6 originals and source review.

Accepted note SHA256: `0f94ceeb4a852c7f46e05df20a2c386152205fa1ff648741c99d61845eb6ce3e`.

Intended destination: `research/source-notes/unreal-notify-eligibility-authority.md`.

## Acceptance checks

- The hypothetical attack explicitly requires the sole request path to execute in the server-local handler, without client forwarding, RPC or another path. The note expressly preserves client-origin/server-validation architectures outside this premise.
- The example concerns a custom Notify in an ordinary Animation Sequence. Montage Queued/Branching Point discussion is separate and supplies no implied filter bypass, worker-thread contract, authority or exactly-once guarantee.
- Disabled dedicated-server triggering is attributed to the documented property, not an inspected dispatch implementation or a measured lost hit. Enabling it removes only that exclusion, not all evaluation or rule prerequisites.
- The generated API's Experimental status, version-selected URLs and unknown patch/publication identity are explicit. Constructor signatures are not treated as project defaults; the AnimTypes.h locator is not represented as a source-code inspection.
- The four-row receiving checklist and failure scenario are original and unexecuted. Callback receipt, request, validation, collision and damage remain separate evidence questions. No universal ban on animation-driven gameplay or automatic timer replacement is proposed.
- Existing Godot and fixed-step evidence is not transferred to Unreal. The linked article's verification scope remains unchanged. Historical 4.27 discovery and inaccessible guessed implementation URL do not supply missing 5.6 guarantees.

No material correction needed. The review accepts this note alone, not an additional article or runtime result. No engine, network, model, listening, image inspection or experiment performed.
