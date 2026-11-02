"""Independent synthetic content probes. No native, subprocess or signals."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
EXPECTED = {'checker.py': '65f49c4ea6a606399d8b1e9aa4a653e6a23c129457c83ac87fdf6269dfd3ffb4',
            'independent-oracle.json': '3bb0f324154852cf070c0e92778f8481bc7c2aed6a4d27a25858c6c970558d03',
            'INPUT-MANIFEST.json': 'bb6af91bca415c50ae4921e5744f33f389d01369d330537dd047bf1e8a2e1ede'}

def require(ok, msg):
    if not ok:
        raise RuntimeError(msg)

def h(n):
    return dict(full=n, index=n & 1048575, version=n >> 20)

def sample(r=0, swap=False):
    # Invented relational assignments, not observations or allocation predictions.
    H,S,B,L = h(7),h(0),h(2),h(3)
    R=h(r)
    rows=[dict(kind='declaration',schema=1,cplusplus=201703,gcc=None,clang=None,
               entt=[3,13,2],entity_mask=1048575,version_mask=4095)]
    entities=[H,R] if swap else [R,H]
    for stream,values,types in [('entities',[2,2,*entities],['uint32','uint32','entity','entity']),
                                ('links',[1,H,{'target':R}],['uint32','entity','Link'])]:
        for i,(value,typ) in enumerate(zip(values,types)):
            rows.append(dict(kind='token',stream=stream,index=i,type=typ,value=value))
    for i,name in enumerate(['prepared','entities_loaded','component_loaded']):
        rows.append(dict(kind='stage',stage=name,remote_box=R,remote_holder=H,local_seed=S,
            mapped_box=h(4294967295) if i==0 else B,mapped_holder=h(4294967295) if i==0 else L,
            source_target=R,archive_target=R,input_target=R if i==2 else None,
            loaded_target=R if i==2 else None,source_box_valid=True,source_holder_valid=True,
            seed_valid=True,box_contains=i>0,holder_contains=i>0,mapped_box_valid=i>0,
            mapped_holder_valid=i>0,holder_has_link=i==2,target_active_count=1 if i==0 else 3,
            target_link_count=int(i==2),entity_written=4,link_written=3,
            entity_read=0 if i==0 else 4,link_read=3 if i==2 else 0,
            loaded_target_in_local_valid=(r in {0,2,3}) if i==2 else None,
            loaded_target_equals_seed=(r==0) if i==2 else None))
    return copy.deepcopy(rows)

def encode(rows):
    return ('\n'.join(json.dumps(x,separators=(',',':')) for x in rows)+'\n').encode()

def main():
    for name, digest in EXPECTED.items():
        require(hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,'frozen_input_changed:'+name)
    spec=importlib.util.spec_from_file_location('frozen_checker',ROOT/'checker.py')
    checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
    def accept(raw):
        return checker.check(raw, ROOT/'independent-oracle.json')
    positives=[sample(0),sample(3),sample(9),sample(9,True)]
    for rows in positives: accept(encode(rows))
    cases=[]
    def mutate(label,row,key,value):
        x=sample();x[row][key]=value;cases.append((label,encode(x)))
    # Exact type checks, especially Python bool == integer coercion.
    for key, value in [('schema',True),('cplusplus',True),('cplusplus',201703.0),('cplusplus','201703'),
                       ('gcc',[1,True,0]),('clang',{}),('entt',[3,13,True]),('entity_mask','1048575')]:
        mutate('declaration_'+key+'_'+repr(value),0,key,value)
    for field in ['full','index','version']:
        for value in [True,1.0,'1',-1,4294967296]:
            x=sample();x[10]['loaded_target'][field]=value
            cases.append(('handle_'+field+'_'+repr(value),encode(x)))
    for key,value in [('seed_valid',False),('source_box_valid',False),('source_holder_valid',False),
                      ('seed_valid',1),('target_active_count',True),('target_link_count',True),
                      ('entity_read',3),('link_read',2),('entity_written',3),('link_written',4),
                      ('mapped_holder_valid',False),('holder_has_link',False),
                      ('loaded_target_in_local_valid',False),('loaded_target_equals_seed',False),
                      ('loaded_target_in_local_valid',1),('loaded_target_equals_seed',1),
                      ('input_target',None),('loaded_target',None),('loaded_target',h(2)),
                      ('input_target',h(2)),('mapped_holder',h(4)),('mapped_box',h(4)),
                      ('remote_box',h(9)),('remote_holder',h(8)),('local_seed',h(8)),
                      ('source_target',h(7)),('archive_target',h(7))]:
        mutate('final_'+key+'_'+repr(value),10,key,value)
    for row in [8,9]:
        for key in ['input_target','loaded_target']:
            mutate('premature_'+str(row)+key,row,key,h(4294967295))
        for key in ['loaded_target_in_local_valid','loaded_target_equals_seed']:
            mutate('premature_'+str(row)+key,row,key,False)
    mutate('wrong_component_owner',6,'value',h(0))
    mutate('converted_archive_target',7,'value',{'target':h(2)})
    mutate('bool_token_count',5,'value',True)
    mutate('duplicate_entity_token',4,'value',h(0))
    mutate('bool_token_index',2,'index',True)
    mutate('null_initial_map',8,'mapped_box',None)
    mutate('prepared_valid_map',8,'mapped_box',h(2))
    mutate('same_local_entities',9,'mapped_holder',h(2))
    # Descriptive valid must vary with full-handle membership, not be fixed true.
    x=sample(9);x[10]['loaded_target_in_local_valid']=True;cases.append(('outside_set_reported_valid',encode(x)))
    x=sample(3);x[10]['loaded_target_equals_seed']=True;cases.append(('holder_not_seed',encode(x)))
    raw=encode(sample())
    cases += [('partial',encode(sample()[:-1])),('extra_line',raw+b'{}\n'),('no_final_lf',raw[:-1]),
              ('crlf',raw.replace(b'\n',b'\r\n')),('blank_line',raw+b'\n'),
              ('duplicate_key',raw.replace(b'"schema":1',b'"schema":1,"schema":1')),
              ('nan',raw.replace(b'"cplusplus":201703',b'"cplusplus":NaN')),
              ('utf8',b'\xff'+raw),('not_bytes',raw.decode()),('oversized',b' '*65537)]
    x=sample();del x[10]['holder_has_link'];cases.append(('missing_field',encode(x)))
    x=sample();x[10]['extra']=0;cases.append(('extra_field',encode(x)))
    x=sample();x[8],x[9]=x[9],x[8];cases.append(('stage_order',encode(x)))
    # Reserved null index and tombstone version cannot describe ordinary live entities.
    # Replace every occurrence of one identity, then recompute descriptive relations.
    def replace_handle(value, old, new):
        if type(value) is dict:
            if value == old and list(value) == ['full','index','version']:
                return copy.deepcopy(new)
            return {k:replace_handle(v,old,new) for k,v in value.items()}
        if type(value) is list:
            return [replace_handle(v,old,new) for v in value]
        return value
    for symbol, old in [('R',9),('H',7),('S',0),('B',2),('L',3)]:
        for label, new in [('null_index',1048575),('tombstone_version',4293918720)]:
            x=replace_handle(sample(9),h(old),h(new))
            z=x[10];r=z['loaded_target']['full'];seed=z['local_seed']['full']
            z['loaded_target_equals_seed']=r==seed
            z['loaded_target_in_local_valid']=r in {seed,z['mapped_box']['full'],z['mapped_holder']['full']}
            cases.append(('reserved_'+symbol+'_'+label,encode(x)))
    failures=[]
    for name,raw in cases:
        try: accept(raw)
        except (ValueError,UnicodeError,TypeError,KeyError): pass
        else: failures.append(name)
    print(json.dumps({'synthetic_positive_cases':len(positives),'synthetic_negative_cases':len(cases),
                      'false_accepts':failures,'native_invocations':0,'scope':'content consumer only'}))
    require(not failures,'false_accept:'+','.join(failures))

if __name__=='__main__': main()
