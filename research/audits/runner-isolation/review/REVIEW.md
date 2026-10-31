# Independent future-runner isolation helper review

2026-10-31 22:03 UTC. Accepted within the five-key contract; no material issue found.

Copied only isolation.py, test_isolation.py and protocol.json after author freeze. Commands from this review directory: `python -B fixture/test_isolation.py` and `python -B -O fixture/test_isolation.py`; both exit 0, five inherited unittest methods each. Each suite launches exactly one actual synthetic Python child that reports only five selected paths and writes sentinel files. Total two synthetic children, zero engine processes. Raw streams retained in normal/optimized stdout/stderr. Independently parsed both RESULT_JSON records, checked source hashes, counts, optimization flag, child exit and exact selected-key stdout/manifest equality.

Production code copies the base mapping, preflights all reserved names before creation, rejects symlink root components before resolving, validates exact environment strings and existing nonsymlink directories. Missing/redirected keys do not silently fall back. No full parent environment is logged; unrelated keys remain in the returned child environment deliberately, so this is not credential stripping or complete isolation.

`python -B additional.py` and `python -B -O additional.py` each pass four extra filesystem probes: ancestor symlink, explicit parent traversal, dangling reserved symlink, and injected PermissionError at the third directory creation. The injected failure propagates, leaves only the first two newly created directories for caller cleanup, and leaves the input mapping unchanged. These probes launch zero children; the injected exception is synthetic, not an actual filesystem permissions incident. Reports additional.json/additional-optimized.json retained.

Exclusive fresh-root ownership is a caller precondition, not verified security ownership. TOCTOU replacement, concurrent mutation, process lifecycle, other writable locations and historical runner adoption remain excluded. No old fixture/harness/registry changed, no new normal adapter is established, and no Godot crash-prevention claim follows. No unexpected failure occurred in this independent repeat.

## Exact copied sources

- `isolation.py`: `1694c02b779462ee84c3e012094764572612a7fa01801380748752a49d3cd36a`
- `protocol.json`: `2717199e1cb4800b3e42665307657e8257e39ff90863c1e7dfd82fe18251e712`
- `test_isolation.py`: `5c5692cc1dd21f13fcf3f3c40d2c52d16badb442ad093b81bbb78783a0097037`

## Final anchor guard acceptance — 22:04 UTC

Initial evidence above remains unchanged. Final copied sources and new raw streams are under `final/`. Diff inspection confirms only the early filesystem-anchor rejection, a mocked-mkdir negative inside the existing test method, and an explicit protocol amendment. The root test cannot actually write `/` even if the guard regresses. Fresh-root ownership is still a caller precondition; this rejects an obvious misuse, not all inappropriate directories.

From `final/`, `python -B fixture/test_isolation.py` and `python -B -O fixture/test_isolation.py` each exited 0 with five methods and one synthetic child. Parsed results bind final hashes and expected child output. Four extra filesystem probes repeated in each mode (`python -B additional.py`, `python -B -O additional.py`) passed with no children. Exactly two additional reviewer synthetic children; reviewer initial+final total four. Together with the author's separately recorded initial+final four, total eight synthetic children, zero engine processes. Historical review/native counts are not rewritten. No unexpected failure. Final helper accepted.

- Final `isolation.py`: `bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970`
- Final `protocol.json`: `543f5a4b9388dd1bc95350fd78ab284ac31701282e8bfe5a49258bed7f505d26`
- Final `test_isolation.py`: `1a9e1553dbeaacf6cc87e8d90c3c0270b6eb69873d5b6d5ca591704d437d082d`
