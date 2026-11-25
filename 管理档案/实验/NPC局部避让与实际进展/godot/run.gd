extends SceneTree

const DT := 1.0 / 60.0
const TOTAL := 600
const RADIUS := 0.5
const HALF_WIDTH := 1.3
var map: RID
var agents: Array[RID] = []
var pos: Array[Vector2] = [Vector2(-2.5,0),Vector2(2.5,0)]
var goal: Array[Vector2] = [Vector2(2.5,0),Vector2(-2.5,0)]
var lane: Array[float] = [-0.65,0.65]
var safe: Array[Vector2] = [Vector2.ZERO,Vector2.ZERO]
var pref: Array[Vector2] = [Vector2.ZERO,Vector2.ZERO]
var stage: Array[int] = [0,0]
var arrived: Array[int] = [-1,-1]
var callbacks := 0
var min_gap := INF
var min_wall := INF
var max_disagreement := 0.0
var mode := "center"

func _initialize() -> void:
    var args := OS.get_cmdline_user_args()
    if not args.is_empty():
        mode = args[0]
    call_deferred("test")

func on_safe(v: Vector2, id: int) -> void:
    safe[id] = v
    callbacks += 1

func sample_gap(before: Vector2, after: Vector2) -> float:
    var delta := after - before
    var fraction := 0.0
    if delta.length_squared() > 0.0:
        fraction = clampf(-before.dot(delta) / delta.length_squared(),0.0,1.0)
    return (before + fraction*delta).length() - 2.0*RADIUS

func wanted(i: int) -> Vector2:
    if arrived[i] >= 0:
        return Vector2.ZERO
    var target := goal[i]
    if mode != "center":
        if stage[i] == 0 and absf(pos[i].y-lane[i]) < 0.001:
            stage[i] = 1
        if stage[i] == 1 and absf(pos[i].x-goal[i].x) < 0.001:
            stage[i] = 2
        if stage[i] == 0:
            target = Vector2(pos[i].x,lane[i])
        elif stage[i] == 1:
            target.y = lane[i]
    return (target-pos[i]).limit_length(DT*1.0)/DT

func test() -> void:
    var s := NavigationServer2D
    map = s.map_create()
    s.map_set_active(map,true)
    s.map_set_use_async_iterations(map,false)
    for i in range(2):
        var a := s.agent_create()
        agents.append(a)
        s.agent_set_map(a,map)
        s.agent_set_radius(a,RADIUS)
        s.agent_set_max_speed(a,1.0)
        s.agent_set_max_neighbors(a,1)
        s.agent_set_neighbor_distance(a,10.0)
        s.agent_set_time_horizon_agents(a,1.0)
        s.agent_set_avoidance_enabled(a,true)
        s.agent_set_position(a,pos[i])
        s.agent_set_avoidance_callback(a,on_safe.bind(i))
    for k in range(TOTAL):
        await physics_frame
        callbacks = 0
        for i in range(2):
            pref[i] = wanted(i)
            s.agent_set_position(agents[i],pos[i])
            s.agent_set_velocity(agents[i],pref[i])
        await process_frame
        if callbacks != 2:
            print("unexpected callbacks=",callbacks," tick=",k)
            cleanup(2)
            return
        var rel := pos[1]-pos[0]
        var actual: Array[Vector2] = []
        for i in range(2):
            var v := Vector2.ZERO if mode == "blocked_actuator" else safe[i]
            var old := pos[i]
            pos[i] += v*DT
            actual.append((pos[i]-old)/DT)
            max_disagreement = maxf(max_disagreement,actual[i].distance_to(safe[i]))
            min_wall = minf(min_wall,HALF_WIDTH - RADIUS - absf(pos[i].y))
            if arrived[i] < 0 and pos[i].distance_to(goal[i]) < 0.025:
                arrived[i] = k+1
        min_gap = minf(min_gap,sample_gap(rel,pos[1]-pos[0]))
        if k in [0,119,299,599]:
            print("tick=",k+1," A_pos=",pos[0]," B_pos=",pos[1]," A_pref=",pref[0]," A_safe=",safe[0]," A_actual=",actual[0])
    print("RESULT mode=",mode," arrivals=",arrived," min_pair_gap=%.6f min_analytic_wall_gap=%.6f max_safe_actual_delta=%.6f" % [min_gap,min_wall,max_disagreement])
    var valid := min_gap > -0.0002 and min_wall > 0.0
    if mode=="center":
        valid=valid and arrived==[-1,-1] and absf(safe[0].x)<0.05 and absf(pos[0].y)<0.0001
    elif mode=="lanes":
        valid=valid and arrived[0]>0 and arrived[1]>0 and max_disagreement<0.00005 and min_gap>0.25
    elif mode=="blocked_actuator":
        valid=valid and arrived==[-1,-1] and max_disagreement>0.9
    else:
        valid=false
    cleanup(0 if valid else 3)

func cleanup(code: int) -> void:
    for a in agents:
        NavigationServer2D.free_rid(a)
    NavigationServer2D.free_rid(map)
    quit(code)
