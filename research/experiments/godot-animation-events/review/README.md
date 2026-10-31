# Independent animation-event boundary review

2026-10-31 15:17 UTC. Copied only frozen fixture main.gd, main.tscn, project.godot, run.py into fixture/ and ran `python3 research-drafts/deep-qa/animation-events/fixture/run.py`. Six fresh-process cases passed; each run uses separate temporary HOME/XDG paths. Author original files/results were not modified. No installation or GitHub write.

Independent check: `python3 research-drafts/deep-qa/animation-events/independent_check.py research-drafts/deep-qa/animation-events/fixture/results` reads raw CONFIG/TRACE/SIGNAL lines, not author passsummary. It verifies cumulative method emission order at every trace, actual sampled float and playback positions, full self-reported version hash, manual/immediate/nonloop configuration, explicit finished signal count, and clean stderr. Output in independent-output.json. Results: single-key seek calls twice versus advance once; two-key seekB,B versus advanceA,B; exactseek update_only suppresses method without suppressing sampled0.5; cross final sample1, finish0 for seek and1 for advance.

This is an observation-based regression after the original hypothesis failed, not proof of that hypothesis. Historical initial failed oracle is retained separately by author, as is corrected-four history. No engine bug assertion. No claim of damage, animation visual render, physics, deferred timing, looping, blends, other platforms or other engines.

## Identity and source limits

Binary SHA256 f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3; self-reported4.6.3.stable.official.7d41c59c4/full7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3. Same installed binary repeat, not independent release provenance authentication.

Read official4.6 seek docs https://docs.godotengine.org/en/4.6/classes/class_animationplayer.html#class-animationplayer-method-seek (access2026-10-31): interval skipping, update_only and no finish on seek documented. Do not convert interval-skipping wording into “seek never invokes a method.”

Independently fetched GitHub https://github.com/godotengine/godot/blob/35e80b3a8822a9df9be390814b62f44c0a9c69e8/scene/animation/animation_mixer.cpp via plugin. TYPE_METHOD branch lines1650–1677 distinguishes seeked key selection from normal interval iteration, suppresses update_only. FIND_MODE_NEAREST name alone does not establish closest-distance semantics. Tag/source identity differs from runtime self-reported hash; parent/author report latter commit lookup422. I did not retry that failed lookup. Tagged source is comparison only, not verified exact binary source. Author README had old line anchor1557–1582; correction requested.

## Frozen fixture hashes

- main.gd90c1eedc6bcfa282be945ad9d0b9aeb30c5a5371da241d7e8df582756dc61343
- main.tscnf85872f76bad18c324d2898596b8fd87cfa0d56e50fb5762379411f94f40097c
- project.godotf03cbe1910b102816a360cb1fed33f8c223c34ae15f079d9c9a55bfcc063f052
- run.pyc898d637a1ac9ead8a8d564278defe3af4ac2e6766a2930dd95b28f4897098cf

No remaining runtime-result mismatch. Final source locator correction pending; publication gate unchanged.

15:18 UTC addendum: author corrected README anchor to1650–1677; independently confirmed final text. Runtime files unchanged. No remaining material issue within declared same-binary scope; suitable for local integration, not remote publication authorization.

## Archived layout

The historical commands above identify the actual reviewer workspace. This archive stores reviewer results beside `independent_check.py`, without duplicating the current fixture sources. From this directory run `python3 independent_check.py results` to check the saved traces; this does not rerun the engine. To rerun independently, copy the four frozen fixture source files into a separate directory and run its `run.py`, preserving old results first.
