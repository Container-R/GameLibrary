# Resume write-gate model

Original Python standard-library model for the accompanying Steam Dynamic Cloud Sync design. Run:

```sh
python test_cloud_resume.py
```

20 safety/transition tests executed on 2026-10-31; see `test-output.txt`. The harness uses immutable value objects, serialized method calls and in-memory assignment. It assumes notification invalidation precedes subsequent write dispatch. An additional full disk-object equality guard against the loaded baseline catches an abstract unnotified change, including changed content under the same revision, but is **not** a filesystem compare-and-swap.

Only direct-parent fast-forward is implemented. Unknown ancestry conservatively becomes conflict. Recovery retains both objects in RAM only; it does not provide durable backups or implement user choice. Constructor/save jobs are trusted internal objects, not a network/file decoder. Values are integers, not a real game schema.

Not covered: Steam SDK/client callbacks, real suspend scheduling, already-issued asynchronous writes, threads, filesystem locking/atomic replace/fsync, crash durability, checksums/cryptographic identity, cloud uploads, authentication, account switching, disk-full failure, or actual multi-device integration. Passing tests validates only these explicit model transitions, never platform safety.

Revision allocation requires exact nonempty strings and rejects locally known or reserved IDs (including observed parent IDs). The teaching registry caps at 256 entries and fails closed instead of evicting IDs. This is not a global uniqueness protocol: the caller must ensure cross-device/persisted identity uniqueness, and the model does not validate a complete revision DAG. Constructor/save jobs remain trusted internal objects.

Review regression: a revision-only dispatch guard previously overwrote unnotified changed content under the same revision. The full-object guard now rejects it without mutating any coordinator field and retains the candidate object. Independent failure evidence is owned by the separate deep-QA review, not rewritten here.

Incoming reload candidates using a known/reserved noncurrent revision are conservatively rejected to recovery (including a→b→a identity cycles); only the exact current loaded identity can be treated as unchanged. This may require manual recovery for repeated conflict candidates; it is not a complete revision-history resolver.

Separately run `python test_inflight_counterexample.py` (1 executed counterexample; output in `counterexample-output.txt`). It deliberately applies an already-issued external old write after a newer download, then rejects its completion token. The assertion confirms that the newer bytes are nevertheless lost. This is evidence of the limitation, NOT one more protection test, and does not claim actual Steam scheduling behaves this way.
