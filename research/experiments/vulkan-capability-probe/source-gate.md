# Vulkan capability gate: loader is not an enumerated device

2026-10-31 22:35 UTC. Source and read-only filesystem gate only. **No ctypes library load, Vulkan API call, probe code, compilation or engine execution performed.**

## Current article boundary actually read

`gamelibrary-work/solutions/rendering/matrix-major-interface-contract.md` SHA256 `94f58229014b70f246d3c70e80d11a29274524cc6355e680b8a5b3b3a2b90b3c`.

Exact metadata:
> verification_method: 固定官方规范与 C API 核对；两个实际编译进程及独立同库复跑，字面 assembly/host bytes 判据，三个启动失败负例；CPU 数值解释，不含 shader 执行

Actual libshaderc compilation and SPIR-V consumption-chain review do not execute a shader, bind buffers, dispatch compute or read GPU results. Neither a Vulkan loader library nor a successful instance/device enumeration would close that execution gap. This gate determines whether a later proposal has a usable initial runtime surface, or documents a precise environment obstacle and stops.

## Observed limited capability scan

Read-only system paths, no private home/credential or full-environment inspection:
- `/etc/vulkan/icd.d` exists, no JSON entries.
- `/etc/xdg/vulkan/icd.d`, `/usr/local/etc/vulkan/icd.d`, `/usr/local/share/vulkan/icd.d`, `/usr/share/vulkan/icd.d` absent.
- `/usr/include/vulkan/vulkan.h` absent. command-v finds `/usr/bin/cc`; not vulkaninfo, glslangValidator or clang.
- ldconfig lists `/lib/x86_64-linux-gnu/libvulkan.so.1`; resolved file `/usr/lib/x86_64-linux-gnu/libvulkan.so.1.4.309`, SHA256 `bbd6827e9fe418e9b9740aea57ce6d21fcea03e9876b4b17835c5a9c58f849fc`. Filename is not authenticated build/version provenance.
- Presence-only checks found no VK_DRIVER_FILES, VK_ICD_FILENAMES, VK_ADD_DRIVER_FILES, VK_INSTANCE_LAYERS, VK_LAYER_PATH, VK_LOADER_DRIVERS_SELECT or VK_LOADER_DRIVERS_DISABLE. No environment values dumped.

These directories are a bounded list, **not an exhaustive search of every possible driver location or physical hardware**. No user-specific ICD dirs inspected. Loader build-time paths, permissions, implicit layers and environment can affect discovery.

## Primary source pins and exact sections

1. Khronos Vulkan-Headers tag `v1.3.290` resolved through GitHub API tag ref to commit **`b379292b2ab6df5771ba9870d53cf8b2c9295daf`**. Exact pinned header was read and matched the tag content:
https://github.com/KhronosGroup/Vulkan-Headers/blob/b379292b2ab6df5771ba9870d53cf8b2c9295daf/include/vulkan/vulkan_core.h
Sections: VK_DEFINE_HANDLE, VkFlags/VkResult/VkStructureType, VkApplicationInfo, VkInstanceCreateInfo and PFN_vkCreateInstance/PFN_vkEnumeratePhysicalDevices/PFN_vkDestroyInstance.
2. Same pin calling convention:
https://github.com/KhronosGroup/Vulkan-Headers/blob/b379292b2ab6df5771ba9870d53cf8b2c9295daf/include/vulkan/vk_platform.h
Linux/default convention is ordinary C (unlike Windows stdcall). Only Linux x86_64 LP64 proposed; no portable-all-ABI claim.
3. Khronos Vulkan-Loader `main` resolved to **`aa6dee8385afe4b2cc0152d086af2184743e16fd`**, commit timestamp2026-10-30T14:54:36Z; exact pinned doc read:
https://github.com/KhronosGroup/Vulkan-Loader/blob/aa6dee8385afe4b2cc0152d086af2184743e16fd/docs/LoaderDriverInterface.md
Sections Driver Discovery on Linux / Overriding Default Driver Discovery. System/XDG directories receive vulkan/icd.d suffix; override variables can replace discovery. This is a comparison document, not proof the installed loader was built from this commit.
4. Official refpages (moving latest, accessed2026-10-31; API definitions cross-checked with fixed header):
- https://docs.vulkan.org/refpages/latest/refpages/source/VkInstanceCreateInfo.html — field definitions and valid usage.
- https://docs.vulkan.org/refpages/latest/refpages/source/VkApplicationInfo.html — NULL application-info is equivalent to requesting Vulkan1.0; avoids needing a second structure or version negotiation.
- https://docs.vulkan.org/refpages/latest/refpages/source/vkCreateInstance.html — valid parameters and result codes.
- https://docs.vulkan.org/refpages/latest/refpages/source/vkEnumeratePhysicalDevices.html — count query then bounded array fill, possible VK_INCOMPLETE.
- https://docs.vulkan.org/refpages/latest/refpages/source/vkDestroyInstance.html — matching NULL allocator and cleanup obligations.

No third-party implementation copied, driver/header installed, schema bulk archived or mirror used.

## Proposed ABI contract, to freeze before code

One isolated Python child, ctypes.CDLL on the exact system loader path. Before loading native library, reject unless platform Linux x86_64, pointer8, c_int32/c_uint32 size4, pointer alignment8 and the following structure offsets/size match. No `_pack_`; use native alignment. `VkResult`/`VkStructureType` represented as signed32, flags/counts unsigned32; dispatchable VkInstance/VkPhysicalDevice handles represented as opaque pointers, not uint32 or inferred GPU identities.

