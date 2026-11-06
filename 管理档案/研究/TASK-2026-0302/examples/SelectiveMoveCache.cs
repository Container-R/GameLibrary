// Original source-based example for Entities 1.3.15.
// NOT compiled or executed. Read the article's domain, numeric and phase contract.
using System;
using System.Collections.Generic;
using Unity.Burst;
using Unity.Burst.Intrinsics;
using Unity.Collections;
using Unity.Entities;
using Unity.Mathematics;

namespace GameLibraryExamples.SelectiveMoveCache
{
    public struct MoveBase : IComponentData { public float BaseSpeed; }
    public struct MoveFactors : IComponentData { public float Scale; }
    public struct MoveCache : IComponentData { public float AllowedSpeed; }

    [UpdateInGroup(typeof(SimulationSystemGroup))]
    public partial class MovePipelineGroup : ComponentSystemGroup { }

    // All public commands below are main-thread, between-round requests.
    // Domain mutations execute only at this boundary, never inside producer jobs.
    [CreateAfter(typeof(MoveCacheRefreshSystem))]
    [UpdateInGroup(typeof(MovePipelineGroup), OrderFirst = true)]
    public partial class MovePhaseOwnerSystem : SystemBase
    {
        readonly Queue<Action<EntityManager>> _pending = new();
        MoveCacheRefreshSystem _cache;
        float _nextCap = 10f;
        bool _faulted;

        protected override void OnCreate()
        {
            _cache = World.GetExistingSystemManaged<MoveCacheRefreshSystem>();
        }

        public void SetSpeedCap(float cap)
        {
            if (!math.isfinite(cap) || cap < 0f)
                throw new ArgumentOutOfRangeException(nameof(cap));
            _nextCap = cap; // Becomes this phase's immutable scalar at BeginRound.
        }

        public void QueueDomainChange(Action<EntityManager> apply)
        {
            if (apply == null) throw new ArgumentNullException(nameof(apply));
            _pending.Enqueue(apply);
        }

        // A detected input-stage failure must close the pipeline, not publish it.
        // This example stays faulted until the World is rebuilt.
        public void Fault()
        {
            _faulted = true;
            _cache.AbortRound();
        }

        protected override void OnUpdate()
        {
            if (_faulted) { _cache.AbortRound(); return; }
            _cache.BeginRound(_nextCap);
            try
            {
                if (_pending.Count != 0)
                {
                    _cache.InvalidateAll(); // Before any mutation or admission.
                    EntityManager.CompleteAllTrackedJobs();
                    while (_pending.Count != 0)
                        _pending.Dequeue()(EntityManager);
                }
            }
            catch
            {
                Fault();
                throw;
            }
        }

        protected override void OnStopRunning() => _cache.AbortRound();
    }

    [CreateAfter(typeof(MoveCacheRefreshSystem))]
    [UpdateInGroup(typeof(MovePipelineGroup))]
    [UpdateAfter(typeof(MovePhaseOwnerSystem))]
    public partial class MoveInputGroup : ComponentSystemGroup
    {
        MoveCacheRefreshSystem _cache;
        protected override void OnCreate()
        {
            base.OnCreate();
            _cache = World.GetExistingSystemManaged<MoveCacheRefreshSystem>();
        }
        protected override void OnUpdate()
        {
            if (_cache.InputsOpen) base.OnUpdate();
        }
    }

    [UpdateInGroup(typeof(MovePipelineGroup))]
    [UpdateAfter(typeof(MoveInputGroup))]
    public partial class MoveCacheRefreshSystem : SystemBase
    {
        EntityQuery _domain;
        ComponentTypeHandle<MoveBase> _baseHandle;
        ComponentTypeHandle<MoveFactors> _factorsHandle;
        ComponentTypeHandle<MoveCache> _cacheHandle;
        bool _forceFull = true;
        bool _armed;
        bool _configured;
        float _cap;
        public bool InputsOpen => _armed;
        public bool Readable { get; private set; }

