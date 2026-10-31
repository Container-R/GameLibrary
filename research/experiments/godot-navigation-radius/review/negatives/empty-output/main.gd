extends Node3D
var nav: NavigationMesh
var source: NavigationMeshSourceGeometryData3D
var nav_map: RID
var region: RID
var initial_iteration: int
var matched = false
var submitted = false
var baked = false
var finished = false
var phase = "setup"
var ticks = 0
var radius: float
var contract: Dictionary
var agents = []
var geometry_before: Dictionary
var trace = []
var start: Vector3
var goal: Vector3

func v(a: Array) -> Vector3:
 return Vector3(a[0],a[1],a[2])
func xyz(p: Vector3) -> Array:
 return [p.x,p.y,p.z]
func points(ps: PackedVector3Array) -> Array:
 var out = []
 for p in ps: out.append(xyz(p))
 return out
func fail(m: String) -> void:
 finished = true
 printerr("FIXTURE_FAILURE="+m)
 get_tree().quit(2)
func mesh_record() -> Dictionary:
 var polys = []
 for i in nav.get_polygon_count(): polys.append(Array(nav.get_polygon(i)))
 return {"vertices":points(nav.get_vertices()),"polygons":polys}
func _ready() -> void:
 contract=JSON.parse_string(FileAccess.get_file_as_string("res://contract.json"))
 var args=OS.get_cmdline_user_args()
 if args.size()!=1 or args[0] not in ["small","large"]:
  fail("fixed case required");return
 radius=0.2 if args[0]=="small" else 1.2
 NavigationServer3D.map_changed.connect(func(changed: RID):
  if changed==nav_map:
   matched=true
   trace.append({"kind":"map_changed","iteration":NavigationServer3D.map_get_iteration_id(nav_map)}))
 for wall in contract["walls"]:
  var body=StaticBody3D.new();body.name=wall["name"];body.collision_layer=2;body.collision_mask=0
  var shape=BoxShape3D.new();shape.size=v(wall["size"])
  var cs=CollisionShape3D.new();cs.shape=shape;body.add_child(cs);body.position=v(wall["center"]);add_child(body)
 call_deferred("setup")
func setup() -> void:
 nav=NavigationMesh.new()
 for key in contract["bake_settings"]: nav.set(key,contract["bake_settings"][key])
 nav.agent_radius=radius
 source=NavigationMeshSourceGeometryData3D.new()
 var faces=PackedVector3Array()
 for rect in contract["rectangles_xz"]:
  var a=Vector3(rect[0],0,rect[2]);var b=Vector3(rect[1],0,rect[2]);var c=Vector3(rect[1],0,rect[3]);var d=Vector3(rect[0],0,rect[3])
  faces.append_array(PackedVector3Array([a,b,c,a,c,d]))
 source.add_faces(faces,Transform3D.IDENTITY)
 print("SOURCE_JSON="+JSON.stringify({"faces":points(faces),"parsed_vertices":Array(source.get_vertices()),"parsed_indices":Array(source.get_indices())}))
 NavigationServer3D.bake_from_source_geometry_data(nav,source,func(): baked=true)
 if not baked or nav.get_polygon_count()==0:
  fail("bake callback or polygon capability gate failed");return
 geometry_before=mesh_record()
 print("BAKE_JSON="+JSON.stringify({"radius":radius,"mesh":geometry_before,"bake_completed":baked}))
 nav_map=NavigationServer3D.map_create();initial_iteration=NavigationServer3D.map_get_iteration_id(nav_map)
 NavigationServer3D.map_set_active(nav_map,true)
 NavigationServer3D.map_set_use_async_iterations(nav_map,false)
 NavigationServer3D.map_set_cell_size(nav_map,0.1);NavigationServer3D.map_set_cell_height(nav_map,0.1)
 NavigationServer3D.map_set_use_edge_connections(nav_map,false)
 region=NavigationServer3D.region_create()
 NavigationServer3D.region_set_use_async_iterations(region,false)
 NavigationServer3D.region_set_enabled(region,true)
 NavigationServer3D.region_set_navigation_layers(region,1)
 NavigationServer3D.region_set_navigation_mesh(region,nav)
 NavigationServer3D.region_set_map(region,nav_map)
 submitted=true;phase="waiting_map"
