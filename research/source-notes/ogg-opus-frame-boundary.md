# Ogg Opus frame-count boundary: source receipt

Accessed 2026-10-31. Source reads preceded implementation and media execution; protocol `4024d6fda4d3533eeca3e124d79c398cae1ec540d143da7ef18b6fb0ba27db5e` was accepted separately. This metadata note complements original experimental analysis, not a standards translation.

| Primary source | Version/date and exact sections read | Used for / limit |
|---|---|---|
| [RFC 7845](https://www.rfc-editor.org/rfc/rfc7845.html) | April 2016, Terriberry / Lee / Giles; §§3, 4.2–4.6, 5.1–5.2 | Header placement, pre-skip / initial-position / tail-trim interpretation and bounded comment parsing. General streams may have nonzero initial positions; this fixture explicitly proves zero for its observed stream. At-most-one-packet trim is a chosen subset restriction, not an RFC MUST. |
| [RFC 3533](https://www.rfc-editor.org/rfc/rfc3533.html) | May 2003, S. Pfeiffer; Informational; §§5–6 | Page structure, lacing/continuation and checksum fields. Not a decoder or full Opus conformance source. |
| [Xiph Ogg framing](https://xiph.org/ogg/doc/framing.html) | Publication date not established; checksum/framing sections | Direct polynomial CRC convention; comparison is integrity checking, not provenance authentication. |
| [RFC 6716](https://www.rfc-editor.org/rfc/rfc6716.html) | September 2012, Valin / Vos / Terriberry; §3.1 Table 2, §§3.2.1–3.2.2 | Actual TOC duration / code 0 packet structure. Zero-length frame payload can be valid but is outside this fixture's accepted subset. |
| [FFmpeg libopus documentation](https://github.com/FFmpeg/FFmpeg/blob/3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587/doc/encoders.texi#L969-L1064) | Official `n7.1.5` pin `3a0867c2bfda4a4d4309ca1a8cbdc6175e67f587` | Encoder options only; no authenticated equivalence to installed Debian bytes. Pinned documented maximum duration differs from installed help; selected 20 ms is shared and actual packets are checked. |

Runtime evidence is separate: exact FFmpeg self-report, executable hash, five resolved library hashes, commands, process timestamps and original data archives are in the experiment receipt. Package-version lookup returned no matching records for the selected library packages; libopus release is not inferred from SONAME. No listening study, real game asset, platform codec implementation, or middleware execution is asserted.

The source-only gate, independent source/protocol/code reviews and pre-native synthetic defect probes retain chronology. This case's formulas and handoff checklist are original analysis; all PCM bytes are generated from the frozen integer formulas. No third-party audio or copied standards diagrams are included.

[Experiment and exact evidence](../experiments/ogg-opus-frame-boundary/README.md) · [Music handoff article](https://github.com/Container-R/GameLibrary/blob/1a7bf18b24ba56395892c4c0cdb3b2acecc16985/solutions/music/pcm-loop-frame-contract.md)
