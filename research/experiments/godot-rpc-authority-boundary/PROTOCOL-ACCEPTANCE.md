# Protocol acceptance, implementation only

2026-11-01 00:12 UTC. Main and independent review accept protocol SHA256 86323211989a29ef3a8cdb008fe9789100e2235c5929af979d2743c940c80e6e. Independent review SHA256 1a12cbf4fe9fc634b6252c3c40410826506c117c1422230c7a4db540d010acd8. Candidate header is retained as frozen historical text; this separate acceptance is authoritative for implementation phase.

Authorized now: original fixture/runner/consumer code and pure synthetic/static checks only. No engine/version process, port binding or packets until final source and runner review. No new protocol variants. Three command intents, five control RPCs, one version process and two behavioral processes are maximum per future accepted attempt; failure may prevent later process launch and must report actual counts.

Implementation must distinguish raw Variant integer type before coercion; explicitly disable SceneMultiplayer object decoding with its documented setter/property and record the readback. Main directly read SceneMultiplayer4.6 property59–67 and auth_callback70–76: empty callback accepts peers automatically, so this is not account authentication. Default SceneTree polling suffices; no recursive polling in deferred validator. Main read MultiplayerAPI.poll146–149.

Client readiness uses both CONNECTED and valid welcome, independent of ordering. Parent retains fragmented raw streams, validates complete terminal payloads and finish confirmation before fresh STOP barrier; bounded cleanup failure is a failed attempt, not containment proof. Preserve all failures and source identities.
