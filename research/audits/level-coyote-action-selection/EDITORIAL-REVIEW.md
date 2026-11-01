# Level-designer coyote-time integration — editorial review

2026-11-01 UTC. Reviewed complete staged ROLE-DESIGN-001 SHA256 `bba2a1938587e9309f9c7bb3c30edb97f4631d0f088d232b7fa270177ed5a1e0`, its diff from the prior role, SOURCE-REVIEW and MAIN-SOURCE-READ. Independently reopened Double Fine's original text at Metrics, Jump Metrics Tool and Coyote Time. No runtime bundles, images, videos, controller execution, model or tests were inspected/run; no stage/legacy/remote edits.

## Verdict and narrow wording request

Accept the source mechanism and original matrix, with a small clarity recommendation: replace wording equivalent to “check recent data, then let the current mode respond” with “give recent data an opportunity to consume the input before directly routing it to the current mode.” The source establishes priority, not that an already-consumed input is always also dispatched to the current mode. Apply the same clarification to the dated source addendum if needed; no new dispatch algorithm should be claimed.

## Substantive findings

The source supports conditional prior-mode action selection with duration/speed/action data. The role does not turn it into an unconditional rule for every transition or all airborne inputs. It distinguishes the selected action from a later resource balance, permitted aerial action, trajectory, collision and successful crossing. Historical tuning values are acknowledged as present but deliberately not reused as universal settings.

The original three-row matrix asks a useful level-design question: is acceptance about reaching a location or completing an intended action sequence? It requires action identity rather than treating button counts or airborne status as an adequate proxy. Its unknown resource and landing columns prevent inventing extra jumps, bypasses or player benefits. This is concrete added scope beyond the old capability/layout record, not a controller tutorial or generic version checklist.

The integration preserves original job/case attributions, four-source inventory and initial 2026-10-31 reading history; 2026-11-01 Coyote Time is a newly read section of existing L3, not another independent source. The added matrix is clearly original and unexecuted. No draft instructions or private runtime metadata remain in the visible whole-file context. Source-derived recap remains compact across the original role and added section. Pending only the small priority wording decision and exact final hash.

## Final acceptance addendum

ACCEPT final full article SHA256 `31421f0edc09fa505a05381fa04c83e354479ace36c6dae12ec5b652aa823da0`. Read the clarified paragraph and dated addendum. Reversing only those two priority phrasings reproduces initial reviewed SHA256 `bba2a1938587e9309f9c7bb3c30edb97f4631d0f088d232b7fa270177ed5a1e0`. This prepublication correction removes a possible implication of unconditional subsequent dispatch; it adds no new implementation claim. No further correction requested.
