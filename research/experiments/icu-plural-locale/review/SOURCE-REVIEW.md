# Independent ICU plural coverage source / ABI gate review

2026-10-31 22:59 UTC. Source review only. No CDLL, ICU call, version call, fixture import, native process or code implementation by this reviewer. Read legacy `case.py` as text only because it executes at module top level.

## Actual existing boundary

Baseline `gamelibrary-publish-allocation-case/solutions/localization/pseudo-localization-contract.md`, SHA256 `2d9ddb7a7e02a32ca442bfb484406736f4c8cacc3ac57d4d7dde20ea21b4c08d`; existing `research/experiments/icu-message-boundary/case.py`, SHA256 `6305b982792337ccab59e0ae23237d2b834683408090e20365840bfa75702e45`.

Existing native evidence uses four English patterns, one positional double, inputs 1.0 and 2.0. It demonstrates syntax corruption and swapped literal messages, not Arabic category coverage. Existing article explicitly does not establish Arabic shaping, bidirectional layout or actual translation quality. The proposed extension must retain those limits.

## Original source sections independently fetched/read

All following paths are in [ICU commit 8eca245c7484ac6cc179e3e5f7c1ea7680810f39](https://github.com/unicode-org/icu/tree/8eca245c7484ac6cc179e3e5f7c1ea7680810f39). No full source archived or implementation copied.

- [umsg.h](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/i18n/unicode/umsg.h), lines 385–416 and 505–527: opaque formatter pointer; UTF-16 pattern and signed 32-bit length; nullable parse-error output; locale C string/status pointer; variadic formatting expects double for ordinary numeric arguments; result length and output capacity are UTF-16 units; close returns void.
- [umsg.cpp](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/i18n/umsg.cpp), format/vformat and `Formattable::kDouble` at lines 426–428: consumes `va_arg(ap, double)`. Freeze precisely one positional numeric argument and pass `ctypes.c_double`; do not generalize this into an arbitrary-pattern varargs wrapper.
- [plurfmt.h](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/i18n/unicode/plurfmt.h), Patterns and Their Interpretation, lines 91–126: `other` is required; missing selected keyword uses `other`. Explicit-number clauses precede keyword selection; offset defaults to zero. The proposed patterns exclude explicit values, offset, `#`, nested formatting and custom number format, so these features do not confound the missing-`few` comparison.
- [msgfmt.cpp](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/i18n/msgfmt.cpp), `PluralSelectorProvider::select`, lines 1952–1997, and `getDefaultNumberFormat`, lines 1828–1839: resolves rules for the locale, inspects number formatting in the `other` submessage, otherwise uses the locale default number formatter. DecimalFormat produces DecimalQuantity for rule selection; the selector is not universally a raw-double-only path.
- [decimfmt.cpp](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/i18n/decimfmt.cpp), `formatToDecimalQuantity`, lines 1565–1590: formatter applies number settings to the quantity used by selection. [number_decimalquantity.cpp](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/i18n/number_decimalquantity.cpp), `getPluralOperand`, lines 271–295: `i` is integer value; `v` comes from visible fraction count. [en.txt](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/data/locales/en.txt), NumberElements/latn/patterns decimalFormat, is `#,##0.###`: no mandatory fractional digit. Thus these exactly representable integer-valued doubles with the unmodified English default format have `v=0`; Python spelling `1.0` does not supply a preserved lexical trailing zero.
- [plurals.txt](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/data/misc/plurals.txt): cardinal locales map `en` to `set3`, `ar` to `set37` (do not accidentally use later ordinal mappings). Set3 one is `i=1 and v=0`; all other chosen integers use other. Set37 zero/one/two are exact 0/1/2; few is n modulo100 in3..10; many is modulo100 in11..99; remaining inputs use other.
- [uvernum.h](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/common/unicode/uvernum.h) declares ICU76.1 and `_76` symbol suffix. [supplementalData.txt](https://github.com/unicode-org/icu/blob/8eca245c7484ac6cc179e3e5f7c1ea7680810f39/icu4c/source/data/misc/supplementalData.txt), `cldrVersion` at line2179, declares46. This is the pinned source's ICU/CLDR relationship, not authentication that installed library/data bytes exactly reproduce that source.

## Independently derived finite oracle

Original marker names below are semantic placeholders for the author's frozen ASCII markers, not Arabic translations. Every test number is an exactly representable nonnegative integer passed as a C double. `ar-omit-few` has all full-pattern clauses except `few` and still has `other`.

| Input | en full | ar full | ar omit few | Target-locale acceptance comparison |
|---:|---|---|---|---|
| 0 | other | zero | zero | unchanged |
| 1 | one | one | one | unchanged |
| 2 | other | two | two | unchanged |
| 3 | other | few | other | deliberate missing-arm mismatch |
| 11 | other | many | many | unchanged |
| 100 | other | other | other | unchanged |

For100, n modulo100 is0 but n itself is not0,1,2, so Arabic chooses other. Omitted few should remain syntactically valid and return the other marker for3. This is correct ICU fallback behavior, not an ICU bug; it violates the separately declared target-locale branch-coverage requirement. English1/2 smoke checks do not traverse the missing Arabic few category.

Six inputs cover these six Arabic named outcomes once in the full pattern, not every rule boundary, residue cycle, fraction, locale variant or complete localization coverage. They do not establish arbitrary trailing-zero semantics: a custom formatter forcing one decimal digit could change English `v`, which is excluded here. Ordinal categories are excluded.

## Pre-code acceptance conditions

Source gate accepted for the narrow proposed three configurations, conditional on immutable literal pattern/input/output protocol before implementation. Three opens and eighteen format calls are the planned author totals, not yet observed calls; separate version/status helper calls must be counted honestly. Freeze UTF-16 buffer capacity, signed status/length guards, Linux ABI checks and handle cleanup; retain negative warnings as observations rather than assuming the old -127 warning will recur. Any returned nonnull handle must be closed on ordinary paths even if opening reports failure. No evaluation after invalid parse, no out-of-range buffer read, no unsupported type/nested pattern execution.

The independent review establishes the source-derived expected table, not actual installed behavior. Any future disagreement must preserve the first failure and stop, not revise the oracle to observed output. Installed source/data provenance remains a comparison boundary; no font/RTL/rendering/Unity/translation approval claim follows from these ASCII branch markers.
