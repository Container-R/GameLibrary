# Noita scheduling — independent source review

2026-11-01 UTC. **ACCEPT as a narrow historical developer-testimony case**, not an implementation or concurrency proof. Reviewed gate SHA256 `727aa793ead4984d0b34b4eaad7bb06686f9e70e05d221b8d73a4a8bb3bca653`.

## Direct source verification

Opened the original [80 Level interview](https://80.lv/articles/noita-a-game-based-on-falling-sand-simulation). Its header dates publication 5 April 2019 and names interviewer Daria Loginova; Introduction identifies the first-person speaker as Petri Purho of Nolla Games. This is firsthand developer testimony hosted by a publisher, not studio-hosted source code. The Distribution section describes a then-future early-access release; current product behavior cannot be inferred.

Selected text in **Optimization of the Falling Sand Simulation**, paragraphs corresponding to current extraction lines 126–131, supports the gate's finite capsule: 64×64 chunks and dirty rectangles; cross-chunk repeated-update concerns; four rounds of an alternating scheme; stated movement allowance extending 32 pixels in cardinal directions. The exclusive-update explanation is the developer's claim, not independently established race freedom. The source does not supply a complete schedule or memory-access specification.

Also opened the [official GDC session page](https://www.gdcvault.com/play/1025695/Exploring-the-Tech-and-Design), confirming Petri Purho / Nolla Games / GDC 2019. Only metadata was used from that page. No video, screenshots, diagrams or graphical movement boundaries were inspected.

## Novelty and constraints

Read the existing fixed-step article's actual verification method and searched current solutions, case-studies and source-notes for Noita/Nolla/Purho/falling-sand terms; no matching case was found. Existing finite timing, business-policy and callback evidence is not spatial partition/parallel ownership evidence. The proposed distinction—work selection versus ownership of updates—therefore adds a concrete mechanism-level handoff, rather than another generic fixed-step explanation.

The future movement-rule scenario is acceptable only as an original hypothetical. A larger movement or exchange range can invalidate a previously assumed access envelope; this is not a reported Noita change or bug. A dirty region can be accurate while still saying nothing sufficient about which thread may touch shared locations.

Do not turn “64 / 32 / four rounds” into executable checkerboard pseudocode. Exact group coordinates, diagonal/corner access, read sets, barriers, dirty-mark ownership, auxiliary shared state and cross-round update semantics are unspecified here. Single-writer reasoning alone is not a complete read/write-race, determinism or serial-equivalence proof. Likewise the interview's synchronization-cost opinion is not a measured universal performance rule.

No material gate correction required. For publication, keep source recap compact and explicitly attributed; retain original rule-author → scheduler-maintainer questions, not alleged studio process. Publish a standalone safe note without legacy article rewrites or runtime metadata. No native/model execution or remote write occurred.

## Authorized addendum — finite access-set counterexample

2026-11-01 UTC. Prior review SHA256 `82b43848da4b89b7c83e78ac399b20931060369df5d10c138dba5a00008496c0` retained here for identity. **Accept the original set argument**, with x and y denoting distinct mutable storage slots shared by both task descriptions. Let R_A={x}, W_A={y}, R_B={y}, W_B={x}. Then W_A∩W_B=∅, but R_A∩W_B={x} and R_B∩W_A={y}. Thus disjoint write sets alone do not establish that every read/write access pair is disjoint.

This is a set-theoretic insufficiency witness, not an executed schedule, observed data race, predicted output or description of Noita internals. It does not prove failure in the presence of synchronization or other ordering. Reads from a physically separate immutable old buffer would denote different storage locations and constitute a different model; reusing x/y names must not hide that change. No runtime or source implementation claim is added.
