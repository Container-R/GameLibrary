# Main inspection: NativeArray wrapper ownership and disposal

2026-11-01. Direct official tag lookup resolved `Unity-Technologies/UnityCsReference` tag `6000.0.0f1` to commit `0d0e6a11923ed73f1e8481eb5a6b2e67fe5ddc09`; commit metadata was separately opened. This identifies reference source, not an installed executable or a verified engine/package combination.

Read fixed `Runtime/Export/NativeArray/NativeArray.cs` 34–67, 156–270 and 924–947, blob `6f6cb8ff9668767258be0bba32fdece3615d2ff8`; `Runtime/Jobs/ScriptBindings/JobHandle.bindings.cs` 22–28 and 74–100, blob `3a3588030535407f942792904ef397eebdc94466`. The main pass followed receiver-field updates, scheduling, the returned handle and the disposal job's eventual call site separately.

Read official [Collections allocator overview](https://docs.unity3d.com/Packages/com.unity.collections@2.1/manual/allocator-overview.html), deallocation and IsCreated sections, and [aliasing allocators](https://docs.unity3d.com/Packages/com.unity.collections@2.1/manual/allocator-aliasing.html). Both page metadata identify Collections 2.1.4, generated 2024-04-02; that document identity is separate from the fixed engine source. View examples are not generalized into a rule for plain owning-struct copies.

Read Unity 6000.0 [CombineDependencies](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/Unity.Jobs.JobHandle.CombineDependencies.html), Description and example, and [Complete](https://docs.unity.com/en-us/engine/6000.0/script-reference/unity/jobs/jobhandle/complete), Definition and Remarks. The latter was reached through an official documentation redirect. These are public API contracts; the native scheduler's implementation remains outside the inspected source. No source was authenticated merely from a method's name.

Accepted analysis scope: a successfully allocated ordinary Persistent array, successful lawful disposal, and explicit application ownership/dependency premises. The two proposed state counterexamples are symbolic deductions, not observed timings or error messages. The release protocol must distinguish prior consumers already covered by valid dependencies from newly admitted borrowers; clearing one wrapper does not announce physical free completion.

No Unity, Burst, allocation, job, unsafe access or safety-check configuration was executed. No existing runtime record was opened or inherited. No exact exception, crash, timing window, general alias API or complete concurrent-owner implementation is certified.