        protected override void OnCreate()
        {
            _domain = GetEntityQuery(
                ComponentType.ReadOnly<MoveBase>(),
                ComponentType.ReadOnly<MoveFactors>(),
                ComponentType.ReadWrite<MoveCache>());
            // Never attach a changed/shared/order filter to this owned query.
            _baseHandle = GetComponentTypeHandle<MoveBase>(true);
            _factorsHandle = GetComponentTypeHandle<MoveFactors>(true);
            _cacheHandle = GetComponentTypeHandle<MoveCache>(false);
        }

        // Called only by the phase owner, before producers schedule work.
        public void BeginRound(float cap)
        {
            Readable = false;
            _armed = false;
            if (!math.isfinite(cap) || cap < 0f)
                throw new ArgumentOutOfRangeException(nameof(cap));
            if (!_configured || cap != _cap) _forceFull = true;
            _configured = true;
            _cap = cap;
            _armed = true;
        }

        public void InvalidateAll()
        {
            _forceFull = true;
            Readable = false;
        }
        public void CloseReadGate() => Readable = false;
        public void AbortRound()
        {
            _armed = false;
            InvalidateAll();
        }
        protected override void OnStartRunning() => InvalidateAll();
        protected override void OnStopRunning() => AbortRound();

        protected override void OnUpdate()
        {
            Readable = false;
            if (!_armed) { InvalidateAll(); return; }
            _armed = false; // Consume this round's permission exactly once.
            bool fullForThisJob = _forceFull;
            _forceFull = true; // Remains true if scheduling/completion fails.

            _baseHandle.Update(this);
            _factorsHandle.Update(this);
            _cacheHandle.Update(this);
            var job = new RefreshMoveCacheJob
            {
                Base = _baseHandle,
                Factors = _factorsHandle,
                Cache = _cacheHandle,
                Since = LastSystemVersion,
                SpeedCap = _cap,
                ForceFull = fullForThisJob
            };
            Dependency = job.ScheduleParallel(_domain, Dependency);
            // Deliberate synchronization point: publish only completed results.
            Dependency.Complete();
            _forceFull = false;
            Readable = true;
        }
    }

    [BurstCompile]
    public struct RefreshMoveCacheJob : IJobChunk
    {
        [ReadOnly] public ComponentTypeHandle<MoveBase> Base;
        [ReadOnly] public ComponentTypeHandle<MoveFactors> Factors;
        public ComponentTypeHandle<MoveCache> Cache;
        public uint Since;
        public float SpeedCap;
        public bool ForceFull;

        public void Execute(in ArchetypeChunk chunk, int unfilteredChunkIndex,
                            bool useEnabledMask, in v128 chunkEnabledMask)
        {
            if (!ForceFull &&
                !chunk.DidChange(ref Base, Since) &&
                !chunk.DidChange(ref Factors, Since))
                return;

            var bases = chunk.GetNativeArray(ref Base);
            var factors = chunk.GetNativeArray(ref Factors);
            var caches = chunk.GetNativeArray(ref Cache); // RW only AFTER decision.
            var entities = new ChunkEntityEnumerator(
                useEnabledMask, chunkEnabledMask, chunk.Count);
            while (entities.NextEntityIndex(out int i))
            {
                // Contract: operands AND their float product are finite/nonnegative.
                float product = bases[i].BaseSpeed * factors[i].Scale;
                caches[i] = new MoveCache
                {
                    AllowedSpeed = math.clamp(product, 0f, SpeedCap)
                };
            }
        }
    }

    // All legitimate readers belong here and declare MoveCache read-only.
    // Readable gates scheduling; the already scheduled reader jobs remain valid.
    [CreateAfter(typeof(MoveCacheRefreshSystem))]
    [UpdateInGroup(typeof(MovePipelineGroup))]
    [UpdateAfter(typeof(MoveCacheRefreshSystem))]
    public partial class MoveReadGroup : ComponentSystemGroup
    {
        MoveCacheRefreshSystem _cache;
        protected override void OnCreate()
        {
            base.OnCreate();
            _cache = World.GetExistingSystemManaged<MoveCacheRefreshSystem>();
        }
        protected override void OnUpdate()
        {
            if (!_cache.Readable) return;
            try { base.OnUpdate(); }
            finally { _cache.CloseReadGate(); }
        }
    }
}
