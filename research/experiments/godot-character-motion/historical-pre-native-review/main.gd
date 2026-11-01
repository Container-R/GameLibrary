extends SceneTree
class Driver extends Node3D:
 var coordinator
 func _physics_process(delta: float) -> void: coordinator.tick(delta)
var scene: Node3D
var wall: StaticBody3D
var wall_node: CollisionShape3D
var actors: Array[CharacterBody3D] = []
var nodes: Array[CollisionShape3D] = []
var query_shape: SphereShape3D
var initial: Dictionary = {}
var trace: Array = []
var callbacks=0
var closed=false
var phase="setup"
const EPS=0.00001
const AXES=[PhysicsServer3D.BODY_AXIS_LINEAR_X,PhysicsServer3D.BODY_AXIS_LINEAR_Y,PhysicsServer3D.BODY_AXIS_LINEAR_Z,PhysicsServer3D.BODY_AXIS_ANGULAR_X,PhysicsServer3D.BODY_AXIS_ANGULAR_Y,PhysicsServer3D.BODY_AXIS_ANGULAR_Z]
func xyz(v: Vector3) -> Array:return [v.x,v.y,v.z]
func xf(t: Transform3D) -> Dictionary:return {"origin":xyz(t.origin),"basis":[xyz(t.basis.x),xyz(t.basis.y),xyz(t.basis.z)]}
func finite_vec(v: Vector3) -> bool:return is_finite(v.x) and is_finite(v.y) and is_finite(v.z)
func fail(message: String) -> void:
 if closed:return
 closed=true
 print("FAIL_JSON="+JSON.stringify({"error":message,"phase":phase,"callbacks":callbacks,"initial":initial,"trace":trace}))
 quit(1)
func _initialize() -> void:
 var driver=Driver.new();driver.coordinator=self;scene=driver;scene.name="Fixture";root.add_child(scene)
 wall=StaticBody3D.new();wall.name="Wall";wall.collision_layer=2;wall.collision_mask=1;wall.constant_linear_velocity=Vector3.ZERO;wall.constant_angular_velocity=Vector3.ZERO
 scene.add_child(wall);wall.position=Vector3(2,0,0)
 wall_node=CollisionShape3D.new();wall_node.name="WallShape";var box=BoxShape3D.new();box.size=Vector3(1,4,2);wall_node.shape=box;wall.add_child(wall_node)
 for i in range(2):
  var a=CharacterBody3D.new();a.name=["Blocked","Open"][i];a.collision_layer=1;a.collision_mask=2;a.velocity=Vector3.ZERO;a.safe_margin=0.001
  for axis in AXES:a.set_axis_lock(axis,false)
  scene.add_child(a);a.position=Vector3(0,0,4*i);actors.append(a)
  var n=CollisionShape3D.new();n.name="ActorShape";var sphere=SphereShape3D.new();sphere.radius=0.5;n.shape=sphere;a.add_child(n);nodes.append(n)
 for axis in AXES:wall.set_axis_lock(axis,false)
 query_shape=SphereShape3D.new();query_shape.radius=0.5
func body_record(body: PhysicsBody3D,n: CollisionShape3D) -> Dictionary:
 var owner=body.shape_find_owner(0);var owners=body.get_shape_owners();var locks=[];var exceptions=[]
 for axis in AXES:locks.append(body.get_axis_lock(axis))
 for obj in body.get_collision_exceptions():exceptions.append(obj.get_instance_id())
 var r={"id":body.get_instance_id(),"rid":body.get_rid().get_id(),"class":body.get_class(),"parent_id":body.get_parent().get_instance_id(),"transform":xf(body.global_transform),"layer":body.collision_layer,"mask":body.collision_mask,"locks":locks,"exceptions":exceptions,"mode":PhysicsServer3D.body_get_mode(body.get_rid()),"shape_node_id":n.get_instance_id(),"shape_parent_id":n.get_parent().get_instance_id(),"shape_transform":xf(n.transform),"disabled":n.disabled,"shape_resource_id":n.shape.get_instance_id(),"shape_rid":n.shape.get_rid().get_id(),"owners":Array(owners),"owner":owner,"owner_object_id":body.shape_owner_get_owner(owner).get_instance_id(),"shape_count":body.shape_owner_get_shape_count(owner),"owner_shape_resource_id":body.shape_owner_get_shape(owner,0).get_instance_id(),"shape_index":body.shape_owner_get_shape_index(owner,0),"owner_disabled":body.is_shape_owner_disabled(owner)}
 if body==wall:r["size"]=xyz(wall_node.shape.size);r["linear_velocity"]=xyz(wall.constant_linear_velocity);r["angular_velocity"]=xyz(wall.constant_angular_velocity)
 else:r["radius"]=n.shape.radius;r["velocity"]=xyz(body.velocity);r["character_safe_margin"]=body.safe_margin
 return r
