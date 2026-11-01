extends SceneTree
var root_node: Node3D
var map_rid: RID
var regions: Array[RID] = []
var meshes: Array[NavigationMesh] = []
var parents: Array[Node3D] = []
var agents: Array[NavigationAgent3D] = []
var finished_flags = [false, false]
var events: Array = []
var snapshots: Array = []
var ready_record: Dictionary = {}
var initial_paths: Array = []
var initial_identities: Array = []
var current_step = 0
var physics_count = 0
var phase = "setup"
var current_call = "none"
var map_matched = false
var submitted = false
var closed = false
var initial_iteration = 0
const TARGETS = [Vector3(8,0,2),Vector3(22,0,2)]
const ENDS = [Vector3(8,0,2),Vector3(10,0,2)]
const LABELS = ["Reachable","Partial"]
const EPS = 0.00001
func xyz(v: Vector3) -> Array: return [v.x,v.y,v.z]
func points(a) -> Array:
 var out=[]
 for v in a: out.append(xyz(v))
 return out
func fail(reason: String) -> void:
 if closed:return
 closed=true
 print("FAIL_JSON="+JSON.stringify({"reason":reason,"phase":phase,"step":current_step,"events":events,"snapshots":snapshots}))
 quit(1)
func event(kind: String, index: int, extra: Dictionary = {}) -> void:
 if closed:return
 var row={"kind":kind,"agent":index,"step":current_step,"frame":Engine.get_physics_frames(),"phase":phase,"call":current_call}
 if index>=0:
  row["agent_id"]=agents[index].get_instance_id();row["parent_id"]=parents[index].get_instance_id();row["position"]=xyz(parents[index].global_position)
 row.merge(extra);events.append(row)
func on_signal(index: int, label: String) -> void:
 if closed:return
 event("signal",index,{"signal":label})
 if label=="navigation_finished":finished_flags[index]=true
func on_waypoint(details: Dictionary,index: int) -> void:
 if closed:return
 event("signal",index,{"signal":"waypoint_reached","waypoint":xyz(details["position"])})
func _initialize() -> void:
 root_node=Node3D.new();root_node.name="Fixture";root.add_child(root_node)
 NavigationServer3D.map_changed.connect(func(r):
  if r==map_rid:map_matched=true)
 map_rid=NavigationServer3D.map_create();initial_iteration=NavigationServer3D.map_get_iteration_id(map_rid)
 NavigationServer3D.map_set_active(map_rid,true);NavigationServer3D.map_set_up(map_rid,Vector3.UP)
 NavigationServer3D.map_set_use_async_iterations(map_rid,false);NavigationServer3D.map_set_use_edge_connections(map_rid,false)
 NavigationServer3D.map_set_cell_size(map_rid,0.25);NavigationServer3D.map_set_cell_height(map_rid,0.25)
 for x in [0.0,20.0]:
  var mesh=NavigationMesh.new();mesh.vertices=PackedVector3Array([Vector3(x,0,0),Vector3(x,0,4),Vector3(x+10,0,4),Vector3(x+10,0,0)]);mesh.add_polygon(PackedInt32Array([0,1,2,3]));meshes.append(mesh)
  var region=NavigationServer3D.region_create();regions.append(region)
  NavigationServer3D.region_set_use_async_iterations(region,false);NavigationServer3D.region_set_enabled(region,true)
  NavigationServer3D.region_set_navigation_layers(region,1);NavigationServer3D.region_set_navigation_mesh(region,mesh);NavigationServer3D.region_set_map(region,map_rid)
 physics_frame.connect(tick)
func settings(a: NavigationAgent3D) -> Dictionary:
 var d={}
 for k in ["navigation_layers","avoidance_enabled","path_height_offset","path_desired_distance","target_desired_distance","path_max_distance","simplify_path","path_return_max_length","path_return_max_radius","path_search_max_distance","path_search_max_polygons","pathfinding_algorithm","path_postprocessing","path_metadata_flags"]:d[k]=a.get(k)
 return d
