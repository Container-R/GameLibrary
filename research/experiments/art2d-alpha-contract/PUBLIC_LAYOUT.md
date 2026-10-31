# Public numeric evidence layout

All fixture data are original numeric buffers and text; no artwork, screenshots or image binary is included. Author and independent reviewer results are preserved separately. Source gate is copied here as `source-gate.md`; historical draft paths in the frozen contract/README are provenance, not runtime dependencies.

`review/check.py` verifies all 11 operations, source hashes and **actual files at the recorded runtime paths**, then creates two negative probe directories. It is not a portable archive-only verifier and intentionally refuses to recreate those directories. To repeat: copy the review directory to fresh scratch, remove the archived `optimized` and `dependency-import-failure` directories only in that scratch copy, ensure identical recorded runtime files are available, and run `python3 check.py`. If runtime paths/hashes differ, stop rather than relabeling the old environment as verified. Alternatively run the fixture in a new environment and document a genuinely new result; do not overwrite historical source or summaries.

The author and reviewer summaries and raw logs are separately checked during integration. Their matching source/tool/operation records do not authenticate the installed binary or prove a second compositor implementation. The two startup failures are not additional color-behavior cases.
