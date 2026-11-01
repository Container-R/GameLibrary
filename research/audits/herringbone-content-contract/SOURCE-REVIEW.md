# Herringbone tile contracts — independent source review

2026-11-01 UTC. **ACCEPT the bounded mechanism**, not a general connectivity guarantee. Gate reviewed: `19ac64e1f2e41603539f3af75d936cb5592c41b9e6738836f225873a79d8d7fb`.

## Primary source identity and locators

Independently opened Sean Barrett's original [2011 article](https://nothings.org/gamedev/herringbone/herringbone_tiles.html) and [2014 follow-up](https://nothings.org/gamedev/herringbone/more_herringbone_tiles.html). The former labels itself unfinished, originally written in 2010, dated 2011-10-22; the latter is dated 2014-07-07. Read text sections Wang Tiles / Herringbone Tiles and follow-up Colored Corners / Authoring tile-map tiles / the opening finite-boundary qualification in §3. No pictures or generated-map quality were inspected.

Fetched official stb commit `003501f6d7a8668ce8b6d875e34dd97ad0d5d5b5`, independently confirmed its 2026-10-23T01:51:27Z commit timestamp. The header identifies v0.7 and its history records 2019-03-04; these dates describe different identities.

Read [stb_herringbone_wang_tile.h](https://github.com/nothings/stb/blob/003501f6d7a8668ce8b6d875e34dd97ad0d5d5b5/stb_herringbone_wang_tile.h): 16–29 and 172–187 API scope; 364–427 shared enumeration; 430–497 template-size calculation/check; 594–640 selection; 841–936 image extraction; 1173–1219 header writing. This is the concrete source chain, not an inference from the library name.

## Mechanism accepted

Template metadata plus the enumerated rectangle position assigns a…f; parse callbacks store those values and copy RGB content. The selector checks already-known constraints (negative values are unspecified), chooses a matching tile and updates the constraint slots. No-match can return null. It does not classify copied RGB as a walkable interface. Thus preserving a valid template's metadata/layout while changing only one tile's payload does not cause a corresponding semantic constraint reclassification in these paths.

This is stronger than a generic “validity is not correctness” warning: the handoff connects a specific metadata/enumeration producer, pixel payload consumer and six-field compatibility comparison. Do not describe the template parser as accepting arbitrary images, validating all malformed inputs, or reading visible edge-color decoration to derive semantic labels. The proposed example assumes valid structure and allocation; no load was executed.

## Historical corrections and scope

The 2014 text explicitly revises the earlier universal-minimum implication and distinguishes edge/corner classes; preserve that correction rather than calling 128 a required minimum. Its authoring discussion supports shared-interface content responsibility, not this project's actual semantic definition. Its finite-crop caveat prevents transferring an infinite-plane connectivity claim to every output rectangle. The original 2011 example did not actually enforce constraints, so it must not be presented as a measured instance of the proposed edge-constrained workflow.

The proposed wall edit is an original hypothetical, not a loaded artifact or Noita bug. Even a local mismatch does not necessarily disconnect a whole map, and RGB is not automatically collision data. Separate internal connectivity, interface compatibility and finite-map reachability. Noita's actual integration/version remains unknown. Current solutions/source-notes search found no existing herringbone mechanism note; the question is distinct from simulation-thread ownership.

No material correction required to the bounded gate. Publish a concise standalone safe note with exact producer/selector responsibilities; no general solver, seam-quality, rotation, safety or performance claims. No runtime, assets, images, legacy edits or remote writes occurred.