func ready_gate() -> bool:
 if not map_matched or NavigationServer3D.map_get_iteration_id(map_rid)==0 or NavigationServer3D.map_get_iteration_id(map_rid)==initial_iteration:return false
 for r in regions:
  if NavigationServer3D.region_get_iteration_id(r)==0:return false
 var rr=[]
 for r in regions:
  rr.append({"id":r.get_id(),"iteration":NavigationServer3D.region_get_iteration_id(r),"map":NavigationServer3D.region_get_map(r).get_id(),"enabled":NavigationServer3D.region_get_enabled(r),"layers":NavigationServer3D.region_get_navigation_layers(r),"async":NavigationServer3D.region_get_use_async_iterations(r)})
 ready_record={"readiness_callbacks":physics_count,"map_id":map_rid.get_id(),"initial_iteration":initial_iteration,"iteration":NavigationServer3D.map_get_iteration_id(map_rid),"matched":map_matched,"regions":rr,"registered":Array(NavigationServer3D.map_get_regions(map_rid)).map(func(r):return r.get_id()),"links":NavigationServer3D.map_get_links(map_rid).size(),"active":NavigationServer3D.map_is_active(map_rid),"async":NavigationServer3D.map_get_use_async_iterations(map_rid),"edge_connections":NavigationServer3D.map_get_use_edge_connections(map_rid),"up":xyz(NavigationServer3D.map_get_up(map_rid)),"cell_size":NavigationServer3D.map_get_cell_size(map_rid),"cell_height":NavigationServer3D.map_get_cell_height(map_rid),"projections":[]}
 if ready_record["registered"].size()!=2 or ready_record["links"]!=0 or not ready_record["active"] or ready_record["async"] or ready_record["edge_connections"] or not NavigationServer3D.map_get_up(map_rid).is_equal_approx(Vector3.UP):fail("map config");return false
 if abs(ready_record["cell_size"]-0.25)>EPS or abs(ready_record["cell_height"]-0.25)>EPS:fail("cell settings");return false
 for r in regions:
  if not ready_record["registered"].has(r.get_id()):fail("registered region set");return false
 for i in range(2):
  if rr[i]["map"]!=map_rid.get_id() or not rr[i]["enabled"] or rr[i]["layers"]!=1 or rr[i]["async"]:fail("region config");return false
 for item in [[Vector3(2,0,2),0],[TARGETS[0],0],[TARGETS[1],1]]:
  var point=NavigationServer3D.map_get_closest_point(map_rid,item[0]);var owner=NavigationServer3D.map_get_closest_point_owner(map_rid,item[0])
  ready_record["projections"].append({"input":xyz(item[0]),"point":xyz(point),"owner":owner.get_id()})
  if point.distance_to(item[0])>EPS or owner!=regions[item[1]]:fail("projection");return false
 return true
func identity(i: int) -> Dictionary:
 return {"label":LABELS[i],"agent_id":agents[i].get_instance_id(),"parent_id":parents[i].get_instance_id(),"actual_parent_id":agents[i].get_parent().get_instance_id(),"root_id":parents[i].get_parent().get_instance_id(),"map_id":agents[i].get_navigation_map().get_id(),"settings":settings(agents[i])}
func setup_agents() -> void:
 for i in range(2):
  var p=Node3D.new();p.name=LABELS[i];root_node.add_child(p);p.global_position=Vector3(2,0,2);parents.append(p)
  var a=NavigationAgent3D.new();a.name="Agent";p.add_child(a);agents.append(a)
  a.navigation_layers=1;a.avoidance_enabled=false;a.path_height_offset=0;a.path_desired_distance=0.1;a.target_desired_distance=0.1;a.path_max_distance=1.0;a.simplify_path=false
  a.path_return_max_length=0;a.path_return_max_radius=0;a.path_search_max_distance=0;a.path_search_max_polygons=4096;a.pathfinding_algorithm=0;a.path_postprocessing=0;a.path_metadata_flags=7
  a.set_navigation_map(map_rid)
  a.path_changed.connect(on_signal.bind(i,"path_changed"));a.target_reached.connect(on_signal.bind(i,"target_reached"));a.navigation_finished.connect(on_signal.bind(i,"navigation_finished"));a.waypoint_reached.connect(on_waypoint.bind(i))
  var observed=identity(i);initial_identities.append(observed)
  var expected={"navigation_layers":1,"avoidance_enabled":false,"path_height_offset":0,"path_desired_distance":0.1,"target_desired_distance":0.1,"path_max_distance":1.0,"simplify_path":false,"path_return_max_length":0,"path_return_max_radius":0,"path_search_max_distance":0,"path_search_max_polygons":4096,"pathfinding_algorithm":0,"path_postprocessing":0,"path_metadata_flags":7}
  for k in expected:
   if typeof(expected[k])==TYPE_BOOL:
    if observed["settings"][k]!=expected[k]:fail("agent bool config");return
   elif abs(float(observed["settings"][k])-float(expected[k]))>EPS:fail("agent numeric config");return
  if observed["map_id"]!=map_rid.get_id() or observed["actual_parent_id"]!=parents[i].get_instance_id() or observed["root_id"]!=root_node.get_instance_id():fail("agent graph config");return
 for i in range(2):agents[i].target_position=TARGETS[i]
 submitted=true;phase="waiting_first_update"
