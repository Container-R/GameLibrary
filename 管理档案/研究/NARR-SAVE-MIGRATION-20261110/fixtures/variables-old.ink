VAR knows_bridge = false
VAR score = false
-> checkpoint
=== checkpoint ===
Checkpoint.
+ [Continue] -> after
=== after ===
{knows_bridge:
    + [bridge_route] -> bridge
}
+ [road_route] -> road
=== bridge ===
Bridge.
-> END
=== road ===
Road.
-> END
