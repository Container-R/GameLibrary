/* Original finite observation fixture; upstream Box2D remains unchanged.
 * No build/run is authorized by merely possessing this source. */
#include <box2d/box2d.h>
#include <box2d/math_functions.h>
#include <math.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>

static const char *case_name = "global", *phase = "version";
static void fail(const char *why)
{
    printf("{\"case\":\"%s\",\"phase\":\"%s\",\"key\":\"failure\",\"value\":\"%s\"}\n", case_name, phase, why);
    fflush(stdout);
    _Exit(1); /* No uncertain-object cleanup on failure; not an OOM safety claim. */
}
static void require(int yes, const char *why) { if (!yes) fail(why); }
static void start(const char *key) { printf("{\"case\":\"%s\",\"phase\":\"%s\",\"key\":\"%s\",\"value\":", case_name, phase, key); }
static void done(void) { puts("}"); if (fflush(stdout) != 0) _Exit(2); }
static void number(double x) { if (!isfinite(x)) { fputs("null", stdout); } else printf("%.9e", x); }
static void scalar(const char *key, double x, double want, double tolerance)
{
    start(key); number(x); done(); require(isfinite(x) && fabs(x-want) <= tolerance, key);
}
static void integer(const char *key, int x, int want) { start(key); printf("%d", x); done(); require(x == want, key); }
static void boolean(const char *key, bool x, bool want) { start(key); fputs(x ? "true" : "false", stdout); done(); require(x == want, key); }
static void vector(const char *key, double x, double y, double a, double b, double tol)
{
    start(key); putchar('['); number(x); putchar(','); number(y); putchar(']'); done();
    require(isfinite(x) && isfinite(y) && fabs(x-a)<=tol && fabs(y-b)<=tol, key);
}
static bool same_shape(b2ShapeId a, b2ShapeId b) { return a.index1==b.index1 && a.world0==b.world0 && a.generation==b.generation; }
static bool same_body(b2BodyId a, b2BodyId b) { return a.index1==b.index1 && a.world0==b.world0 && a.generation==b.generation; }
static bool same_world(b2WorldId a, b2WorldId b) { return a.index1==b.index1 && a.generation==b.generation; }
static void shape_id(const char *key, b2ShapeId id) { start(key); printf("[%d,%u,%u]", (int)id.index1, (unsigned)id.world0, (unsigned)id.generation); done(); }
static void body_id(const char *key, b2BodyId id) { start(key); printf("[%d,%u,%u]", (int)id.index1, (unsigned)id.world0, (unsigned)id.generation); done(); }
static void world_id(const char *key, b2WorldId id) { start(key); printf("[%u,%u]", (unsigned)id.index1, (unsigned)id.generation); done(); }
static void pose(const char *key, b2BodyId body, double expected_x)
{
    b2Transform t=b2Body_GetTransform(body);
    start(key); putchar('['); number(t.p.x); putchar(','); number(t.p.y); putchar(','); number(t.q.c); putchar(','); number(t.q.s); putchar(']'); done();
    require(isfinite(t.p.x)&&isfinite(t.p.y)&&isfinite(t.q.c)&&isfinite(t.q.s) && fabs(t.p.x-expected_x)<=1e-5 && fabs(t.p.y)<=1e-5 && fabs(t.q.c-1)<=1e-5 && fabs(t.q.s)<=1e-5, key);
}
static void body_shapes(const char *prefix, b2BodyId body, b2ShapeId wanted)
{
    char key[96]; b2ShapeId ids[1]={b2_nullShapeId};
    snprintf(key,sizeof key,"%s.shape_count",prefix); integer(key,b2Body_GetShapeCount(body),1);
    int count=b2Body_GetShapes(body,ids,1);
    snprintf(key,sizeof key,"%s.shapes_returned",prefix); integer(key,count,1);
    snprintf(key,sizeof key,"%s.shape",prefix); shape_id(key,ids[0]); require(same_shape(ids[0],wanted),key);
}
static void shape_setup(const char *prefix, b2ShapeId shape, b2BodyId body, b2WorldId world, bool sensor, bool events)
{
    char key[96];
#define K(s) (snprintf(key,sizeof key,"%s.%s",prefix,s),key)
    boolean(K("valid"),b2Shape_IsValid(shape),true);
    integer(K("type"),b2Shape_GetType(shape),sensor ? b2_polygonShape : b2_circleShape);
    b2BodyId owner=b2Shape_GetBody(shape); body_id(K("body"),owner); require(same_body(owner,body),"shape_body");
    b2WorldId w=b2Shape_GetWorld(shape); world_id(K("world"),w); require(same_world(w,world),"shape_world");
    boolean(K("sensor"),b2Shape_IsSensor(shape),sensor);
    boolean(K("sensor_events"),b2Shape_AreSensorEventsEnabled(shape),events);
    boolean(K("contact_events"),b2Shape_AreContactEventsEnabled(shape),false);
    boolean(K("hit_events"),b2Shape_AreHitEventsEnabled(shape),false);
    boolean(K("presolve_events"),b2Shape_ArePreSolveEventsEnabled(shape),false);
    scalar(K("density"),b2Shape_GetDensity(shape),1,0);
    b2Filter f=b2Shape_GetFilter(shape); start(K("filter")); printf("[%llu,%llu,%d]",(unsigned long long)f.categoryBits,(unsigned long long)f.maskBits,(int)f.groupIndex); done();
    require(f.categoryBits==1 && f.maskBits==1 && f.groupIndex==0,"shape_filter");
#undef K
}
static b2Polygon observed_box;
static b2Circle observed_circle;
static void geometry(b2ShapeId sensor,b2ShapeId visitor)
{
    observed_box=b2Shape_GetPolygon(sensor); observed_circle=b2Shape_GetCircle(visitor);
    integer("polygon.count",observed_box.count,4);
    const double xy[4][2]={{-.125,-1},{.125,-1},{.125,1},{-.125,1}};
    const double normals[4][2]={{0,-1},{1,0},{0,1},{-1,0}};
    char key[64];
    for(int i=0;i<4;++i) {
        snprintf(key,sizeof key,"polygon.vertex.%d",i); vector(key,observed_box.vertices[i].x,observed_box.vertices[i].y,xy[i][0],xy[i][1],0);
        snprintf(key,sizeof key,"polygon.normal.%d",i); vector(key,observed_box.normals[i].x,observed_box.normals[i].y,normals[i][0],normals[i][1],0);
    }
    vector("polygon.centroid",observed_box.centroid.x,observed_box.centroid.y,0,0,0);
    scalar("polygon.radius",observed_box.radius,0,0);
    vector("circle.center",observed_circle.center.x,observed_circle.center.y,0,0,0);
    scalar("circle.radius",observed_circle.radius,.25,0);
}
static void separation(b2BodyId sensor,b2BodyId visitor,bool initial)
{
    b2Transform a=b2Body_GetTransform(sensor), b=b2Body_GetTransform(visitor);
    double xmin=INFINITY,xmax=-INFINITY;
    for(int i=0;i<4;++i) {
        double x=a.p.x+a.q.c*observed_box.vertices[i].x-a.q.s*observed_box.vertices[i].y;
        if(x<xmin) xmin=x;
        if(x>xmax) xmax=x;
    }
    double cx=b.p.x+b.q.c*observed_circle.center.x-b.q.s*observed_circle.center.y;
    double lo=cx-observed_circle.radius, hi=cx+observed_circle.radius;
    start("projection"); putchar('['); number(xmin); putchar(',');number(xmax);putchar(',');number(lo);putchar(',');number(hi);putchar(']');done();
    double gap=initial ? xmin-hi : lo-xmax;
    start("gap");number(gap);done();require(isfinite(gap)&&gap>1,"endpoint_separation");
}
static void motion(b2BodyId sensor,b2BodyId visitor,double x,bool initial,bool events,b2ShapeId sensor_shape,b2ShapeId visitor_shape)
{
    pose("sensor.pose",sensor,0);pose("visitor.pose",visitor,x);
    b2Vec2 v=b2Body_GetLinearVelocity(visitor); vector("visitor.velocity",v.x,v.y,256,0,1e-5);
    scalar("visitor.angular_velocity",b2Body_GetAngularVelocity(visitor),0,1e-5);
    scalar("visitor.min_extent",b2Body_GetMinExtent(visitor),.25,0);
    scalar("visitor.safety_factor",b2Body_GetSafetyFactor(visitor),.5,0);
    boolean("visitor.bullet",b2Body_IsBullet(visitor),false);
    boolean("sensor.sensor_events",b2Shape_AreSensorEventsEnabled(sensor_shape),true);
    boolean("visitor.sensor_events",b2Shape_AreSensorEventsEnabled(visitor_shape),events);
    separation(sensor,visitor,initial);
}
static void event_pair(const char *key,b2ShapeId s,b2ShapeId v,b2ShapeId want_s,b2ShapeId want_v)
{
    char k[64];snprintf(k,sizeof k,"%s.sensor",key);shape_id(k,s);snprintf(k,sizeof k,"%s.visitor",key);shape_id(k,v);
    boolean("pair.sensor_valid",b2Shape_IsValid(s),true);boolean("pair.visitor_valid",b2Shape_IsValid(v),true);
    require(same_shape(s,want_s)&&same_shape(v,want_v),"pair_identity");
}
static void run_case(bool events)
{
    case_name=events ? "events_on" : "visitor_events_off";phase="requested";
    /* Request-only fields with no corresponding public getters. */
    boolean("default_definitions",true,true);boolean("update_body_mass",true,true);
    boolean("task_callbacks_null",true,true);boolean("custom_callbacks_absent",true,true);
    boolean("custom_filtering",false,false);scalar("dt",.015625,.015625,0);integer("substeps",1,1);
    b2WorldDef wd=b2DefaultWorldDef();wd.gravity=(b2Vec2){0,0};wd.enableContinuous=true;wd.enableSleep=false;wd.maximumLinearSpeed=512;wd.workerCount=1;
    wd.enqueueTask=NULL;wd.finishTask=NULL;wd.userTaskContext=NULL;
    b2WorldId world=b2CreateWorld(&wd);phase="setup";world_id("world.id",world);boolean("world.valid",b2World_IsValid(world),true);
    scalar("length_scale",b2GetLengthUnitsPerMeter(),1,0);
    b2Vec2 gravity=b2World_GetGravity(world);vector("world.gravity",gravity.x,gravity.y,0,0,0);
    boolean("world.continuous",b2World_IsContinuousEnabled(world),true);boolean("world.sleep",b2World_IsSleepingEnabled(world),false);
    scalar("world.max_speed",b2World_GetMaxLinearSpeed(world),512,0);integer("world.workers",b2World_GetWorkerCount(world),1);
    b2BodyDef sd=b2DefaultBodyDef();sd.type=b2_staticBody;sd.position=(b2Pos){0,0};sd.rotation=(b2Rot){1,0};
    b2BodyId sensor_body=b2CreateBody(world,&sd);body_id("sensor_body.id",sensor_body);boolean("sensor_body.valid",b2Body_IsValid(sensor_body),true);
    b2BodyDef vd=b2DefaultBodyDef();vd.type=b2_dynamicBody;vd.position=(b2Pos){-2,0};vd.rotation=(b2Rot){1,0};vd.linearVelocity=(b2Vec2){256,0};vd.angularVelocity=0;
    vd.linearDamping=0;vd.angularDamping=0;vd.gravityScale=1;vd.enableSleep=false;vd.isAwake=true;vd.isEnabled=true;vd.isBullet=false;vd.safetyFactor=.5;
    vd.motionLocks=(b2MotionLocks){false,false,false};
    b2BodyId visitor_body=b2CreateBody(world,&vd);body_id("visitor_body.id",visitor_body);boolean("visitor_body.valid",b2Body_IsValid(visitor_body),true);
    require(!same_body(sensor_body,visitor_body),"body_distinct");
    b2ShapeDef ss=b2DefaultShapeDef();ss.isSensor=true;ss.enableSensorEvents=true;ss.density=1;ss.updateBodyMass=true;
    ss.filter=(b2Filter){.categoryBits=1,.maskBits=1,.groupIndex=0};ss.enableCustomFiltering=false;ss.enableContactEvents=false;ss.enableHitEvents=false;ss.enablePreSolveEvents=false;
    b2Polygon box=b2MakeBox(.125f,1.0f);box.radius=0;
    b2ShapeId sensor=b2CreatePolygonShape(sensor_body,&ss,&box);shape_id("sensor.id",sensor);boolean("sensor.created_valid",b2Shape_IsValid(sensor),true);
    b2ShapeDef vs=b2DefaultShapeDef();vs.isSensor=false;vs.enableSensorEvents=events;vs.density=1;vs.updateBodyMass=true;
    vs.filter=(b2Filter){.categoryBits=1,.maskBits=1,.groupIndex=0};vs.enableCustomFiltering=false;vs.enableContactEvents=false;vs.enableHitEvents=false;vs.enablePreSolveEvents=false;
    b2Circle circle={.center={0,0},.radius=.25f};
    b2ShapeId visitor=b2CreateCircleShape(visitor_body,&vs,&circle);shape_id("visitor.id",visitor);boolean("visitor.created_valid",b2Shape_IsValid(visitor),true);
    require(!same_shape(sensor,visitor),"shape_distinct");
    integer("sensor_body.type",b2Body_GetType(sensor_body),b2_staticBody);integer("visitor_body.type",b2Body_GetType(visitor_body),b2_dynamicBody);
    body_shapes("sensor_body",sensor_body,sensor);body_shapes("visitor_body",visitor_body,visitor);
    scalar("visitor.linear_damping",b2Body_GetLinearDamping(visitor_body),0,0);scalar("visitor.angular_damping",b2Body_GetAngularDamping(visitor_body),0,0);
    scalar("visitor.gravity_scale",b2Body_GetGravityScale(visitor_body),1,0);
    boolean("visitor.sleep",b2Body_IsSleepingEnabled(visitor_body),false);boolean("visitor.awake",b2Body_IsAwake(visitor_body),true);
    boolean("visitor.enabled",b2Body_IsEnabled(visitor_body),true);boolean("visitor.bullet",b2Body_IsBullet(visitor_body),false);
    b2MotionLocks locks=b2Body_GetMotionLocks(visitor_body);boolean("visitor.lock_x",locks.linearX,false);boolean("visitor.lock_y",locks.linearY,false);boolean("visitor.lock_rotation",locks.angularZ,false);
    scalar("visitor.min_extent",b2Body_GetMinExtent(visitor_body),.25,0);scalar("visitor.safety_factor",b2Body_GetSafetyFactor(visitor_body),.5,0);
    double mass=b2Body_GetMass(visitor_body);start("visitor.mass");number(mass);done();require(isfinite(mass)&&mass>0,"positive_mass");
    b2Vec2 local=b2Body_GetLocalCenter(visitor_body);vector("visitor.local_center",local.x,local.y,0,0,0);
    b2Pos center=b2Body_GetWorldCenter(visitor_body);vector("visitor.world_center",center.x,center.y,-2,0,0);
    shape_setup("sensor",sensor,sensor_body,world,true,true);shape_setup("visitor",visitor,visitor_body,world,false,events);geometry(sensor,visitor);
    phase="initial";motion(sensor_body,visitor_body,-2,true,events,sensor,visitor);
    double previous_x=b2Body_GetTransform(visitor_body).p.x;
    for(int step=1;step<=3;++step) {
        char step_phase[32];snprintf(step_phase,sizeof step_phase,"step_%d",step);phase=step_phase;
        integer("step_begin",step,step);b2World_Step(world,.015625f,1);integer("step_returned",step,step);
        motion(sensor_body,visitor_body,-2+4*step,false,events,sensor,visitor);
        double x=b2Body_GetTransform(visitor_body).p.x,dx=x-previous_x;previous_x=x;
        start("dx");number(dx);done();require(isfinite(dx)&&dx>b2Body_GetMinExtent(visitor_body)*b2Body_GetSafetyFactor(visitor_body),"fast_displacement");
        b2SensorEvents e=b2World_GetSensorEvents(world);
        start("begin_count");printf("%d",e.beginCount);done();
        start("end_count");printf("%d",e.endCount);done();
        require(e.beginCount==(events&&step==1 ? 1:0),"begin_count");
        require(e.endCount==(events&&step==2 ? 1:0),"end_count");
        if(e.beginCount) {require(e.beginEvents!=NULL,"begin_pointer");b2SensorBeginTouchEvent p=e.beginEvents[0];event_pair("begin",p.sensorShapeId,p.visitorShapeId,sensor,visitor);}
        if(e.endCount) {require(e.endEvents!=NULL,"end_pointer");b2SensorEndTouchEvent p=e.endEvents[0];event_pair("end",p.sensorShapeId,p.visitorShapeId,sensor,visitor);}
        int want=events&&step==1 ? 1:0;
        integer("cache_capacity",b2Shape_GetSensorCapacity(sensor),want);
        b2ShapeId overlaps[1]={b2_nullShapeId};int count=b2Shape_GetSensorData(sensor,overlaps,1);integer("cache_count",count,want);
        if(count) {shape_id("cache_visitor",overlaps[0]);boolean("cache_valid",b2Shape_IsValid(overlaps[0]),true);require(same_shape(overlaps[0],visitor),"cache_identity");}
        integer("step_complete",step,step);
    }
    phase="destroy";b2DestroyWorld(world);boolean("world_destroyed",true,true);
}
int main(void)
{
    b2Version v=b2GetVersion();start("version");printf("[%d,%d,%d]",v.major,v.minor,v.revision);done();require(v.major==3&&v.minor==2&&v.revision==0,"version");
    scalar("length_scale",b2GetLengthUnitsPerMeter(),1,0);
    run_case(true);run_case(false);case_name="global";phase="complete";integer("worlds",2,2);integer("steps",6,6);return 0;
}