`VkInstanceCreateInfo`, total64 bytes, alignment8:

| Field | ctypes representation | offset | value |
|---|---|---:|---|
| sType | c_int32 | 0 | 1 (INSTANCE_CREATE_INFO) |
| pNext | c_void_p | 8 | NULL |
| flags | c_uint32 | 16 | 0 |
| pApplicationInfo | c_void_p, NULL only | 24 | NULL (Vulkan1.0 semantics) |
| enabledLayerCount | c_uint32 | 32 | 0 |
| ppEnabledLayerNames | POINTER(c_char_p) | 40 | NULL |
| enabledExtensionCount | c_uint32 | 48 | 0 |
| ppEnabledExtensionNames | POINTER(c_char_p) | 56 | NULL |

Explicit function signatures, no varargs/default-int pointer truncation:
- vkCreateInstance: `(POINTER(CreateInfo), c_void_p, POINTER(c_void_p)) -> c_int32`; allocatorNULL, output initializedNULL.
- vkEnumeratePhysicalDevices: `(c_void_p, POINTER(c_uint32), POINTER(c_void_p)) -> c_int32`.
- vkDestroyInstance: `(c_void_p, c_void_p) -> None`; allocatorNULL, once only for successfully created nonnull instance, in finally on normal Python error paths. A process kill/crash cannot guarantee destructor execution.

Bind all three symbols before create; missing symbols are a loader-binding obstacle, not proof of absent device. No VkDevice creation, queue/property query, shader module, pipeline, buffer, dispatch, rendering or surface extensions. No downloaded code executed.

## Proposed fixed call and outcome protocol

One native child, parent20-second timeout, unique invocation directory with STARTED then terminal report; capture returncode/raw stdout/stderr/source and loader hashes/ABI readbacks plus numbered call trace. No blanket PASS meaning shader support. Avoid printing native handle addresses; record only nonnull/count facts. API call counts are actual increments, not claimed from constant configuration.

1. Call create **once** with above frozen input.
2. If result nonzero: preserve exact signed VkResult/name if recognized and raw diagnostics; never enumerate/destroy an uncreated handle. In particular -9 is VK_ERROR_INCOMPATIBLE_DRIVER **for this requested API and scoped environment**, not a universal “no GPU” assertion. Other codes/unknowns are reported distinctly, not forced into expected success.
3. On VK_SUCCESS require nonnull instance; invalid success/NULL is a protocol anomaly, stop.
4. Enumerate count **once**, pPhysicalDevicesNULL. Only VK_SUCCESS permits consuming returned count. Negative/unexpected result is ENUMERATION_FAILED/UNEXPECTED_RESULT; then cleanup.
5. If count0: record ENUMERATED_ZERO, no fill call. This means no devices enumerated through that instance, not no physical hardware.
6. If count1..64: allocate exactly that many opaque-handle slots and call fill **once**, passing capacity in count. VK_SUCCESS reports returned count<=capacity and nonnull returned handles; VK_INCOMPLETE reports partial discovery, not complete count. Do not retry or grow arrays in this bounded gate. Count>64 records COUNT_EXCEEDS_PROBE_BOUND without allocating; it is not a device failure. Do not consume array on error.
7. Destroy successfully created instance once, no child Vulkan objects were created. Stop even if devices are found: existence is not capability, a physical-device handle may represent software implementation, and shader execution needs a separate approved protocol.

Result categories must distinguish loader unavailable/binding failure, ABI guard failure, instance creation failure, enumeration failure, zero/nonzero/partial enumeration, count-bound limitation, timeout/crash and protocol anomaly. Preserve stderr rather than assuming every loader diagnostic is expected or treating native nonzero as Python success. Successful capture of a negative API result is an observation, not an accepted GPU test.

## Scoped environment and safety limits

Use fresh temporary HOME/XDG_CONFIG_HOME/XDG_DATA_HOME/XDG_CACHE_HOME/TMPDIR, explicitly fixed XDG_CONFIG_DIRS=/etc/xdg and XDG_DATA_DIRS=/usr/local/share:/usr/share. No personal manifest scans. Build a minimal child environment, without inherited VK override/layer/filter variables or LD_PRELOAD/LD_LIBRARY_PATH; no driver-selection variable is set to an empty folder to manufacture failure. Record this isolation as a **system-path-only scoped probe**, not the untouched user desktop environment. No explicit layers/extensions requested; system implicit layers, if any, remain a loader behavior, not asserted absent. No debug environment producing unrelated inventories needed.

ctypes is native execution and can fail despite type checks. Parent timeout bounds waiting, not universal cleanup or OS safety. All probe failures remain immutable evidence; no privilege escalation, driver search outside agreed system paths, installation, alternate API or arbitrary retry to make it pass. A missing/incompatible-driver result is sufficient reason to stop this shader-execution branch and continue other library work.

## Recommendation

Approve one minimal scoped capability invocation only after ABI/control review. It can replace a vague “not tested” with an exact loader/instance/enumeration obstacle or candidate capability. It **cannot** upgrade the current matrix article from compile+CPU interpretation to shader execution. If no usable discovery, retain that precise negative and do not install software just to enlarge article evidence.
