# Pre-execution source review

2026-11-01 02:34 UTC. Accepted for the fixed seven-case CPU protocol. No reader import, compilation, fixture generation or execution in this review.

Exact source hashes:
- `reader.py`: `f4236faccf9de7d57f65d5f4e68f8e900865bac7cd42f480e5cfe81f6d376f91`
- `run.py`: `d825d33f2af4d304a930fecdd8f42088fca22a6f24cfd9bc965a045688ef838b`
- `protocol.md`: `de8c9bd74299fb409d58859a099de8b5ff2802df6b78ba1308400762b294172d`

Read full reader and runner. The reader resolves initialized base values before replacing indexed elements; absent base emits zeros without reading the unused dense region. Bounds are checked at backing view and local payload levels; view/local component alignment is separate. Sparse count, strict-int indices/metadata, tight layout, finite floats, order and index range are enforced before replacement. Element addresses are computed from view + local offsets with the declared component sizes. No additive or destination-position confusion found.

Runner literal hex matches the frozen three rows. It writes/reloads two JSON documents and validates their embedded bytes before decoding. Five private-copy mutations match protocol offsets and exact rejection categories. Ordinary Python list equality permits integer/float numeric equivalence here, but values arise from fixed struct decoding and addresses from validated exact ints; this is a fixed test oracle, not a general hostile-JSON acceptance consumer.

Scope details for later evidence: the decoder receives an explicit bytes argument and does not resolve URI content itself. The positive runner binds the data URI to those bytes; the negative byte mutations exercise the decoder directly while the document URI stays the original one. Do not call these five malformed disk-asset import tests or claim general URI consistency validation. Optional view layout fields are rejected when the view is used; this is not whole-document glTF validation.

Summary removal occurs before reader import and optimized-mode rejection. Unexpected mismatch stops with nonzero exit and no successful summary; partial CASE_JSON output remains useful. Source hashes are recorded at completion, not an authenticated before/after receipt. For the authorized run, preserve the pre-run freeze, actual process exit/raw logs and post-run source comparison externally. The small runner is not the hardened native invocation harness.

No material code correction required for this bounded protocol. Five negatives are not exhaustive alignment/type/error-injection coverage. Existing dense/native archives remain unchanged. Main owns execution authorization.
