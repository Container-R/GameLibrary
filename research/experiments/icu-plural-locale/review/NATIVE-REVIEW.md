# Independent finite native repeat acceptance

2026-10-31 23:08 UTC. Main authorized exactly one independent three-configuration repeat at 23:07:35 UTC after author batch and pre-native source acceptance. No retry, added locale, input, formatting helper or exploratory native call was performed.

Reviewed source bytes are copied unchanged in `final-source/`; protocol e44d2d3a, child e4f879c4, runner d1013713, consumer a20cbbce. Parent command output/error are preserved as `native-parent-stdout.txt` / `native-parent-stderr.txt`.

Actual reviewer batch: **51693796-d462-4068-8d93-cf96d488eb99**.

| Configuration | Actual child UUID | Outputs for0,1,2,3,11,100 |
|---|---|---|
| en_full | e3400eeb-07ca-4b43-bf66-f84792719c0f | OTHER, ONE, OTHER, OTHER, OTHER, OTHER |
| ar_full | 9178dad8-4087-4da2-923f-6c91cd36d9e3 | ZERO, ONE, TWO, FEW, MANY, OTHER |
| ar_omit_few | 6107b93c-3894-4178-9ce8-fa9ca851f065 | ZERO, ONE, TWO, OTHER, MANY, OTHER |

Each child records version1/open1/format6/close1, both attempted and returned:27 actual ICU calls per complete batch, including18 formatting calls, not18 total API calls. Library loads are separately traced and not included in this API count. Open status0; first format for n0 returns warning-127 in each process; remaining format statuses0. Warnings are retained without attributing their cause. All children exit0 with empty stderr, no timeout and no observed remaining owned process group. Source/library before/after identities agree with the frozen pins. No native pointer addresses are reported.

`check_raw.py` is a separate standard-library-only checker with independently literal expected tables; it imports neither author selector/consumer nor native child. It verifies raw trace order, version/open/format/close lifecycle, exact locale/pattern/input, status and bounded UTF-16 decoding, marker outputs, fallback intent, process outcomes and source/raw/receipt hashes. Its successful records are `native-independent-check.json` and `author-independent-check.json`. The latter checks the already completed author batch2f4f411a without rerunning it.

Reproduction of static checks from this review directory (no native calls):

```sh
python check_raw.py native-repeat/51693796-d462-4068-8d93-cf96d488eb99 final-source
```

The independently observed result agrees with the source-derived contract. Missing Arabic few remains syntactically valid and selects OTHER at3, while the explicitly declared full-category intent expects FEW. This is a meaningful target-locale branch-coverage counterexample, not ICU failure or a linguistic correctness judgment.

Combined author+reviewer evidence is six fresh children and54 ICU calls, including36 formatting calls across repeated versions of the same three configurations and six inputs. Do not present repeats as additional locales or novel cases. Native result does not authenticate CLDR resource provenance, prove complete integer/fraction coverage, or establish translation quality, Arabic shaping, fonts, RTL layout or Unity behavior. No remaining material blocker for a narrowly scoped existing-article supplement.
