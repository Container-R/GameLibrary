"""Two complete synthetic histories indistinguishable to the old progress counter."""
histories = {
    "A": (("raid-1", 4),),
    "B": (("raid-2", 2), ("raid-3", 2)),
}
def project(events):
    # Authoritative successful runs; delivered events may be duplicated.
    by_run = dict(events)
    return sum(by_run.values()), len(by_run)
for player, events in histories.items():
    kills, wins = project(events)
    print(f"{player}: old_kills={kills} old_goal_3={kills>=3} new_goal_5={kills>=5} wins={wins} win_goal_2={wins>=2}")
assert {project(e)[0] for e in histories.values()} == {4}
assert {project(e)[1] for e in histories.values()} == {1, 2}
assert all(project(e + e) == project(e) for e in histories.values())
print("same stored kills cannot determine new win progress; identical deliveries do not change either projection")
