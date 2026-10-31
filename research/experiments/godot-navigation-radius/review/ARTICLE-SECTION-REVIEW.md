# Navigation radius section editorial review

2026-10-31 20:21 UTC. Accepted final author section research-drafts/godot-navigation-radius/article-section.md SHA256 bd8b8e327348d5cb5dddeff4ff81dd86ae88bc8f2cb50dc7d664c647a3c9b747. No engine rerun or source/results changes.

Original ea25e975 text overstated query margin as logged runtime evidence. Requested narrow distinction: collider/shape and wall fields are logged, margin0 is explicitly set in source but no getter readback is recorded. Final text fixes it. No underlying run/oracle changed.

Other claims accepted: two bakes/four actual agent paths, independent two-bake repeat, three synthetic rejects with zero Godot executions; floor-only bake free-edge erosion versus separate physical walls; observed navY0.2 versus explicit spherecenterY1.5; no RVO, movement, sweep, global reachability or collision-safety inference. Ready-state gate is bounded to this initialized map/region and not a generic timing barrier. Startup source hashes are correctly described as observations, not enforced immutable manifest or post-run rehash. Broader article prior2D-scope wording still requires parent integration qualification; this review covers standalone section only. Intended archive links depend on parent copying evidence; no current publication identity asserted here.
