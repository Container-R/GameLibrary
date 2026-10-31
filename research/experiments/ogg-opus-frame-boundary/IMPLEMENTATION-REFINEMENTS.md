# Pre-native implementation review refinements

2026-10-31. Protocol `4024d6fd…` remains unchanged. Parent approved refinements separately. **No version query, encode or decode has yet run for this fixture.**

Initial code snapshot is retained under `historical-pre-native-review/` (runner `5aa9277e…`, consumer `818983a1…`). Independent reviewer retained a second copy and pure synthetic false-acceptance evidence at `research-drafts/deep-qa/music-codec/`: its fabricated archive is not an encoder result. Four initial-consumer defects involved selected library identity, environment association, UUID association and unbound parsed metadata. They do not imply any actual media result.

Current pre-native changes:
- Check generated original PCM formula/length before tool entry; validate bounded encoded subset immediately after encode and before launching decode.
- Bind all selected library/binary identities, protocol/helper pins, source-after manifest, process argv/status/raw streams/UTC times and UUID/environment association.
- Independent consumer validates actual page/packet/header metadata, CRC and TOC duration relationships; duplicate JSON keys and Boolean/float substitutions rejected. Bounded single-member gzip reconstruction and chunk bounds prevent unrestricted archive decompression.
- Feed the unchanged five-key helper only explicit base `PATH=/usr/bin:/bin`, `LANG=C`, `LC_ALL=C`, rather than inherited loader variables. This is not a sandbox or proof of all dynamic code provenance.
- Start each process in a new session. On 20-second timeout send SIGKILL to its process group and attempt a further bounded 5-second communicate; preserve partial streams and cleanup failures. This does not contain deliberately escaped descendants or guarantee all cleanup succeeds.

Pure synthetic tests exercise framing, reference polynomial CRC, header/layout/trim rejection, an explicit continued Tags page, and type/FAIL receipt rejection. Their payload bytes are not valid entropy-coded media and are never decoded. Normal and optimized tests use explicit production validation (not Python assertions); `unittest` assertions are test oracles and still execute under `-O`.

Static archive consistency is not execution authentication. Recorded selected hashes are not complete authenticated upstream provenance. Actual native execution remains blocked pending final code review acceptance.
