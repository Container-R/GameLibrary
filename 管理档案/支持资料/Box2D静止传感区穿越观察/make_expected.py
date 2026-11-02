"""Pre-execution literal schema assembly, never reads native output.
This author-side specification is not independent reviewer authorship.
"""
import json
from pathlib import Path
rows=[]
def add(key,value=None,rule='exact',**extra):
    rows.append(dict(case=case,phase=phase,key=key,rule=rule,value=value,**extra))
def ref(key,name): add(key,name,'ref')
def ident(key,kind): add(key,None,'bind',kind=kind)
def motion(x,initial,events):
    add('sensor.pose',[0.,0.,1.,0.],'motion')
    add('visitor.pose',[float(x),0.,1.,0.],'motion')
    add('visitor.velocity',[256.,0.],'motion');add('visitor.angular_velocity',0.,'motion')
    add('visitor.min_extent',.25);add('visitor.safety_factor',.5)
    add('visitor.bullet',False);add('sensor.sensor_events',True);add('visitor.sensor_events',events)
    add('projection',[-.125,.125,x-.25,x+.25],'projection')
    add('gap',1.625 if initial else x-.375,'gap')
def shape(prefix,kind,events):
    add(prefix+'.valid',True);add(prefix+'.type',3 if kind=='sensor' else 0)
    ref(prefix+'.body',prefix+'_body.id');ref(prefix+'.world','world.id')
    add(prefix+'.sensor',kind=='sensor');add(prefix+'.sensor_events',events)
    for key in ['contact_events','hit_events','presolve_events']:add(prefix+'.'+key,False)
    add(prefix+'.density',1.);add(prefix+'.filter',[1,1,0])
case='global';phase='version';add('version',[3,2,0]);add('length_scale',1.)
for case,events in [('events_on',True),('visitor_events_off',False)]:
    phase='requested'
    for key in ['default_definitions','update_body_mass','task_callbacks_null','custom_callbacks_absent']:add(key,True)
    add('custom_filtering',False);add('dt',.015625);add('substeps',1)
    phase='setup';ident('world.id','world');add('world.valid',True);add('length_scale',1.)
    add('world.gravity',[0.,0.]);add('world.continuous',True);add('world.sleep',False);add('world.max_speed',512.);add('world.workers',1)
    for prefix in ['sensor_body','visitor_body']:
        ident(prefix+'.id','body');add(prefix+'.valid',True)
    for prefix in ['sensor','visitor']:
        ident(prefix+'.id','shape');add(prefix+'.created_valid',True)
    add('sensor_body.type',0);add('visitor_body.type',2)
    for prefix in ['sensor_body','visitor_body']:
        add(prefix+'.shape_count',1);add(prefix+'.shapes_returned',1);ref(prefix+'.shape',prefix.replace('_body','')+'.id')
    for key in ['linear_damping','angular_damping']:add('visitor.'+key,0.)
    add('visitor.gravity_scale',1.)
    for key,value in [('sleep',False),('awake',True),('enabled',True),('bullet',False),('lock_x',False),('lock_y',False),('lock_rotation',False)]:add('visitor.'+key,value)
    add('visitor.min_extent',.25);add('visitor.safety_factor',.5);add('visitor.mass',None,'positive')
    add('visitor.local_center',[0.,0.]);add('visitor.world_center',[-2.,0.])
    shape('sensor','sensor',True);shape('visitor','visitor',events)
    add('polygon.count',4)
    for i,(xy,normal) in enumerate(zip([[-.125,-1.],[.125,-1.],[.125,1.],[-.125,1.]],[[0.,-1.],[1.,0.],[0.,1.],[-1.,0.]])):
        add(f'polygon.vertex.{i}',xy);add(f'polygon.normal.{i}',normal)
    add('polygon.centroid',[0.,0.]);add('polygon.radius',0.);add('circle.center',[0.,0.]);add('circle.radius',.25)
    phase='initial';motion(-2.,True,events)
    for step in [1,2,3]:
        phase=f'step_{step}';add('step_begin',step);add('step_returned',step);motion(-2.+4*step,False,events);add('dx',4.,'dx')
        add('begin_count',1 if events and step==1 else 0);add('end_count',1 if events and step==2 else 0)
        if events and step in [1,2]:
            kind='begin' if step==1 else 'end';ref(kind+'.sensor','sensor.id');ref(kind+'.visitor','visitor.id')
            add('pair.sensor_valid',True);add('pair.visitor_valid',True)
        count=1 if events and step==1 else 0;add('cache_capacity',count);add('cache_count',count)
        if count:ref('cache_visitor','visitor.id');add('cache_valid',True)
        add('step_complete',step)
    phase='destroy';add('world_destroyed',True)
case='global';phase='complete';add('worlds',2);add('steps',6)
Path(__file__).with_name('expected.json').write_text(json.dumps({'schema':1,'scope':'literal pre-execution two-world six-step specification','rows':rows},ensure_ascii=False,indent=2)+'\n')
