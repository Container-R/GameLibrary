# FMOD observation-layer source review

2026-11-01 UTC. **ACCEPT the narrow source-only supplement gate**, SHA256 `b1e470e565511d13e404708523c94b4ba4171263179e38a385730b972eb99eae`. No material correction required.

## Originals independently read

- [Core API Managing Resources](https://www.fmod.com/docs/2.04/api/managing-resources-in-the-core-api.html), §§9.1.5–9.1.7, especially “Interaction with the Core API Virtual Voice System” (retrieved lines 167–168). The explicit counterexample supports event-level false coexisting with partially or wholly virtual underlying channels. Sections 9.1.5/9.1.6 distinguish permanently stolen Core handles from retained virtual channels and describe default resumption versus the Core start-from-beginning flag. The post-play sorting advice locates its channel query after System::update, not an arbitrary atomic Studio snapshot.
- [Studio Advanced Topics](https://www.fmod.com/docs/2.04/studio/advanced-topics.html), §§16.4.1–16.4.2 (199–215): distinguishes stopping, None refusing additional playback and event-only Virtualize. Virtualization retains advancing playback/behavior while muting the master track. Its Core-channel paragraph supports partial event silence. Do not generalize the Core guide's “stealing on” shorthand to all these Studio modes.
- [EventInstance reference](https://www.fmod.com/docs/2.04/api/studio-api-eventinstance.html#studio_eventinstance_isvirtual), isVirtual (975–1011), START_FAILED (1963–1964): query scope is event polyphony virtualization; rejected starts omit STARTING/STARTED/STOPPED in the described case. Rejection is not a paused instance waiting to resume.

All three page footers actually read identify **2.04.00 (2026-09-29)**. This is a documentation label, not observed installed behavior or independently established release chronology. These are version-series URLs, not immutable sources. An incorrect guessed Core URL failed; the exact page above subsequently opened successfully. No Wwise evidence or equivalence is claimed.

## Existing evidence and distinct contribution

Read the current music transition contract (SHA256 `2eb0620deb8f97e95bc5d4ccce31395b0b1f8cf49616bf0279b9467e0431d13b`) and critical-sound information contract (`f504bd973ebb5814e8c31f6aa1a79ad5902808ac4bd2688c9efcb2fd97ea0691`). Their respective fake-port lifecycle tests and static semantic-coverage analysis do not observe FMOD channel virtualization. Start rejection and event-versus-heard distinctions already exist; repeat those only as context.

The useful addition is the specific false inference between API layers: successful event nonvirtual status cannot establish cue-bearing channel nonvirtual status. This is more concrete than another generic warning that playback is not perception.

## Drafting boundaries

Retain successful-query/error handling, identity and observation time. Separate samples are not an atomic cross-layer state. An invalid handle alone does not diagnose capacity stealing without further context; the gate correctly conditions that row on known stealing.

The opening-plus-tail scenario is a conditional original example: retained valid channel, remaining content and stated return policy. It is not an observed missing cue. Do not infer guaranteed later reactivation, replay usefulness, sample accuracy, or a whole Studio event restart from a Core flag. A real channel still does not certify delivery or listener understanding. Keep inaccessible Wwise material and broad tuning recommendations outside the supplement.

No native calls, listening, asset inspection, implementation, experiments or publication performed.