func query_one(i: int) -> Dictionary:
 var a=agents[i];phase="queries";event("before_update",i)
 current_call="get_next_path_position";event("call_enter",i);var next=a.get_next_path_position();event("call_return",i,{"value":xyz(next)})
 current_call="is_navigation_finished";event("call_enter",i);var done=a.is_navigation_finished();event("call_return",i,{"value":done})
 current_call="is_target_reachable";event("call_enter",i);var reachable=a.is_target_reachable();event("call_return",i,{"value":reachable})
 current_call="get_final_position";event("call_enter",i);var last=a.get_final_position();event("call_return",i,{"value":xyz(last)})
 current_call="none"
 var row={"agent":i,"step":current_step,"frame":Engine.get_physics_frames(),"parent":xyz(parents[i].global_position),"next":xyz(next),"finished":done,"reachable":reachable,"reached":a.is_target_reached(),"final":xyz(last),"path":points(a.get_current_navigation_path()),"index":a.get_current_navigation_path_index(),"distance":a.distance_to_target()}
 snapshots.append(row);event("after_queries",i,{"snapshot":row})
 if done!=finished_flags[i]:fail("finish latch mismatch")
 return row
func valid_path(row: Dictionary,i: int) -> bool:
 var path=row["path"]
 if path.is_empty():return false
 if Vector3(path[0][0],path[0][1],path[0][2]).distance_to(Vector3(2,0,2))>EPS:return false
 var prior=2.0
 for v in path:
  if not is_finite(v[0]) or not is_finite(v[1]) or not is_finite(v[2]) or abs(v[1])>EPS or abs(v[2]-2)>EPS or v[0]<prior-EPS or v[0]>ENDS[i].x+EPS:return false
  prior=v[0]
 return abs(prior-ENDS[i].x)<=EPS and Vector3(row["final"][0],row["final"][1],row["final"][2]).distance_to(ENDS[i])<=EPS
func tick() -> void:
 if closed:return
 physics_count+=1
 if not submitted:
  if physics_count>240:fail("readiness watchdog");return
  if ready_gate() and not closed:setup_agents()
  return
 current_step+=1
 if current_step>48:fail("driver watchdog");return
 var rows={}
 for i in range(2):
  if finished_flags[i]:continue
  rows[i]=query_one(i)
  if closed:return
  if not valid_path(rows[i],i):fail("path gate");return
  if rows[i]["reachable"]!=(i==0):fail("reachability changed");return
  if current_step==1 and (rows[i]["finished"] or rows[i]["reached"] or rows[i]["reachable"]!=(i==0)):fail("initial state");return
 if current_step==1:initial_paths=[rows[0]["path"],rows[1]["path"]]
 for i in range(2):
  if finished_flags[i]:continue
  phase="movement"
  var n=rows[i]["next"];var next=Vector3(n[0],n[1],n[2]);var old=parents[i].global_position;var wanted=old.move_toward(next,0.5)
  parents[i].global_position=wanted
  event("position_assigned",i,{"old":xyz(old),"next":xyz(next),"computed":xyz(wanted)})
 if finished_flags[0] and finished_flags[1]:complete()
func complete() -> void:
 phase="complete"
 var identities=[];var geometry=[]
 for i in range(2):
  identities.append({"label":LABELS[i],"agent_id":agents[i].get_instance_id(),"parent_id":parents[i].get_instance_id(),"actual_parent_id":agents[i].get_parent().get_instance_id(),"root_id":parents[i].get_parent().get_instance_id(),"map_id":agents[i].get_navigation_map().get_id(),"settings":settings(agents[i]),"target":xyz(agents[i].target_position)})
  geometry.append({"vertices":points(meshes[i].vertices),"polygon":Array(meshes[i].get_polygon(0))})
 var result={"version":Engine.get_version_info(),"root_id":root_node.get_instance_id(),"ready":ready_record,"identities":identities,"geometry":geometry,"initial_paths":initial_paths,"initial_identities":initial_identities,"steps":current_step,"events":events,"snapshots":snapshots}
 closed=true
 print("RESULT_JSON="+JSON.stringify(result))
 for a in agents:a.set_navigation_map(RID())
 for r in regions:NavigationServer3D.free_rid(r)
 NavigationServer3D.free_rid(map_rid)
 quit(0)
