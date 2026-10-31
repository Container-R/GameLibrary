# Modal focus policy model

Original Python 3 standard-library state model accompanying the modal focus restoration article. Run from this directory:

```sh
python --version
python test_focus_model.py
```

Recorded execution: 2026-10-31, Python 3.12.14, eleven unittest methods passed (the invalid-flag test contains four subtests). See `test-output.txt`.

The model checks scope confinement, fallback after missing/ineligible/recycled opener, nested restoration, rejection of out-of-order closes and stale deferred focus requests. A per-open monotonic frame token rejects late close requests after the same named dialog is reopened. This token differs from the global revision used for deferred focus requests: closing a child changes the revision but does not invalidate its parent's close token.

Review caught an initial scope-name-only close guard that could close a newly reopened dialog. The `test_old_close_cannot_close_reopened_same_scope` regression exercises its fix and verifies that rejection does not mutate the current revision, focus, or top frame.

Limits: `visible`, `enabled`, and `live` are input booleans, not computed Unity layout/tree results. There is no real input consumption, focus event dispatch, rendering, animation, controller reconnection, accessibility API, platform certification, or full fallback-chain implementation. A no-candidate result proves only that the model does not escape the modal scope; production needs an explicit usable recovery/exit state. Model tests do not validate engine integration or usability.

A newer accepted `user_focus` intent increments the revision even within the same scope. The same-scope user-navigation regression rejects an older deferred request. In engine integration, distinguish user/new focus intents from acknowledgement events of the coordinator’s own request; this model does not implement that event adapter.

The finite model forbids concurrently reopening a scope name already in the active stack; rejection is tested without mutation. Real products that allow nested instances of the same dialog template must bind nodes to unique frame/view identities, not just a shared template name. Sequential close/reopen remains supported by unique close tokens.
