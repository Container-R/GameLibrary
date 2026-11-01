"""Author-side raw-value checks against the prospective finite graph contract."""
import json, math, re, uuid
MODES=('shallow','internal','all')
STAGES=('copied','append','internal_edit','external_edit')
RED=[1,0,0,1]; GREEN=[0,1,0,1]; BLUE=[0,0,1,1]; MAGENTA=[1,0,1,1]; WHITE=[1,1,1,1]
def need(condition,message):
    if not condition: raise ValueError(message)
def keys(obj,names):need(type(obj) is dict and set(obj)==set(names.split()),'schema keys '+names)
def integer(x):need(type(x) is int,'exact integer');return x
def ident(x):
    need(type(x) is str and re.fullmatch(r'-?[1-9][0-9]*',x) is not None,'opaque nonzero decimal ID');return x
def pairs(items):
    out={}
    for k,v in items:
        need(k not in out,'duplicate JSON key');out[k]=v
    return out
def load(raw):
    return json.loads(raw,object_pairs_hook=pairs,parse_constant=lambda s: (_ for _ in ()).throw(ValueError('nonfinite constant')))
def finite_tree(x):
    if type(x) is float:need(math.isfinite(x),'nonfinite number')
    elif type(x) is dict:
        for value in x.values():finite_tree(value)
    elif type(x) is list:
        for value in x:finite_tree(value)
def numbers(actual,expected):
    need(type(actual) is list and len(actual)==len(expected),'numeric array')
    for a,b in zip(actual,expected):need(type(a) in (int,float) and math.isfinite(a) and a==b,'numeric value/type')
def grad(g,id_,first):
    keys(g,'id class count colors offsets');need(ident(g['id'])==id_ and g['class']=='Gradient','Gradient identity/class')
    need(integer(g['count'])==2,'point count');numbers(g['offsets'],[0,1])
    need(type(g['colors']) is list and len(g['colors'])==2,'colors');numbers(g['colors'][0],first);numbers(g['colors'][1],WHITE)
def graph(g,root,script,b,c,length,bc,cc):
    keys(g,'root_id script_id length first3_ids slot3 values')
    need(ident(g['root_id'])==root and ident(g['script_id'])==script,'graph root/script')
    need(integer(g['length'])==length,'array length')
    need(type(g['first3_ids']) is list and len(g['first3_ids'])==3,'three identities')
    need([ident(x) for x in g['first3_ids']]==[b,b,c],'alias graph')
    if length==4:need(integer(g['slot3'])==137,'sentinel')
    else:need(g['slot3'] is None,'absent sentinel')
    need(type(g['values']) is list and len(g['values'])==3,'graph values')
    for value,id_,color in zip(g['values'],[b,b,c],[bc,bc,cc]):grad(value,id_,color)
def check(result):
    keys(result,'schema invocation_uuid mode process_id engine_version constants setup stages');finite_tree(result)
    need(integer(result['schema'])==1,'schema');mode=result['mode'];need(mode in MODES,'mode')
    need(type(result['invocation_uuid']) is str and str(uuid.UUID(result['invocation_uuid']))==result['invocation_uuid'],'UUID')
    need(integer(result['process_id'])>0,'PID')
    ev=result['engine_version'];need(type(ev) is dict,'Engine version dictionary')
    for key,value in {'major':4,'minor':6,'patch':3}.items():need(integer(ev.get(key))==value,'version '+key)
    for key,value in {'status':'stable','build':'official','hash':'7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3'}.items():need(ev.get(key)==value,'version '+key)
    # Other engine-returned version fields are preserved, not invented/frozen formats.
    constants={'type_array':28,'storage':2,'always':1<<19,'never':1<<20,'none':0,'internal':1,'all':2}
    need(type(result['constants']) is dict and set(result['constants'])==set(constants),'constants schema')
    for k,v in constants.items():need(integer(result['constants'][k])==v,'constant '+k)
    s=result['setup'];keys(s,'property typed_array a b c script_path a_graph a2_graph held_b held_c cached_c cached_root_id')
    p=s['property'];keys(p,'name type usage');need(p['name']=='entries' and integer(p['type'])==28,'property Array')
    usage=integer(p['usage']);need(usage>=0 and usage&2 and not usage&((1<<19)|(1<<20)),'storage/duplicate flags')
    need(s['typed_array'] is False and s['script_path']=='res://config.gd','untyped/script')
    for name,cls,path,builtin in [('a','Resource','res://config.tres',False),('b','Gradient',None,True),('c','Gradient','res://external.tres',False)]:
        m=s[name];keys(m,'id class path built_in local_to_scene');ident(m['id'])
        need(m['class']==cls and m['built_in'] is builtin and m['local_to_scene'] is False,'resource metadata')
        need(type(m['path']) is str and (m['path'].startswith('res://config.tres::') and len(m['path'])>len('res://config.tres::') if path is None else m['path']==path),'resource path')
    a,b,c=[s[k]['id'] for k in ('a','b','c')];script=ident(s['a_graph']['script_id'])
    need(len({a,b,c,script})==4,'distinct baseline resources/script')
    need(ident(s['cached_root_id'])==a,'cached root')
    for name in ('a_graph','a2_graph'):graph(s[name],a,script,b,c,3,RED,GREEN)
    grad(s['held_b'],b,RED);grad(s['held_c'],c,GREEN);grad(s['cached_c'],c,GREEN)
    stages=result['stages'];need(type(stages) is list and len(stages)==4,'four stages')
    d=ident(stages[0]['d']['root_id']);db=ident(stages[0]['d']['first3_ids'][0]);dc=ident(stages[0]['d']['first3_ids'][2])
    need(d not in {a,b,c,script},'new root')
    need((db==b)==(mode=='shallow') and (dc==c)==(mode!='all'),'copy scope')
    need(db!=dc and db not in {a,d,script} and dc not in {a,d,script},'payload distinctness')
    if db!=b:need(db!=c,'internal copy not external original')
    if dc!=c:need(dc!=b,'external copy not internal original')
    for index,(label,stage) in enumerate(zip(STAGES,stages)):
        keys(stage,'stage a a2 d cached_root_id held_b held_c cached_c same_array')
        need(stage['stage']==label and stage['same_array'] is (mode=='shallow'),'stage/array identity')
        need(ident(stage['cached_root_id'])==a,'cached root stable')
        original_length=4 if index>=1 and mode=='shallow' else 3
        original_b=BLUE if index>=2 and mode=='shallow' else RED
        original_c=MAGENTA if index>=3 and mode!='all' else GREEN
        for name in ('a','a2'):graph(stage[name],a,script,b,c,original_length,original_b,original_c)
        graph(stage['d'],d,script,db,dc,4 if index>=1 else 3,BLUE if index>=2 else RED,MAGENTA if index>=3 else GREEN)
        grad(stage['held_b'],b,original_b);grad(stage['held_c'],c,original_c);grad(stage['cached_c'],c,original_c)
    return {'mode':mode,'stages':4,'mutable_payload_scope_verified':True}
