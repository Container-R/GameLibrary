# Finite read/write interleaving check

Purpose: check only the article's original two-location arithmetic example, not Noita or native concurrency.

Initial mutable values are x=1, y=2. A reads x once into its own temporary then assigns that value to y. B reads y once into its own temporary then assigns that value to x. Each read/write is an indivisible model event; A's read precedes A's write, likewise B. Enumerate exactly the six permutations satisfying these orders. There are no other reads, state, synchronization, processors or language memory-model effects.

Frozen expected current-state outcomes, written before execution:

| Schedule | Final (x,y) |
|---|---|
| AR AW BR BW | (1,1) |
| AR BR AW BW | (2,1) |
| AR BR BW AW | (2,1) |
| BR BW AR AW | (2,2) |
| BR AR BW AW | (2,1) |
| BR AR AW BW | (2,1) |

For the contrasting immutable-input policy, each read uses the initial snapshot, not the output locations. The two writes still target different output locations. All six permitted schedules must then yield (2,1). This policy is intentionally different from either complete sequential in-place update order. It is not a proof that snapshot-based simulation implements intended gameplay, nor that arbitrary double-buffered systems are race-free.

Model controls: reject duplicate, missing or unknown events and writes before own reads. No I/O beyond reading the program and emitting a compact JSON result; no threads, subprocesses, engine, network, clocks or host metadata. Execution will be distinguished from the pre-execution protocol; results must not be called a real data race or performance measurement.
