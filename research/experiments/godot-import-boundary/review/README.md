# Independent review: clean import metadata boundary

2026-10-31 independent frozen-copy review of `research-drafts/godot-import-boundary/`. Copied only runner and seed to `fixture/`; no author output or cache copied, original artifacts unchanged.

## Verdict

**PASS; no material blocker for the narrow import-configuration claim.** Independently ran the exact sequence: default baseline import, configured baseline clean reimport, baseline probe; kept/omitted clean imports and separate probes. Four real editor import processes and three real resource/scene probes passed. No additional parameter matrix.

`fixture/results/` preserves raw logs, per-invocation command/environment, generated sidecars, configured inputs, initial file manifests and loaded-resource JSON. `review-checks.json` records extra review assertions. `runner-output.txt` records completion. `optimized-rejection.txt` confirms -O guard.

## Evidence checks

- Five source hashes and binary SHA256 match the author's frozen manifest. After rerun, original source hashes still match; no original writes.
- Source SVG explicitly defines16×8; no external asset/font/network dependence. Seed scene references texture by source path, not a UID annotation.
- First baseline sidecar came from actual importer; before reimport its only text change is svg/scale1.0→2.0. No manually invented UID/remap.
- Both test folders lacked `.godot` immediately before import by executable assertions. Initial manifest set difference is exactly `asset.svg.import`; all common files, including script UID, have equal content hashes. Separate HOME/XDG environments start empty.
- Actual import logs mention processing `asset.svg`; generated `.ctex` exists. Probes independently read actual ResourceLoader texture dimensions and instantiated Sprite2D.texture dimensions, not just sidecar scale.
- Baseline/kept are32×16; omitted is16×8. All three resources load successfully, are CompressedTexture2D, and scene/direct textures are the same loaded resource.
- Resource paths and registered UID path are `res://asset.svg`; exact scene dependencies are `res://probe.gd` and `res://asset.svg`. This validates the path-based fixture, not UID-only scene references or rename recovery.
- This batch observed the same UID across baseline/kept/omitted despite different dimensions. That equality is recorded, not asserted as a universal importer property. Kept retains baseline UID as intended.

## Interpretation and limits

The result isolates missing sidecar parameters, not engine load failure. It supports keeping asset-specific import configuration while rebuilding generated cache for this SVG and exact binary. It does not establish all asset metadata portability, byte-identical cache reproducibility, cross-version/cross-machine behavior, source-control/LFS transport, exports, GPU pixel quality, script-UID-loss consequences or UID fallback behavior.

The runner records Godot4.6.3 and binary digest rather than claiming all future binaries behave identically. Baseline editor may generate additional legitimate input metadata; configured snapshot preserves it equally in both cases. Temporary `.godot` removal is confined to generated experiment workspace.

## Primary source cross-check

Accessed2026-10-31:

- [Godot4.6 Import process / Files generated](https://docs.godotengine.org/en/4.6/tutorials/assets_pipeline/import_process.html): separates asset-side configuration from regenerable `.godot/imported` outputs and recommends preserving sidecars.
- [ResourceImporterTexture.svg/scale](https://docs.godotengine.org/en/4.6/classes/class_resourceimportertexture.html#class-resourceimportertexture-property-svg-scale): scale1.0 uses original SVG design size; higher values increase imported image size.

These support the scoped interpretation; independently observed sizes remain execution evidence rather than borrowed documentation assertions.

## Provenance clarification — 2026-10-31

The version string is the local executable’s self-report. Matching fixture-source and executable hashes establish consistency for these runs, not official release authentication or exact engine-source correspondence. Original observations and raw logs remain unchanged. See the [shared evidence note](../../../source-notes/godot-runtime-provenance.md).
