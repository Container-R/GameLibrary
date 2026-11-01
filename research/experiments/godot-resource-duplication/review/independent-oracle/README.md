# Protocol-only literal graph oracle

Frozen 2026-11-01 03:00 UTC after acceptance of protocol748ab074 and BEFORE author code/results inspection. Written directly from the protocol, with no implementation execution, JSON parser execution, engine/version invocation or generated observation.

`expected.json` enumerates all three modes and four ordered stages. Common fields apply to every row: two Gradient points, offsets[0,1], white point1, held-reference value relationships, stable object equivalence classes, shared script and distinct copied root. Palette names resolve to literal RGBA tuples. Thus the full arrays and aliases are specified without inventing actual object IDs. Point0 lists are entry0/entry1/entry2 in order. Sentinel null means no fourth element exists, not a fourth element storing null.

The mode-level copy-entry identities and Array-identity Boolean must hold at every stage, including immediately after duplication. A2 is the same root as A; held B/C/Ccache values follow their bound original objects. No clone path preservation is assumed. Root native class Resource is distinct from its attached script identity; every payload is a Gradient.

This is prospective expected data, not an observed PASS. The finite graph oracle does not authenticate the installed binary, prove generic deep-copy isolation, or transfer earlier ResourceLoader cache observations. A later checker may translate the frozen aliases into equality/inequality relations on observed canonical decimal IDs, but must not substitute newly observed values for these literals.
