# Main source read — translator explanation and lookup identity

2026-11-01 UTC. Main fully read existing ROLE-LOC-001 and its source record; both selected text files contain no private execution metadata. Existing historical practice attribution remains unchanged. Read official Godot 4.6 Internationalizing games / Translation contexts; Localization using gettext / template generation, extraction comments and Using context; Translation description and message identity. These are mutable versioned documents, not evidence of a local runtime.

Independently resolved official tag 4.6-stable to `89cea143987d564363e15d207438530651d943ac` and confirmed commit timestamp 2026-01-25T12:41:41Z. Read at that pin:

- `modules/gdscript/editor/gdscript_translation_parser_plugin.cpp` 42–78, 81–139, 328–356: parse/analyze and constant-string extraction; translator explanation enters a separate field from id/context.
- `editor/translations/template_generator.cpp` 37–123, 175–213: field separation, MessageKey{msgctxt,msgid}, comment/location collections, POT output with comments versus msgctxt.
- `core/io/translation_loader_po.cpp` 164–320: text PO context reading, singular message insertion and comment handling. Context accumulates in its own variable. Some comments influence skip handling, so a blanket assertion that all comments are inert is incorrect and is not adopted.
- `core/string/translation.h` 44–61 and `translation.cpp` 145–175: both components participate in key equality; add and default get use the same pair. get first permits a virtual override; only the default branch is covered.

The source inference is narrow: for recognized constant singular calls with equal id/context, different translator explanations do not create distinct template keys; comments are associated with that existing key. Valid, non-skipped PO messages carry context to default message storage. This is not a generated POT, loaded locale or screen result. No Object.tr locale/domain fallback chain, custom parser, arbitrary resource, MO/CSV, plural algorithm or malformed-input audit is claimed.

If language reviewers require different messages for two simultaneous Confirm uses, the proposed handoff must carry call-site context, template identity and corresponding locale-entry identity, rather than only a prose explanation. Whether a locale actually needs different wording remains a language decision. No translation or LQA is performed; no installed binary identity, old runtime archive or pending release is used.
