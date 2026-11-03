# Lua 5.4.8 coroutine close: finite execution protocol

Status: PREPARED, NOT EXECUTED. Independent static review and explicit execution approval are required. This document remains a pre-execution input; actual results belong in separate receipts.

## Scope and literal oracle

The original case.lua uses three fresh coroutines and three separate event arrays. A table with a __close method records events only: it is not a game, file, GPU or network resource. The table sentinel in the error branch is compared by identity, never printed. Assertions check complete return arity, values/identity, exact event sequences, coroutine status and close count before each fixed output label. The independent literal seven-line stdout oracle is frozen in runner.py, not derived from execution.

All three first resumes must return true, waiting (two values), suspended, zero closes and only enter. Then:

- normal: resume returns true, done (two values), dead; enter,after-yield,close; one close, nil error argument.
- close: explicitly close while suspended returns only true, dead; enter,close; one close, nil error argument. No after-yield event.
- error: the second resume throws the prescribed table sentinel without an inner protected handler; returns false and the same sentinel (two values), dead; enter,before-error, zero closes. Explicit close then returns false and the same sentinel (two values), dead; enter,before-error,close; one close with that same sentinel as its error argument.

No close-method error, GC, wrap, external callback, thread, crash or host-cleanup case is included. Success is only a finite observation of these inputs. Lua's _VERSION checks the 5.4 series; exact patch identity comes from verified release inputs, not that string alone.

## Fixed source and local build

Official source: https://www.lua.org/ftp/lua-5.4.8.tar.gz
Release 5.4.8, 21 May 2025, 374332 bytes; SHA256 4f18ddae154e793e46eeab727c59ef1c0c0c2b744e7b94219710d76f530629ae, checked against https://www.lua.org/ftp/ . The archive's lua.h contains the 1994–2025 Lua.org, PUC-Rio MIT notice. Preserve it with redistributed source. This local package does not require publishing the upstream archive.

runner.py extracts only its explicit src C/header list, checking exact member uniqueness, regular-file status and bounded size. It does not extract paths chosen by archive members, links, Makefiles or executables. Explicit C sources exclude luac.c. Build uses cc, C99, -O2, -Wall, -Wextra, -DLUA_COMPAT_5_3 and -lm. No platform macros enabling dynamic loading/readline, no system Lua linking, no installation or platform guessing. The included loadlib.c is compiled in generic mode, not a promise that every future build has the same feature set.

## Preparation and bounded execution

Verify manifest keys and every original input hash: archive, case.lua, this protocol and runner.py. Reject symbolic links in paths/ancestors. Create a fresh 0700 runs/<name>, refusing reuse; copy inputs and verify all copied hashes. Create work, private-logs, HOME, all listed XDG and TMP directories at mode0700, with actual write/unlink probes before the first subprocess. Environment is a complete whitelist: fixed PATH, C.UTF-8, UTC and those new directories only; no inherited LUA_* configuration. Invoke the locally compiled interpreter with -E and case.lua, stdin closed.

Compile has a 120-second timeout, run a 5-second timeout; each starts a process group, killed on timeout and the direct child reaped. This is bounded normal POSIX process-group management, not a security sandbox or proof against deliberate detachment. No timeout fault test is included. Missing compiler or other preparation failure stops; never install or auto-retry.

## Results and privacy

A failed-by-default receipt is created once the exclusive run root exists. Earlier input/run-name rejection may occur without a receipt. A zero compiler exit and the expected regular output file permit the runtime step. Nonempty compiler stdout/stderr are retained and flagged as requiring human review, not silently classified as harmless or automatically treated as a semantic failure. Both exits must be zero, runtime stderr empty, and runtime stdout byte-equal to the frozen literal before passed. That status means the finite oracle matched; any compiler diagnostics still require separate review before publication. If diagnostics indicate a substantive build problem, stop acceptance and escalate rather than treating a matching runtime trace as a cure. No diagnostic class is presumed before actual execution. Keep any failed stdout/stderr intact locally, including unexpected output; do not turn an incomplete run into old success. There is no automatic retry.

Private logs contain raw diagnostics. Only a successful validated runtime stdout is copied to output.txt; failure output is never promoted as public output. result.json contains source/input/output hashes, fixed technical flags, stage, exit codes, empty-stream flags, copy/environment checks and a general failure category. No installed compiler location/version probe, host fingerprint, process identifier or binary hash is collected. A receipt or wrapper pass does not certify real resources, all Lua error paths, platform equivalence or the previous source-only article's full scope.
