# Generated Ogg Opus reader source gate — no media execution

2026-10-31. Follow-up to triage.md, still **source/capability only**, not frozen execution protocol. No PCM generation, encoding, decoding or codec API calls occurred. No main-tree edits.

## Sources read and exact scope

- [RFC 7845](https://www.rfc-editor.org/rfc/rfc7845.html), April 2016, T. Terriberry / R. Lee / R. Giles: §3 header placement, §4, §4.2–4.5, §5.1 and §5.2 comment bounds/padding. Read initial nonzero-position rules, EOS trimming, OpusHead fields and the distinction between input-rate metadata and output clock. Granules count per-channel samples at48 kHz; stereo does not double that count. Exact pre-skip is a header value, not a fixed codec constant. Seeking pre-roll is separate and excluded.
- [RFC 3533](https://www.rfc-editor.org/rfc/rfc3533.html), May 2003, S. Pfeiffer; **Informational**, not itself Standards Track: §5 segmentation and §6 page format. Read length bounds, little-endian fields, BOS/EOS/continuation flags, serial/sequence and checksum coverage. Lacing255 continues; a smaller value completes, including zero termination for a multiple-of255 packet. No completed packet uses the special granule -1.
- [Xiph original Ogg framing documentation](https://xiph.org/ogg/doc/framing.html), accessed2026-10-31, publication date unknown: Packet segmentation, Packets spanning pages, page checksum. It specifies direct CRC polynomial0x04c11db7, initial value0 and final XOR0 over the whole page with checksum bytes zeroed. This fills the initialization detail absent from the inspected RFC3533 paragraph. CRC is integrity checking, not authenticity.
- [RFC 6716](https://www.rfc-editor.org/rfc/rfc6716.html), September2012, JM. Valin / K. Vos / T. Terriberry: §3.1 Table2, count-code meanings, §3.2.1 frame-size bounds and §3.2.2 code0. TOC configuration identifies frame duration; code0 has one frame. A requested encoder option is not evidence that actual packet TOCs meet it.

No full codec or entropy decoder is proposed. Source paragraphs and diagrams are not copied into the archive.

## Bounded reader proposal

The next protocol can constrain acceptance to this **one freshly generated single serial Ogg Opus stream**, <=1 MiB, <=1024 pages/packets, header metadata bounded to the file. These caps are original fixture limits, not format maxima. Supported output subset:

1. Walk pages at exact computed offsets, not by searching inside payload for magic. Require OggS/version0, complete27-byte base header, complete lacing table/body, no trailing bytes, known flag bits, one serial, contiguous page sequence starting0, exactly first-page BOS and final-page EOS. Reject extra chained/multiplexed streams as unsupported, not universally invalid Ogg.
2. Calculate every page CRC with checksum field zero; verify it before trusting page contents. Do not use ZIP's differently conditioned CRC32 as a substitute.
3. Reassemble packets using lacing, retaining a pending packet across pages. Continuation flag must agree with pending state; a terminal255 leaves pending data, a value<255 completes even when zero. EOF/EOS must not leave unfinished data. No resynchronization or recovery. Record actual continuation occurrences; if none occur, structural code support is not claimed as runtime continuation coverage.
4. Require first packet exactly the supported19-byte version1 OpusHead with outputchannels2, mappingfamily0, gain0 and inputrate48000. Read pre-skip little-endian, require positive for the proposed counterexample, **do not require312**. Require a separately completed OpusTags header before audio, checking vendor/comment lengths within packet bounds. Other valid header variants are outside this fixture, not necessarily malformed.
5. Accept audio packets only in RFC6716 **code0** subset, bounded nonempty frame payload <=1275 bytes. Derive duration from actual TOC config Table2 and require20 ms/960 output frames at48 kHz for every accepted packet. Do not demand stereo TOC flag just because output channels are2: encoded channel mode can differ from output layout. If code1/2/3 or another duration occurs, preserve the stream and stop this bounded capability gate; do not silently implement a wider parser or multiply packet count blindly.
6. Require the first completed audio page is **not EOS** and its granule equals the sum of decoded durations of all audio packets completed so far. This anchors initial granule offset to0 rather than assuming that a source labeled “new” cannot contain a nonzero offset. Require each subsequent non-EOS audio page's granule equals cumulative completed-packet frames. Pages with no completed packet require -1; header pages follow header-zero rules.
7. For EOS, require a completed final packet, increasing/nonnegative final granule consistent with prior completed-page granule, and `0 <= total_packet_frames - final_granule <= final_packet_frames`. Record this difference as tail trim; require positive trim only if the eventual protocol elects to establish both front and tail counterexamples. The independent presented-frame oracle is `final_granule - pre_skip == 93659`, and actual full decoded PCM length must independently equal93659 frames. Require finalgranule>=preskip. Whole-file bytes/channel components/packet counts are distinct units.

The metadata-to-count relation above is restricted to the verified zero-initial-offset stream. A stream satisfying this reader is not certified fully conformant Opus: payload decodability is separately exercised by the actual existing decoder if later authorized. No waveform byte equality, artifact-free joins, random access or latency claim follows from matching counts.

## Read-only dependency identity

`dependencies.stdout` retains ldd for both executables, resolved file paths and selected hashes. `dependencies.stderr` preserves failed dpkg-query lookups: package registry did **not** provide versions for the named libraries. Do not invent a libopus release number from its soname.

| Observed resolved file | SHA256 |
|---|---|
| /usr/lib/x86_64-linux-gnu/libopus.so.0.10.1 | 621e97f23655dbf2727873b7717e3b65ae8c734f84a0848f88c21edb95202357 |
| /usr/lib/x86_64-linux-gnu/libavcodec.so.61.19.101 | c01e80460c07b27883a61c53e549755b9ff052071a83f4912ff285168719219d |
| /usr/lib/x86_64-linux-gnu/libavformat.so.61.7.103 | 8cde31eb30ee1ccc7d3758f60fe46dc9f342c4c9fef98cef81ecf7b681b78eeb |
| /usr/lib/x86_64-linux-gnu/libswresample.so.5.3.100 | de57f190891cf107b9c2fb51fc7d45c02c6c652f6fc7992a3c26d1f16f371674 |
| /usr/lib/x86_64-linux-gnu/libavutil.so.59.39.100 | 6c463f7e033438989533aea3c35e4c9a98fd6b0a637ddb8529733c0f3db1850a |

This is observed loader resolution and selected local-byte identity, not exact upstream build provenance, proof of every actually executed instruction, or a complete supply-chain audit. FFmpeg/ffprobe executable hashes and self-report are in triage.md. Future execution should rerecord identities; present inspection does not count as encoding success.

## Decision and stopping boundary

Source support is sufficient to freeze a **narrow generated-stream protocol next**. No code or encoding is authorized by this document. The actual codec may produce an unsupported packet/header layout; preserve it as a capability mismatch rather than “fixing” bytes to fit the reader. The useful result remains a real demux/decode frame-count boundary, not a new benchmark or general-purpose parser.
