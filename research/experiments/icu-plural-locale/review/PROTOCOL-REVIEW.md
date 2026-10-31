# Independent frozen protocol acceptance

2026-10-31 23:01 UTC. Read-only review of `research-drafts/icu-plural-locale/protocol.json`, SHA256 `e44d2d3a7463eeb2669ad1a3ad37d894611d792ee3221642b1d459dda32d377c`. No implementation, import of legacy executable module, CDLL or native call performed.

Accepted for implementation subject to a separate pre-native code review. The protocol pins the immutable source review `56cf6e4f…`, source gate and current LOC article rather than assuming prior runtime evidence establishes this locale extension.

- Literal patterns, six integers and all eighteen expected ASCII outputs match the independently derived cardinal rule table. The intentional Arabic few omission is correctly expected to format OTHER for3 while separately failing the FEW target-intent contract. English numeric tests do not imply Arabic/full-language coverage.
- Linux x86_64/little-endian pointer8, signed32 status/length, uint16 UTF-16 units, double8 and UParseError72/offsets0,4,8,40 preserve the narrow existing ABI. Open pointer return, format signed length, close/version void and explicit one variadic double match the primary declarations. Bind-all-before-call prevents partial API availability from beginning formatting.
- Status<=0 warning semantics are retained, not hidden; output reads require nonnegative bounded length below64 and success status. Open nonnull is not itself success. Every nonnull formatter is closed in finally, including error-status opens. No error-name helper calls inflate unrecorded call counts.
- Successful per-config maximum is nine function calls: version1/open1/format6/close1; three fresh configurations imply27, not eighteen total native calls. Each attempt/return is separately flushed; CDLL loads are separately identified and not counted as these API calls. First unexpected failure prevents later inputs/configurations.
- Exact file paths/hashes are checked before loading resolved uc/i18n paths and again after cleanup; this does not authenticate all runtime dependencies/data. The minimal environment omits ICU_DATA and loader overrides, uses the exact reviewed helper and fresh owned directories, and is not described as a sandbox.
- Unique STARTED/terminal receipts, own-process-group timeout handling and post-leader group inspection prevent stale success consumption. Interrupted close remains incomplete; timeout does not promise universal cleanup. Static consumer must use frozen literal ABI/outputs and enforce exact typed metadata rather than trusting a claimed success class.

No material protocol correction requested. Approval here is for the written bounded protocol, not authorization to execute a native child or an independent repeat. No reported source-review bytes were modified by this acceptance.
