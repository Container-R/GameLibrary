# Offline amix: independent protocol acceptance

2026-11-01 03:27 UTC. Accepted protocol `04beb14e9feab0215f5493fe4eda59426f2f4be75a22e1ba1fb3d9588e386f36` for implementation review, not native execution.

The source review is separately immutable: `SOURCE-REVIEW.md`, SHA256 `c4658b15a7b7f4247bc8cd04743eaa6af2dbd596518dd8afaaa2e061bee11c23`.

No material correction requested. The previously provisional seconds-based signal is explicitly superseded before implementation. The exact 256-sample partition, 4096/2048 lengths, A-first ordering, no padding and EOF/FIFO distinction support the prospective index2048 boundary. Zero-dropout arithmetic and non-authenticated comparison-source identity remain explicit. Byte equality is a deliberately stronger fixed-case acceptance choice, not a general numerical guarantee.

Independently froze `INDEPENDENT-LITERAL-ORACLE.json`, SHA256 `a904ecc7a41cbc9338f0b1ee8f48ecc046835a0792d67815e3bff9c039c36f2b`, before author code. It contains three input hashes, three expected full-output hashes, lengths and half-open literal sample segments. Only standard-library in-memory literal byte repetition and SHA256 were used; no media files or decoded observations were generated, and no FFmpeg/native/version/filter command ran. This oracle is a prospective expectation, not an execution result.

The command envelope is finite: version plus three sequential mixes, no additional native probes or retries; graph is one argv argument, not shell interpretation. Process attempts and returned children are distinguished, selected environment is minimal, source/input/tool pins bracket execution, and current PASS is withheld until final checks. Timeout handling is bounded termination attempts, not a universal cleanup guarantee. Future review must check implementation actually enforces these requirements, including failure stop and exact typed raw/archive associations.

Full samples and length must match; neither averages nor excluded transition windows may replace the fixed oracle. Archive hex permits portable reconstruction without installed FFmpeg. No middleware lifecycle, audible quality, runtime schedule or complete dynamic-library provenance is established. Native execution still requires separate exact-code review and parent authorization.
