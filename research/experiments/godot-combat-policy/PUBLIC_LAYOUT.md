# Public evidence selection and rerun safety

Final author and independent reviewer raw traces, commands, status receipts, frozen source and results are published. Initial author `historical-declared-tree-order` evidence is retained to expose the instrumentation weakness: tree_order originally echoed a constant, although source creation order was correct. This was not a failed combat oracle. Final source measures actual child order.

The intermediate observed-tree-only author batch and earlier independent repeat batches remain local; their duplicate raw logs are not all published. `intermediate-provenance.json` preserves the intermediate source/result identity and explains omission. These are repeated executions of four scenarios, not extra unique cases. No engine failure or unexpected behavioral result was omitted. Final full independent evidence is under `review/`.

Author README/execution.json were frozen while review was pending; `review-completion.json` and final `review/REVIEW.md` supersede that historical status without rewriting the frozen files.

Negative directories retain actual outer probe streams and subprocess status/streams, but omit generated copied source files; `review/check.py` records the exact mutations and can regenerate them from `review/fixture`. **Run only in a fresh scratch copy.** That checker recreates its fixed-name negative directories and would overwrite archived probe evidence if run here. It also checks the actual binary at its recorded absolute path, so it is not a portable archive-only verifier. The raw-log archive checks in the repository registry do not launch Godot.

To repeat author execution, copy final main.gd/main.tscn/project.godot/contract.md/run.py to a fresh directory, verify the intended installed binary and dependencies, then run `python3 run.py`. New runtime identity is a new observation, not permission to relabel old evidence. No binary or third-party source is distributed here.
