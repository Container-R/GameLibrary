# Music frame archive integration check

The integrator independently ran the existing archive verifier in normal and optimized Python modes: 127 declared consistency checks passed in each mode with byte-identical reports. This is not 127 audio tests.

The independent reviewer’s literal full-PCM checker was run against both the author and reviewer **public text-only archives**, with raw WAV duplicates omitted. Both passed. Two separately parsed `RESULT_JSON ` raw stdout records exactly equal their respective summary JSON. No additional FFmpeg filtering was performed by this integration step. Actual author and reviewer filtering commands and their outputs remain in the experiment archive.

`summary.json` records commands and exits; numbered stdout/stderr files preserve actual output. Paths reflect the publication staging directory at execution time. To repeat in another checkout, substitute the repository root while retaining the same relative files.

The verifier checks selected source hashes and author/reviewer metadata, cases and artifact equality. The independent PCM oracle adds the semantic and lossless-archive checks; neither proves listening quality, runtime middleware loop behavior, build authenticity, or arbitrary failure-path freshness.
