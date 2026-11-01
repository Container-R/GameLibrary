# Main source reading: build ordering and generated-file invalidation

2026-11-01 UTC. Read complete existing ROLE-ENGINE-001, SHA-256 `86b87bcb71d496fdd15e0d647180d289f37a64ab801ca70eb727b55ed4ea8a3e`, and its source note. Existing Cygames case establishes CI-generated inputs, not the CMake mechanism or a diagnosed studio incident.

Direct connector reads of Kitware/CMake fixed commit `6acf7153156bb45038be62e79a32ed5a6ea2d00e`:

- [add_custom_command.rst](https://github.com/Kitware/CMake/blob/6acf7153156bb45038be62e79a32ed5a6ea2d00e/Help/command/add_custom_command.rst#L102-L206),102–206: full TARGET_FILE expressions in command/arguments add ordering; not the executable file dependency needed for regeneration on recompilation. DEPENDS names for executable/library targets add that file-level dependency as well as ordering.
- [CMP0112.rst](https://github.com/Kitware/CMake/blob/6acf7153156bb45038be62e79a32ed5a6ea2d00e/Help/policy/CMP0112.rst), complete policy: component expressions such as TARGET_FILE_DIR/NAME have separate policy behavior. Do not generalize full TARGET_FILE to every target-related expression.

Main independently resolved official `v3.31.12` to annotated tag `652f4bb8113887a924eab3a379074ee47f1c2d88`, whose object is the commit above. This pins documentation, not local tool authenticity or generated Ninja behavior. No configure, compile, asset generation, timestamp experiment, benchmark or runtime archive inspection.

The proposed original asset_packer example separates source-table changes from tool executable changes after output already exists. A clean build cannot alone demonstrate the missing tool-to-output invalidation edge. Scope remains one native executable target, same-directory rule, explicitly known inputs and one output; no proof that target dependency captures all files, plugins, environment, caches or external services consumed by the tool.
