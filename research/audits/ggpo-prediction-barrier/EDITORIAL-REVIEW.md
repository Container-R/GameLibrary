# GGPO normal-step barrier integration — editorial acceptance

2026-11-01 UTC. **ACCEPT unchanged** solution SHA256 `4b14a283b83e4015c6ef64dad5592b05454571b2ae9bdd971517df14763f40ff` and source-note SHA256 `206f79951f4ba32d3ab5e46554a0d2dcbafc2f8eb6318d25bf82a0314c3fd278`.

Read the new subsection and surrounding model/RPC/GGPO scope, both source reviews, and complete two-file diffs against the preceding stage. Independently reopened fixed upstream Sync::AddLocalInput (57–77), P2P AddLocalInput/SyncInput/IncrementFrame (263–338), and VectorWar_RunFrame/Idle (395–439) at `7ddadef8546a7d99ff0b3530c6056bc8ee4b9c0a`. No SDK, model, engine, network or archive execution; no source/stage/remote edits.

## Mechanism and logic

The rejection predicate includes both F>=M and F−C>=M, and precedes this input's queue insertion. P2P maps that rejection to the named error. SyncInput has a distinct path without that barrier, but the article correctly requires initial synchronization, valid internal preconditions and normal internal return before describing OK. It does not manufacture a successful reachable run after every rejected submission.

For positive M with F=M,C=0, both inequalities hold by direct substitution. This hand condition example is explicitly not a produced network history. Later synchronization success cannot retroactively admit the rejected input or replace the host's earlier failure gate. VectorWar's nested success checks concretely support the normal-forward integration proposal; drawing remains outside that branch.

The article limits stopping to this normal-forward branch, not all application state: idle may process rollback. The proposal is not imposed on rollback callbacks. Input retention, resampling, reconnect behavior, multiple-local-player partial success, optimal window choice and other backends remain unknown. GGPO's internal confirmation frame is not relabeled as the server-authoritative model's acknowledgment.

## Integration and public-scope scan

The diff adds metadata/source inventory and the new subsection; previously published RPC experiment prose is byte-unchanged in the diff, and no archive edit is part of this review. The source note labels its former three-file count as initial history and adds the call-chain scope rather than rewriting prior evidence. The wrapper mapping is recorded in the main source read, not claimed as an executed API validation.

A whole-file text scan found no absolute private filesystem paths, private execution identifiers or actual 64-hex binary identity in either reviewed public file. Existing public version self-report, loopback address and bounded experiment counts remain prior content; this is not approval or inspection of the linked raw archives. No new runtime metadata or execution result is introduced.

The source-only barrier has a concrete integration payoff without upgrading the 16 model tests or Godot RPC observations to GGPO evidence. No material correction requested.
