# Headless Godot Control safe-area layout fixture

Run `python run.py`. Python creates an isolated temporary Godot project and XDG directories, copies layout.gd, invokes the installed Godot with a 60-second subprocess timeout and a 120-frame engine cap, extracts OBSERVED JSON, and cleans the temporary directory. No project/cache is created beside these source files.

Actual Godot 4.6.3 built-in Control nodes are laid out in a 1200×800 SubViewport. Two process_frame signals pass after construction before reading position, size, anchors, offsets and get_global_rect. All expected node values are exact assertions. Returned JSON is actual engine node state, not a Python rectangle calculator.

Input is explicitly mocked: a 2400×1600 physical window with safe rectangle (120,80,2160,1440), converted by a declared 2 physical pixels per UI unit. This is symmetric inset and axis-aligned untransformed Control geometry. No DisplayServer safe-area query is made, no mobile device runs, no viewport stretch or project scaling policy is inferred.

Full parent + one inset gives global (60,40,1080,720). Already-inset parent + zero child inset gives the identical global rect, with local child position (0,0). Already-inset parent + repeated inset gives (120,80,960,640), an incorrect double reduction. The latter is not outside the safe area; it wastes available space and moves HUD placement inward. Raw node output is provided rather than a claimed mobile screenshot.

Limits: no Container layout rules, minimum-size constraints, rotation, asymmetric cutouts, device orientation changes, keyboard, dynamic platform reports or touch interaction tested. A production conversion must account for its actual coordinate mapping and parent ownership of insets.

Execution note: initial attempts exceeded 30 and 60 seconds without a result. A bounded retry then succeeded; no successful result was inferred from the timeout runs. The final run.py retains bounded execution and includes captured logs if a future run times out.
