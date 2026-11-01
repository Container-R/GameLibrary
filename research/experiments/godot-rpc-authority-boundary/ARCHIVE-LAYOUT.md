# Publication layout

Accepted author evidence is `evidence/27e538cb-7c1e-4feb-8e60-ddfb3960b6ad/`, bound to the current nine-source set. Independent accepted evidence is `review/native-repeat/evidence/58830003-76ab-4bab-a089-36d642139fb4/`, bound to its exact source copy `review/native-repeat/`.

The failed author invocation is published once under `historical-callable-return-failure/evidence/cee0c49d-8f19-4f76-aeee-76d302a255ca/`, with its exact nine-source snapshot and original raw logs. It remains FAIL. Local duplicate failed-evidence directory is omitted, not merged with the corrected source. Initial pre-native reviewer findings and source snapshots remain separate from runtime history.

Environment directories, caches and bytecode are excluded; recorded selected-environment paths do not need to exist for static consumers. STOP is a small original coordinator barrier file, not a request data channel. Original raw streams and receipts are kept. The source discovery gate and primary/source/protocol/code/native/editorial review remain accessible under source-gate/ and review/.

Use consumer.py with explicit source-root/evidence arguments, or review/check_native.py with evidence directory, for static checks. Some historical synthetic review probes preserve original workspace paths; these are inspection history, not a portable launcher. Native reproduction requires a new external disposable copy as README specifies. No archive consumer authenticates that execution occurred.
