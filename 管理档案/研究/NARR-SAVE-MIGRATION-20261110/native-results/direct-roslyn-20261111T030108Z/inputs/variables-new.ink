VAR heard_bridge = false
VAR score = 0
-> checkpoint
=== checkpoint ===
Checkpoint.
+ [Continue] -> after
=== after ===
Arithmetic: {score + 1}.
{heard_bridge:
    + [bridge_route] -> bridge
}
+ [road_route] -> road
=== bridge ===
Bridge.
-> END
=== road ===
Road.
-> END
=== migration_resume ===
-> after
