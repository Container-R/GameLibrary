# Scoped Vulkan instance capability observation

## Result and evidence boundary

On 2026-10-31, one native child invocation, `c8cf0a91-18ed-4b66-afb4-11141bb7ed0d`, attempted `vkCreateInstance` once and received `-9` (`VK_ERROR_INCOMPATIBLE_DRIVER`) once. No instance was successfully created, so neither device enumeration nor destruction was called. The child exited 0 after recording this negative API result; stderr was empty, no timeout occurred, and the parent observed no remaining owned process group. Exit 0 means the evidence-recording process completed, **not Vulkan/GPU success**.

This establishes a failed Vulkan 1.0 instance request in the explicitly scoped system-path-only environment. It does not establish that physical hardware is absent, that every possible user environment fails, or that the loader is defective. No alternate API, driver installation, retry, device creation, shader execution or performance measurement followed. The existing matrix-major article remains actual shader compilation plus CPU interpretation, not shader execution.

`results/<UUID>/stdout.txt` contains flushed attempt and returned records followed by the terminal record. `receipt.json` records process metadata, exact source hashes before/after, the five isolated writable locations, explicit base environment, raw output hashes and terminal category. Loader bytes before/after both match `bbd6827e9fe418e9b9740aea57ce6d21fcea03e9876b4b17835c5a9c58f849fc`. Its filename is not authenticated version/build provenance.

## Frozen protocol and source review

`protocol.json` SHA256 `8ec8c5746b1b8280ea0a9acfc1cedc2fb73e2572970675d90db90bfa858a0057` predates implementation. It pins the source gate, independent gate review, Linux LP64 layout, exact helper, one-child/20-second deadline and allowed call branches. Both coordinator and independent reviewer inspected the native source before the one authorized invocation. There was **no independent native repeat**.

`source-manifest.json` lists the executed source bytes. `historical-pre-native-review/` preserves the exact initial source/manifest and four pure tests before consumer hardening. These are pre-execution review findings, **not failed native invocations**. The initial consumer underchecked phase/category consistency and recorded ABI/loader provenance. Final code checks these fields, uses the resolved hashed loader path, records before/after hashes and rejects incomplete/anomalous observations.

Six final author pure unit tests inspect ABI layout and synthetic records without loading a library. The independent reviewer separately checked eight pure records under normal and optimized Python. Synthetic checks do not exercise native success, partial enumeration, crash, timeout or driver cleanup paths. Only the negative create branch was observed natively.

## Read-only archival check

From the fixture directory, after relocation:

```sh
python consume.py results/c8cf0a91-18ed-4b66-afb4-11141bb7ed0d c8cf0a91-18ed-4b66-afb4-11141bb7ed0d --source .
python -m unittest -v test_pure.py
```

The consumer imports definitions only; it does not call CDLL or native APIs. It checks pinned archive consistency, not authenticated execution. Absolute paths in the receipt describe the original invocation and need not exist after publication; the checker validates their recorded relationships rather than reopening old temporary directories. Source checks apply to the explicit relocated `--source` tree. The pure author ABI test is Linux x86_64 specific; the archived consumer compares a literal frozen ABI and does not require the verifier host to reproduce it.

`run.py` and `child.py` are native-execution entry points, **not archival verification commands**. Running them again creates a new observation rather than reproducing the original receipt; it was not part of independent acceptance. Parent timeout limits waiting and attempts bounded TERM/KILL on its own Linux process group; crashes or kills cannot guarantee `vkDestroyInstance` or complete descendant cleanup. The five-location helper is not a sandbox. Environment isolation intentionally excludes user HOME/driver overrides while preserving explicit system XDG search roots; implicit system layers and loader build-time paths are not asserted absent.

## Scope exclusions

No graphics device properties, queues, physical-device handle addresses, shaders, surfaces, buffers, pipelines, dispatch or rendering are queried/created. No private HOME files, credentials or full inherited environment are archived. No installed loader/driver origin, hardware census, SLSA-like execution authenticity, Vulkan conformance or universal cleanup guarantee is claimed.
