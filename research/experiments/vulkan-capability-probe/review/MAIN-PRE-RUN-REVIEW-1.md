# Initial implementation review, before native launch

2026-10-31 22:43 UTC. Reviewed child.py 1d89be32, run.py 8d693504 and consume.py 91a9586e, manifest213d74ed. No native invocation authorized or observed; this is a rejected implementation draft, not a failed Vulkan experiment.

Native ABI bindings and bounded count-before-index logic match accepted protocol. Child library loading should use the already-resolved hashed path rather than re-resolving a requested symlink. The parent needs explicit ordinary setup/spawn exception receipts and before/after identity observations. A genuine interruption may still leave STARTED; that must fail closed rather than be relabeled complete.

The initial consumer checks UUID/stream/raw/source consistency but does not enforce recorded ABI, loader identity or exact scoped environment/argv. It only fully checks enumeration categories and instance-creation failure; other categories could accept inconsistent phases/cleanup. Destroy returned must be exactly null, not any integer. Require phase-specific validation for all claimed outcomes, and separately preserve partial/error observations without labeling completed native success.

Author asked to preserve this initial source/manifest/pure-test snapshot, correct the specific issues and return hashes before launch. Tests so far are pure Python/ABI/JSON checks, not native call attempts. Do not count a source-review rejection as a runtime failure, and do not present future archived consistency checks as authentication of execution.

Second draft read at22:44 UTC (child dea86a15, run7c862407, consumer4f55cbad): principal fixes added. Remaining bounded corrections requested before launch: compare archived ABI with frozen expected layout rather than the verifier host; missing ABI record is not a valid ABI_GUARD_FAILED observation; validate resolved loader path and signed/unsigned native integer ranges; reject creation-failure record claiming a valid instance. No native calls yet.
