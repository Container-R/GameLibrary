# Addressables dependency-depth gate — independent review

2026-11-01 UTC. **ACCEPT a short integrated §3.1 in SOL-ENGINE-002**, with a dated addition to its existing source-reading record; a new standalone note or indexed article would unnecessarily split the same workflow. Gate SHA256 `18fa5842cde9f3b949062172956bbc98646863d48c520426d2495000d8d3ebfa`.

## Independently inspected scope

Read the complete existing solution and companion source note. The solution already separates baseline selection, restrictions, output catalog and old-client acceptance, but only briefly mentions dependencies. Its source record honestly limits the earlier S4 dependency reading. Both selected files contain source-only workflow material rather than local execution identities; no other legacy files need modification for this unit.

Opened the official [Content update examples](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-examples.html#content-update-dependencies), including HTML text/tables 272–387, and [Unique Bundle IDs setting](https://docs.unity3d.com/Packages/com.unity.addressables@1.21/manual/content-update-build-settings.html#unique-bundle-ids-setting), 163–172. Returned metadata/title identifies Addressables 1.21.21; 2024-05-16 is the documentation generator date, not a verified package release date. These version-series pages are not immutable implementation pins. No figures or installed Inspector were inspected.

## Supported distinction

S4's hypothetical Local_Static examples explicitly move indirect consumers into content_update_group when their dependency changes, including a shared dependency and an asset-to-asset chain. This supports rejecting “the consumer file was not edited, therefore it is outside the update” for those examples. It does not document a universal closure implementation for arbitrary cycles, implicit imports or every group setting.

S2 separately describes Unique Bundle IDs allowing changed and original bundles to coexist in memory and requiring referencing-asset bundles to rebuild. This is a bundle identity/rebuild consequence, not the same operation as restriction-check asset migration. Neither source converts a count of affected assets into bundle count, bytes or actual user downloads. Packing, selected references, requested assets and cache state remain separate inputs.

## Integration controls

- Add one concise §3.1 after static-group semantics: edited dependency → consumers requiring inspection → restriction-check group membership → built bundle/catalog references. Keep the proposed equipment example explicitly unexecuted, without fabricated resulting groups or file counts.
- Retain current source-backed status and all unexecuted build/hosting/client limits. Existing baseline-selection and cache-fallback qualifications are not changed by this deeper reading.
- Preserve the 2026-10-31 S4 row and its partial-reading statement verbatim as historical scope. Append a new 2026-11-01 scope entry covering the newly read dependency section and table range, plus the S2 re-read. Do not retroactively claim the first review covered the full dependency section.
- Update the article's reading-date language additively if needed so it does not falsely label the new section as reviewed only on 2026-10-31. No need to copy full vendor tables or expand into an implementation audit.

No material gate correction required. No Unity, build, download measurement, client or native execution occurred; no author, repository or remote files were edited by this review.
