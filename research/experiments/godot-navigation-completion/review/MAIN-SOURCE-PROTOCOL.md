# Main source and protocol acceptance

Observed 2026-11-01 01:14 UTC. Read the existing SOL-AI-001 article and exact gate/reviewer records. Its current exclusion of actual character motion is accurate. Read Godot4.6 NavigationAgent3D class description, signals, method contracts and Using NavigationAgents pathfollowing; independently inspected stored public comparison C++ at35e80b3a8822a9df9be390814b62f44c0a9c69e8.

The class distinguishes last-waypoint completion from requested-target reach. The tutorial assigns movement to caller code; no agent-driven collision locomotion is implied. Pinned methods show four updating getters; repeated calls are not assumed frame-cached. Reachability uses target_desired_distance >= endpoint distance, whereas reached/waypoint progression uses strict distance comparisons. The protocol avoids equality boundaries. Passive accessor constness and target-before-finish ordering agree with source. This does not authenticate the installed executable against the public source.

Accepted protocol7e5197e2368bb8be30c446b3a8ac1cc2274b781e77e2db8238a1788963d53dad for implementation/pure review only. No native/version run authorized. Both query sequences precede either position assignment; callback logging is passive. Initial topology/path/ownership/configuration gates must pass before movement. Main interim code inspection requested early exact region/configuration and agent hierarchy/settings gates plus recorded readiness callback count; final source must be reviewed after author completion.

No runtime outcome, performance, physical arrival or general AI cancellation semantics follows from this source/protocol acceptance.
