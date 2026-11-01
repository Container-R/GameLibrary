# Independent Resource duplication repeat and literal review

2026-11-01 UTC. **Accepted for the frozen three-mode graph.** No expectation, checker, protocol or source changes after results.

## Fixed identities and prior independence

Protocol748ab074 and literal expected.json8da52809 were frozen before author implementation inspection. Independent checker SHA256 `b333beb890c12505d031ae5d346b7b7b1cfe47173521147ce49df1cd644dfc17` was written before author native execution; it imports no author oracle/consumer. Source schema was read only to map archived fields onto the predeclared literals. Final source manifest SHA256 `c105634a0748ccd16589138bc94e5a292e80e4ff7f822cdb32f16f8160d60ddf` includes the separately reviewed strict raw/parsed equality correction. Initial bd5acde2 pins remain preserved, not reused for final evidence.

## Actual sequence and counts

1. Frozen checker accepted author UUID `db16c3a8-a67e-48ce-9e63-ab2b6706e777`, receipt SHA256 `b426c264d28f7ce88466889e419d1bc309b0f35df764c2c2e931bee9e4184d7b`. Exit0, empty checker stderr. Records under `independent-oracle/author-static/`.
2. After that pass, copied exact final eleven source/config files and manifest into fresh `independent-repeat/`. Invoked `python run.py` once, with command/start/end/raw streams/exit and source before/after captured under `execution/`. Sources remained hash-identical. Runner exited0 with empty stderr and produced UUID `0ab51875-74f4-4335-8af7-7e0cdbdf9ab9`.
3. Frozen checker accepted the independent receipt SHA256 `adf16bc46a4e4908fb9b60f2265b53430452bc52176a3c2a4fd6dd09afe2f398`. Exit0, empty checker stderr. Records under `independent-oracle/repeat-static/`.

The independent invocation ran exactly one version query plus three behavior processes, all RETURNED/exit0/empty stderr. Author plus independent repeat totals **two version queries and six behavior processes**, repeating the same **three unique modes**, each with four mutation snapshots. Two static checker invocations are separate Python inspections, not extra engine cases. There were no native retries, parse-only probes, additional malformed scenarios or extra version queries in this review.

## Literal findings

All four stages satisfy both value and identity relationships in the predeclared table:

| Mode | Array shared with A | B shared with original | C shared with original | Repeated B within D |
|---|---|---|---|---|
| shallow | yes | yes | yes | same live Resource |
| internal | no | no | yes | same cloned Resource |
| all | no | no | no | same cloned Resource |

Copied root D differs from A; A2 and cached root remain A. The shared script identity persists in all modes. Appending137 changes original length only in shallow. Editing copied B makes both copied B slots blue, but original B only in shallow. Editing copied C makes original/Ccache magenta in shallow/internal, not all. White endpoints, offsets, counts and all held identity classes remain as frozen. Built-in/external path classification and exported property metadata pass the setup gates; no clone-path preservation was required.

The checker independently expands the literal palette and symbolic identity classes, validates all original/clone/held value snapshots, strict numeric and identity types, raw/parsed association, mode/PID/UUID/argv, selected environment paths, before/after source/input manifests and recorded binary hash. It does not use author verdicts as the expected graph. Individual expected oracle booleans are checked only after independently verifying the graph.

## Limits / preservation

Evidence is on the same local installed binary SHA256 `f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3`, self-reporting4.6.3.stable.official.7d41c59c4. This repeat is not a second implementation/platform and does not authenticate correspondence with public comparison source. Record consistency is not execution attestation.

This validates only the original acyclic exported Array[B,B,C] graph and selected methods. It does not establish arbitrary clone isolation, thread safety, signal delivery, cache eviction, persistent writes, memory cost or rendered appearance. Prior ResourceLoader experiments remain separate. Historical pre-native bool-coercion false acceptance is retained in the separate gameplay review, not counted as a failed engine process here. No broad timeout/kill failure injection was performed.

For publication, retain eleven copied source files, manifest, raw streams, parsed records, receipt and the five copied project inputs per mode; exclude incidental environment/cache/pycache directories. Do not run the archived runner in place when reproducing. The independent static checker has no current-engine dependency and supports relocated source/evidence paths while checking historical command paths lexically.
