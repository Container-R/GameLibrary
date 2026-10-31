# Independent pause/input fixture audit

Date: 2026-10-31 UTC. Reviewer independently read the author fixture, identified a vacuous pause witness at high process frequency, then reran the corrected frozen source in a separate directory. Author `results/` were not overwritten. This is independent review on the **same installed engine and platform**, not cross-platform or different-build replication.

## Review correction and result

The initial fixture waited one `_process` callback while paused. At artificial 144 fps there need not be a physics scheduling opportunity in that interval. The corrected fixture waits for at least two actual ALWAYS-controller physics heartbeats and asserts the PAUSABLE gameplay count remains unchanged. Independent runs at artificial 30/60/144 fps all passed, with respectively 4/5/13 process callbacks, 6/3/3 gameplay physics callbacks, and two paused heartbeats each.

Independent output is in this directory's `results/` and `runner-output.txt`; author output remains the fixture's separate `results/`. Both summaries record matching five source SHA-256 values and Godot binary SHA-256. Engine: `4.6.3.stable.official.7d41c59c4`, Linux x86_64, Python 3.12.14. The source files in the fixture root are checked against these fingerprints; the verification script is review tooling, not part of the fixture's original five-file source manifest.

## Additional evidence check

`verify_pause_trace.py` compares author/reviewer source and engine-binary manifests, hashes the author's actual source files, and checks that each recorded paused heartbeat falls strictly between the unique pause/resume boundaries. It also checks heartbeat sequence, fixed delta, unchanged gameplay counter, and absence of a gameplay physics entry inside that interval. It reads saved evidence; it does not rerun Godot.

After archiving this directory as `fixture/review/`, run:

```sh
python review/verify_pause_trace.py
# Or from any working directory:
python /path/to/fixture/review/verify_pause_trace.py /path/to/fixture/review --author /path/to/fixture
```

Original local verification command:

```sh
python research-drafts/godot-pause-input-independent-review/verify_pause_trace.py --author research-drafts/godot-pause-input
```

Actual output: `verify-output.txt`. No dependency on that original sibling layout is required after publication: the default author directory is the evidence directory's parent, with an explicit override available.

## Confidence limits

Exact synthetic input receiver/event-list oracles and queue results passed in the independent engine runs. The naive failure is deliberately retained **application-owned queue persistence**, not an engine input-buffer bug. Dual-boundary queue clearing prevents old commands reaching the epoch filter; rejection of separately delayed stale-epoch commands remains untested. The fixture does not show that a late physical event tagged with the new epoch can be detected. Artificial `--fixed-fps` schedules, headless callbacks and manually injected InputEventAction pairs establish neither physical device delivery nor real-time rendering performance. Signals may still execute on paused nodes; this is not a global business-state write barrier. No material blocker remains for these explicitly scoped claims.

## Provenance clarification — 2026-10-31

The version string is the local executable’s self-report. Matching fixture-source and executable hashes establish consistency for these runs, not official release authentication or exact engine-source correspondence. Original observations and raw logs remain unchanged. See the [shared evidence note](../../../source-notes/godot-runtime-provenance.md).
