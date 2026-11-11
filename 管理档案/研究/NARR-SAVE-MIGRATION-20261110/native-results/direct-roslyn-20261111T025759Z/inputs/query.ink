EXTERNAL has_rope()
~ temp equipped = has_rope()
{equipped:
    + [rope_route] -> finish
- else:
    + [walk_route] -> finish
}
=== finish ===
Done.
-> END