func config() -> Dictionary:
 return {"root_id":scene.get_instance_id(),"root_transform":xf(scene.global_transform),"backend_setting":ProjectSettings.get_setting("physics/3d/physics_engine"),"server_class":PhysicsServer3D.get_class(),"wall":body_record(wall,wall_node),"actors":[body_record(actors[0],nodes[0]),body_record(actors[1],nodes[1])],"query_resource_id":query_shape.get_instance_id(),"query_rid":query_shape.get_rid().get_id(),"query_radius":query_shape.radius,"static_mode":PhysicsServer3D.BODY_MODE_STATIC,"kinematic_mode":PhysicsServer3D.BODY_MODE_KINEMATIC}
func config_gate(c: Dictionary) -> bool:
 if c["backend_setting"]!="GodotPhysics3D" or not scene.global_transform.is_equal_approx(Transform3D.IDENTITY):return false
 var all_bodies=[wall,actors[0],actors[1]];var all_nodes=[wall_node,nodes[0],nodes[1]];var records=[c["wall"],c["actors"][0],c["actors"][1]]
 for i in range(3):
  var b=all_bodies[i];var n=all_nodes[i];var r=records[i];var expected=Vector3(2,0,0) if i==0 else Vector3(0,0,4*(i-1))
  if b.global_position.distance_to(expected)>EPS or not b.global_basis.is_equal_approx(Basis.IDENTITY) or not n.transform.is_equal_approx(Transform3D.IDENTITY):return false
  if r["mode"]!=(PhysicsServer3D.BODY_MODE_STATIC if i==0 else PhysicsServer3D.BODY_MODE_KINEMATIC) or r["layer"]!=(2 if i==0 else 1) or r["mask"]!=(1 if i==0 else 2):return false
  if r["locks"].has(true) or not r["exceptions"].is_empty() or r["disabled"] or r["owner_disabled"]:return false
  if r["shape_count"]!=1 or r["owners"].size()!=1 or r["owner_object_id"]!=n.get_instance_id() or r["owner_shape_resource_id"]!=n.shape.get_instance_id() or r["shape_index"]!=0 or n.get_parent()!=b or b.get_parent()!=scene:return false
 if wall_node.shape.size.distance_to(Vector3(1,4,2))>EPS or not wall.constant_linear_velocity.is_zero_approx() or not wall.constant_angular_velocity.is_zero_approx():return false
 for i in range(2):
  if abs(nodes[i].shape.radius-0.5)>EPS or not actors[i].velocity.is_zero_approx() or abs(actors[i].safe_margin-0.001)>EPS:return false
 return abs(query_shape.radius-0.5)<=EPS
func query(label: String,origin: Vector3,delta: float) -> Array:
 var q=PhysicsShapeQueryParameters3D.new();q.shape=query_shape;q.transform=Transform3D(Basis.IDENTITY,origin);q.margin=0;q.motion=Vector3.ZERO;q.collision_mask=2;q.collide_with_bodies=true;q.collide_with_areas=false;q.exclude=[actors[0].get_rid(),actors[1].get_rid()]
 var hits=scene.get_world_3d().direct_space_state.intersect_shape(q,4);var out=[];var excludes=[]
 for rid in q.exclude:excludes.append(rid.get_id())
 for h in hits:out.append({"object_id":h["collider"].get_instance_id(),"collider_id":h["collider_id"],"rid":h["rid"].get_id(),"shape_index":h["shape"]})
 trace.append({"kind":"query","label":label,"callback":callbacks,"frame":Engine.get_physics_frames(),"delta":delta,"parameters":{"shape_resource_id":q.shape.get_instance_id(),"shape_rid":q.shape.get_rid().get_id(),"transform":xf(q.transform),"margin":q.margin,"motion":xyz(q.motion),"mask":q.collision_mask,"bodies":q.collide_with_bodies,"areas":q.collide_with_areas,"exclude":excludes,"max_results":4},"hits":out,"actors":[xf(actors[0].global_transform),xf(actors[1].global_transform)]})
 return out
