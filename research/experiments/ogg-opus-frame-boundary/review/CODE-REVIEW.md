# Initial pre-native code findings

2026-10-31 23:24 UTC. Reviewed initial run5aa9277e, reader6bcd411d, consumer818983a1, common da589ab8, tests8919cbf9; exact source snapshot preserved in `initial-source/`. No FFmpeg/version/codec invocation, media generation or real compressed input processing performed. Synthetic framing is artificial non-entropy-coded data and was never submitted to a decoder.

Five author pure methods passed normal and optimized Python, but this does not cover receipt integrity sufficiently. `probe_consumer.py` creates a synthetic receipt whose headers/counts match the finite oracle, then independently mutates it. Results in `initial-consumer-probes.jsonl` confirm:

1. Before/after libopus hash changed together to all-zero digest still accepted; only executable identity pinned.
2. Unrelated selected HOME mapping still accepted; environment ignored.
3. Different receipt UUID still accepted; not bound to invocation directory.
4. Rehashed parsed.json false channels, stereo bit, packet start page and continuation count still accepted; these metadata fields not associated with original bytes.

The synthetic unmodified control being accepted proves only internal consistency of the test setup, not real execution. No authenticity claim is intended.

Static inspection additionally finds plain JSON duplicate-key ambiguity, no independently frozen protocol pin, insufficient OpusTags metadata/page-placement revalidation in consumer, and unbounded gzip decompression. Author is correcting these before native execution. The structural reader's source-level TOC/duration/CRC/origin arithmetic is otherwise aligned with the approved restricted protocol, but the archive consumer must not certify altered recorded facts it has not checked.

Runner review also requires encoded subset parsing before decoding (currently after both media operations), explicit source-after evidence and process timestamps, input-formula check before encoding, and clear environment/timeout cleanup policy. Initial inherited environment and subprocess.run leader-only timeout cleanup must not be represented as sealed dependencies or universal descendant cleanup. Main and author are coordinating narrower fixes; no native authorization is inferred here.

Initial code is NOT accepted for execution yet. Preserve this finding record and source bytes; subsequent corrected-source acceptance belongs in a new review file.
