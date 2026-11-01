# Static checker freeze

2026-11-01 02:38 UTC. `check.py` SHA256 `20901fdd4f66eaaac7d1ddd7c8bc2041ae04215ba899247fa91e23fa650637e9` frozen before inspecting any author output. No checker, author reader, or runner was executed during preparation. Only `run.py` was read for its serialized output schema; the literal expectations came from the already frozen `expected.json`, not decoded output or reader imports.

Final source pins supplied by main are recorded separately in `source-pins.json`. The checker accepts fixture root and explicit stdout/stderr/exit-code paths; exit-code file contains the integer 0 alone for a successful recorded process. Example invocation, NOT yet executed:

```
python check.py /path/to/copied-fixture --stdout /path/to/stdout.txt --stderr /path/to/stderr.txt --exit-code /path/to/exit-code.txt --source-pins source-pins.json
```

It binds the three source files, both complete input JSON documents/data URIs, all 44 literal bytes, artifact hashes, seven case records and terminal raw/parsed result. It checks both full successful values/address maps and the five existing rejection labels. This remains seven semantic cases; source/artifact/raw consistency checks are not additional decoder scenarios. It does not reconstruct the negative executions from binary artifacts because the runner does not archive five mutated inputs; those transformations remain source-inspected, while the checker binds that source identity and reported outcomes. Source hashes/recorded exit/stream agreement are not execution authentication.

The script is portable with respect to archive location and has no installed-engine/library dependency. The independent expected JSON is itself hash-pinned; externally supplied source pins must be the separately reviewed file, not untrusted archive claims. No generic glTF validator or arbitrary URI loader is included. Finite checks use explicit exceptions and remain active under -O, but no optimized invocation or synthetic parser test has yet been executed for this checker.
