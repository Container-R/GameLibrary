# Main integrator source review before native execution

2026-10-31 22:41 UTC. No native probe or loader load by main.

Read current matrix article (94f58229 prefix), preserving its actual shaderc compilation plus CPU interpretation verification method. Any later Vulkan capability result is separate fixture identity, not an upgrade of its existing GLSL result into executed shader output.

Directly read official current VkInstanceCreateInfo, VkApplicationInfo, vkCreateInstance and vkEnumeratePhysicalDevices reference pages at 22:37, vkDestroyInstance at 22:40. NULL application info permits the API 1.0 request; NULL allocator must match destroy. No child API resources are proposed. Refpages are moving latest, not installed loader source identity.

Read fixed Vulkan-Headers b379292b2ab6df5771ba9870d53cf8b2c9295daf vk_platform.h and relevant vulkan_core.h structures/prototypes through GitHub after the web raw-file fetch returned a cache miss. Dispatchable handles are pointers, natural LP64 field layout and ordinary Linux C convention agree with reviewer. No copied implementation/header enters public experiment.

Read pinned Vulkan-Loader aa6dee8385afe4b2cc0152d086af2184743e16fd Linux discovery and override sections. Explicit system XDG directories plus fresh per-run HOME/XDG limit the observation to that environment. Compile-time discovery roots and implicit layers remain possible. Manifest presence would not guarantee its referenced shared library loads; no overrides or dynamic-library-path changes will be used to force a desired result. System directory absence alone does not prove absent hardware.

Accept reviewer precision: validate capacity and nonnull returned range for both successful and incomplete array calls; never consume unknown/error output. Emit call-attempt event before entry and completion event after return with flushed output, so timeout/crash cannot be counted as completed native calls. Only a successful nonnull instance is destroyed, at most once. A bound of 64 is this probe's allocation bound, not a Vulkan limit. No shader, logical device or queue operation follows enumeration in this unit.

Next: accept immutable protocol hash before implementation, inspect code before one bounded native child, independently archive exact outcome. No expected API outcome is treated as a test success criterion.
