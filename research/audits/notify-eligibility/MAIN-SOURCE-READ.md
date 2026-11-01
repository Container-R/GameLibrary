# Main source read: Notify eligibility versus request ownership

2026-11-01 UTC. Directly read the Epic 5.6 Animation Notifies manual's Common Notify Properties and Montage Notify sections, generated AnimNotifyEvent property descriptions, and Networking Overview's architecture/gameplay example. Returned page titles identify version 5.6; no immutable source commit, patch version or runtime behavior is established.

The exact dedicated-server property description supports the authored eligibility question. The manual's weight/chance/LOD/follower descriptions and queued/branching timing choices do not establish filter implementation order, bypass rules or a network-authority bridge. Generated Python constructor defaults are not actual project asset defaults. The networking source separates client/server worlds and makes replication/requests a designed implementation concern.

A proposed configuration mismatch needs an additional explicit premise: the expected sole request path is the server-local Notify handler, with no separate client-to-server forwarding or other authoritative request mechanism. A client-side Notify could otherwise legitimately participate in an authored request path; disabling server-local triggering alone would not prove the request absent. Prefer an ordinary sequence custom Notify for the finite example and keep Montage timing discussion separate from implementation claims.

Client/editor preview is not evidence that the server-local hook ran. Conversely, enabling the server flag is not evidence that all animation evaluation, authority checks, hit validation and idempotency requirements are met. This supports an original asset/role checklist, not a blanket prohibition on animation-driven gameplay.

No engine source implementation, UE runtime, damage/collision experiment, network traffic or binary was inspected or executed. Existing Godot method-track and Python simulation observations remain separately scoped.