func overlap(r: float,position_: Vector3) -> Array:
 var s=SphereShape3D.new();s.radius=r
 var q=PhysicsShapeQueryParameters3D.new();q.shape=s;q.transform=Transform3D(Basis.IDENTITY,position_);q.collision_mask=2;q.margin=0
 var hits=get_world_3d().direct_space_state.intersect_shape(q,8)
 var out=[]
 for h in hits: out.append({"name":str(h["collider"].name),"id":h["collider_id"],"shape":h["shape"]})
 return out
func _physics_process(_delta: float) -> void:
 if finished or not submitted:return
 ticks+=1
 if ticks>240:fail("phase watchdog pending="+phase);return
 if phase=="waiting_map":
  var mi=NavigationServer3D.map_get_iteration_id(nav_map)
  if not matched or mi==0 or mi==initial_iteration or NavigationServer3D.region_get_iteration_id(region)==0:return
  if NavigationServer3D.region_get_map(region)!=nav_map or not NavigationServer3D.region_get_enabled(region):return
  var ctrl=overlap(0.2,Vector3(0,1.5,2.5))
  if ctrl.is_empty():return
  start=NavigationServer3D.map_get_closest_point(nav_map,Vector3(-4,0,0))
  goal=NavigationServer3D.map_get_closest_point(nav_map,Vector3(4,0,0))
  for r in [0.2,1.2]:
   var parent=Node3D.new();add_child(parent);parent.global_position=start
   var agent=NavigationAgent3D.new();agent.radius=r;agent.avoidance_enabled=false;agent.path_desired_distance=0.01;agent.target_desired_distance=0.01
   parent.add_child(agent);agent.set_navigation_map(nav_map);agent.target_position=goal;agents.append(agent)
  trace.append({"kind":"ready","tick":ticks,"map_iteration":mi,"region_iteration":NavigationServer3D.region_get_iteration_id(region),"positive_control":ctrl})
  phase="query_agents";return
 if phase=="query_agents":
  var paths=[]
  for agent in agents:
   var next=agent.get_next_path_position()
   paths.append({"radius":agent.radius,"avoidance":agent.avoidance_enabled,"map_id":agent.get_navigation_map().get_id(),"next":xyz(next),"path":points(agent.get_current_navigation_path()),"final":xyz(agent.get_final_position())})
  if paths[0]["path"].is_empty() or paths[1]["path"].is_empty():
   fail("agent query empty after explicit readiness");return
  var settings={}
  for key in contract["bake_settings"]:settings[key]=nav.get(key)
  var walls=[]
  for label in ["WallPositive","WallNegative"]:
   var body=get_node(label);walls.append({"name":label,"position":xyz(body.global_position),"size":xyz(body.get_child(0).shape.size),"layer":body.collision_layer})
  print("RESULT_JSON="+JSON.stringify({"radius":radius,"version":Engine.get_version_info(),"display":DisplayServer.get_name(),"physics_engine":ProjectSettings.get_setting("physics/3d/physics_engine"),"settings":settings,"actual_bake_radius":nav.agent_radius,"mesh_before":geometry_before,"mesh_after":mesh_record(),"map_id":nav_map.get_id(),"region_id":region.get_id(),"region_map_id":NavigationServer3D.region_get_map(region).get_id(),"map_iteration":NavigationServer3D.map_get_iteration_id(nav_map),"region_iteration":NavigationServer3D.region_get_iteration_id(region),"initial_iteration":initial_iteration,"map_async":NavigationServer3D.map_get_use_async_iterations(nav_map),"region_async":NavigationServer3D.region_get_use_async_iterations(region),"region_enabled":NavigationServer3D.region_get_enabled(region),"layers":NavigationServer3D.region_get_navigation_layers(region),"registered_regions":NavigationServer3D.map_get_regions(nav_map).size(),"map_cell_size":NavigationServer3D.map_get_cell_size(nav_map),"map_cell_height":NavigationServer3D.map_get_cell_height(nav_map),"start":xyz(start),"goal":xyz(goal),"agents":paths,"trace":trace,"walls":walls,"overlap_small":overlap(0.2,Vector3(0,1.5,0)),"overlap_large":overlap(1.2,Vector3(0,1.5,0)),"positive_control":overlap(0.2,Vector3(0,1.5,2.5))}))
  finished=true
  for agent in agents:agent.set_navigation_map(RID())
  NavigationServer3D.free_rid(region);NavigationServer3D.free_rid(nav_map)
  get_tree().quit(0)
