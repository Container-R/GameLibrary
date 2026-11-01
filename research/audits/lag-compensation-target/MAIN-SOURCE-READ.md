# Main reading: accepted target and history sample

2026-11-01. ValveSoftware/source-sdk-2013 fixed commit `be57e3d01ac7d7aa6a2cacbfef187c0b46616db0`, resolved directly through the official GitHub commit API. Its committer date is 2026-10-10; the commit’s item-schema change does not imply lag-compensation code was authored on that date. No current commercial-game applicability is inferred.

Direct main reads:
- `src/game/server/player_lagcompensation.cpp`: lines 1–105, 235–700 and 768–850. Blob `020af6fccb54479cb57f883d55d645bbfe5063ea`.
- `src/game/shared/shareddefs.h`: lines 1–24, including tick conversions. Blob `dc62e583af8fa18cc6ef245c1ae11d87c7e67df3`.
- `src/game/server/hl2mp/hl2mp_player.cpp`: lines 640–659, Start/Finish around base FireBullets call. Blob `9457928a0c5d41bacafb16177fe6be2c7a95b757`.

Fixed source entry: https://github.com/ValveSoftware/source-sdk-2013/blob/be57e3d01ac7d7aa6a2cacbfef187c0b46616db0/src/game/server/player_lagcompensation.cpp .

Target-time selection and position-sampling branches were inspected directly, not inferred from the paper abstract. The proposed two-command example uses ideal arithmetic away from rounding and threshold boundaries; it is not an execution. `GetLatency(FLOW_OUTGOING)` is retained as the code-read quantity, without replacing it with assumed RTT/2. Recording inserts advancing simulation timestamps at the head; position interpolation is conditional on bracketing valid records. Empty history and an unavailable lower bracket are different paths. The retention threshold is integer-valued in this source, so no exact continuous buffer-duration claim is accepted.

Pre-draft integration checks: optional fix-stuck recursion deliberately bypasses the outer player eligibility predicate; it cannot be described as only moving the outer-selected set. The finite position example excludes that optional branch. Candidate position is not automatically actual installed position because later checks and an origin-change epsilon exist. Animation and restoration have separate rules. No full-world rollback, current-door obstruction, hit result, fairness, exploit or complete shutdown guarantee is inferred from the manager and wrapper.

The discovery worker reported one original-paper URL access returning 403 and stopped that path; main did not retry or read a mirror. No compilation, model run, network exchange or game execution was performed. No runtime archive was used as mechanism evidence; separate archive consistency checks are recorded in the integration run. No source code bulk is included in the proposed publication.

The complete frozen note `99e12a7cdb9605a4f6908b698689557274024d6963f601a6a6c0bff6d1ed921f` was read after drafting. It includes the oldest-record fallback, optional recursive filter bypass and candidate-versus-hit distinction. The main integrator found no blocking mismatch in the stated two-command and two-record example. Full-file source reading is the author's scope; the narrower main ranges above are retained rather than upgraded to a full-file claim.
