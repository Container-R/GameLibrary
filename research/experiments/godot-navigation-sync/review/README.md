# Independent review: navigation readiness and partial endpoints

2026-10-31: copied frozen `main.gd`, `main.tscn`, `project.godot`, `run.py`, `run_diagnostic.py` from `research-drafts/godot-navigation-sync/` to `fixture/`. Original artifacts were not modified. Ran exactly the main naive/guarded processes plus the authorized default-region readiness diagnostic.

## Verdict

**PASS for the stated initialization experiment; no material blocker.** Four main-source fingerprints, diagnostic runner bytes and binary digest match the original. Three actual Godot4.6.3 processes passed. Raw evidence is in `fixture/results/`, with `runner-output.txt`, `diagnostic-output.txt`, extra `review-checks.json`, and `optimized-rejection.txt` alongside this audit.

Independent observations:

- Naive query uses the newly created own map RID, at iteration0, and returns an empty path before regions register.
- Main guarded case uses explicit synchronous map and region settings, enabled regions, exactly one initialization submission and no further writer. Its own-RID map signal precedes readiness; map and region iteration checks are present. Request configuration is distinct from actual server getter observations.
- Reachable path is(5,5)→(25,5). Disconnected goal(105,5) yields a **nonempty partial path**(5,5)→(30,5), not successful arrival. Extra independent checks confirm both starts, endpoint error, goal projection, different region owners, no links/connections and partial-path containment in the original rectangle.
- Default-region diagnostic actually observes map-ready/region-pending states (4 observations this run), then final map iteration2 and the same correct paths. Final regions report enabled=true, async=true and nonzero iterations. Intermediate observation count is not a pass criterion and is not portable timing evidence.
- All three actual stderr files are empty. There is no startup-error whitelist or general error suppression. An unexpected diagnostic remains a harness failure.
- No `map_force_update`, sleeps, baked mesh claims or physical movement. Controls use the real NavigationServer2D, not a mock path list.

## Readiness interpretation

Map change alone was insufficient in the author's preserved weaker initial attempt. The diagnostic supports a concrete separation between region registration/map iteration and region geometry readiness without claiming that changing two flags isolated a single causal default.

The accepted main result is bounded to explicit synchronous region/map settings and one initial submission by one writer. The diagnostic demonstrates one default-region initialization run, not a transaction protocol. Region iteration!=0 and any prior map_changed are **not** a general barrier for ongoing/multi-writer asynchronous updates; production must track update ownership and ensure the map view incorporates the intended region version. The README already limits this claim. `!=initial` avoids assuming monotonic `>` forever, but only startup0→nonzero was exercised; no counter-wrap test was performed.

A nonempty path is judged by its endpoint, not truthiness. Empty startup results are classified pending, not cached as unreachable. Watchdog expiration is synchronization failure, not geometry proof. The finite hand-authored geometry supplies a disconnected control independently of path result.

## Sources checked

Official Godot4.6, accessed2026-10-31:

- [NavigationServer2D](https://docs.godotengine.org/en/4.6/classes/class_navigationserver2d.html): deferred server updates, iteration semantics, experimental scope and deprecated force-update boundary.
- [Using NavigationServer / Threading and Synchronization, Waiting for synchronization](https://docs.godotengine.org/en/4.6/tutorials/navigation/navigation_using_navigationservers.html): startup and queued-update distinction.

No graphics, avoidance, baking, continuous topology changes, pathfinding performance, engine-version generality or final-agent movement was independently tested.