func move_one(i: int,delta: float) -> bool:
 phase="move";var a=actors[i];var before=a.global_transform
 var args={"motion":[4,0,0],"test_only":false,"safe_margin":0.001,"recovery_as_collision":false,"max_collisions":1}
 trace.append({"kind":"move_enter","actor":i,"callback":callbacks,"frame":Engine.get_physics_frames(),"delta":delta,"id":a.get_instance_id(),"arguments":args,"transform":xf(before)})
 var hit=a.move_and_collide(Vector3(4,0,0),false,0.001,false,1)
 var after=a.global_transform;var displacement=after.origin-before.origin;var collision=null
 if hit!=null:
  collision={"count":hit.get_collision_count(),"travel":xyz(hit.get_travel()),"remainder":xyz(hit.get_remainder()),"depth":hit.get_depth()}
  if hit.get_collision_count()==1:
   collision.merge({"object_id":hit.get_collider(0).get_instance_id(),"collider_id":hit.get_collider_id(0),"rid":hit.get_collider_rid(0).get_id(),"collider_shape_node_id":hit.get_collider_shape(0).get_instance_id(),"local_shape_node_id":hit.get_local_shape(0).get_instance_id(),"shape_index":hit.get_collider_shape_index(0),"normal":xyz(hit.get_normal(0)),"position":xyz(hit.get_position(0)),"velocity":xyz(hit.get_collider_velocity(0))})
 trace.append({"kind":"move_return","actor":i,"callback":callbacks,"frame":Engine.get_physics_frames(),"delta":delta,"id":a.get_instance_id(),"transform":xf(after),"displacement":xyz(displacement),"collision":collision})
 if not finite_vec(displacement) or not after.basis.is_equal_approx(Basis.IDENTITY):return false
 if i==1:return hit==null and after.origin.distance_to(Vector3(4,0,4))<=EPS and displacement.distance_to(Vector3(4,0,0))<=EPS
 if hit==null or hit.get_collision_count()!=1:return false
 if hit.get_collider(0)!=wall or hit.get_collider_id(0)!=wall.get_instance_id() or hit.get_collider_rid(0)!=wall.get_rid() or hit.get_collider_shape_index(0)!=0 or hit.get_collider_shape(0)!=wall_node or hit.get_local_shape(0)!=nodes[0]:return false
 var travel=hit.get_travel();var remainder=hit.get_remainder();var normal=hit.get_normal(0);var point=hit.get_position(0)
 if not finite_vec(travel) or not finite_vec(remainder) or not finite_vec(normal) or not finite_vec(point) or not is_finite(hit.get_depth()):return false
 if after.origin.x<0.95 or after.origin.x>1.05 or abs(after.origin.y)>EPS or abs(after.origin.z)>EPS or travel.distance_to(displacement)>EPS or (travel+remainder).distance_to(Vector3(4,0,0))>0.0001 or remainder.x<=0:return false
 return normal.x<=-0.99 and abs(normal.y)<=0.01 and abs(normal.z)<=0.01 and abs(normal.length()-1)<=0.01 and point.x>=1.45 and point.x<=1.55 and abs(point.y)<=0.1 and abs(point.z)<=0.1 and hit.get_collider_velocity(0).length()<=EPS
func tick(delta: float) -> void:
 if closed:return
 callbacks+=1
 if callbacks>120:fail("readiness timeout");return
 if not is_finite(delta) or delta<=0:fail("delta");return
 phase="configuration"
 var c=config()
 if not config_gate(c):fail("setup config");return
 if initial.is_empty():initial=c
 phase="visibility"
 var positive=query("positive",Vector3(2,0,0),delta)
 if positive.is_empty():return
 if positive.size()!=1 or positive[0]["object_id"]!=wall.get_instance_id() or positive[0]["collider_id"]!=wall.get_instance_id() or positive[0]["rid"]!=wall.get_rid().get_id() or positive[0]["shape_index"]!=0:fail("positive identity");return
 var labels=["blocked_start","blocked_endpoint","open_start","open_endpoint"];var positions=[Vector3(0,0,0),Vector3(4,0,0),Vector3(0,0,4),Vector3(4,0,4)]
 for j in range(4):
  if not query(labels[j],positions[j],delta).is_empty():fail("occupancy control");return
 if not move_one(0,delta):fail("blocked motion");return
 if not move_one(1,delta):fail("open motion");return
 var final=config();closed=true
 print("RESULT_JSON="+JSON.stringify({"version":Engine.get_version_info(),"initial":initial,"final":final,"readiness_attempts":callbacks,"trace":trace}))
 quit(0)
