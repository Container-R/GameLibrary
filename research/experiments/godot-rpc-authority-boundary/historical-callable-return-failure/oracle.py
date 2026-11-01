"""Finite literal receipt oracle; no engine or network entry points."""
import json
import copy
import math

BINARY = 'f64d4ed19fc9df9440321653fcc80df8c6e365ba7b6de0a29e2cfa9fa71bfeb3'
PROTOCOL = '86323211989a29ef3a8cdb008fe9789100e2235c5929af979d2743c940c80e6e'
HELPER = 'bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970'
VERSION = '4.6.3.stable.official.7d41c59c4'
BANNER = 'Godot Engine v' + VERSION + ' - https://godotengine.org'
ENGINE = dict(build='official', hash='7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3', hex=263683, major=4, minor=6, patch=3, status='stable', string='4.6.3-stable (official)', timestamp=0)
SOURCES = ('protocol.md','isolation.py','project.godot','main.gd','endpoint.gd','oracle.py','consumer.py','run.py','test_pure.py')
BASE_ENV = {'PATH':'/usr/bin:/bin','LANG':'C','LC_ALL':'C'}
ENV_DIRS = {'HOME':'home','XDG_CACHE_HOME':'cache','XDG_CONFIG_HOME':'config','XDG_DATA_HOME':'data','TMPDIR':'tmp'}
NAIVE = [{'A':1,'B':0},{'A':1,'B':1},{'A':10001,'B':1}]
GUARDED = {'A':1,'B':0}
REASONS = ['accepted','ownership','input_bound']
ACTORS = ['A','B','A']
AXES = [1,1,10000]

def require(condition, message):
    if not condition:
        raise ValueError(message)

def pairs(items):
    result = {}
    for key,value in items:
        require(key not in result, 'duplicate JSON key')
        result[key] = value
    return result

def finite(value):
    if isinstance(value,float):
        require(math.isfinite(value), 'nonfinite number')
    elif isinstance(value,list):
        for item in value: finite(item)
    elif isinstance(value,dict):
        for item in value.values(): finite(item)
    return value

def loads(text):
    def bad(value): raise ValueError('nonfinite JSON constant '+value)
    return finite(json.loads(text, object_pairs_hook=pairs, parse_constant=bad))

def equal(actual, expected, label):
    require(type(actual) is type(expected), label+' type')
    if isinstance(expected,dict):
        require(set(actual)==set(expected),label+' keys')
        for key in expected: equal(actual[key],expected[key],label+'.'+key)
    elif isinstance(expected,list):
        require(len(actual)==len(expected),label+' length')
        for n,(a,b) in enumerate(zip(actual,expected)): equal(a,b,label+str(n))
    else: require(actual==expected,label+' value')

def row(role, n, kind, **fields):
    return dict(sequence=n,role=role,kind=kind,**fields)

def ready(role, client):
    return dict(local_port=32187 if role=='server' else 32188, unique_id=1 if role=='server' else client,
                authority=1,path='/root/Fixture/Endpoint',allow_object_decoding=False,auth_callback_valid=False,is_server=role=='server')

def startup(role, client):
    return [row(role,1,'CREATE',return_code=0,requested_bind_ip='127.0.0.1',requested_local_port=32187 if role=='server' else 32188,
                destination='none' if role=='server' else '127.0.0.1:32187'),
            row(role,2,'READY' if role=='server' else 'CLIENT_BOUND',**ready(role,client))]

def expected_server(client):
    rows=startup('server',client)
    def add(kind,**fields): rows.append(row('server',len(rows)+1,kind,**fields))
    add('PEER_CONNECTED',peer_id=client,owners={'A':client,'B':1},actual_peers=[client])
    add('CONTROL_SENT',method='welcome',target=client,return_code=0)
    for i in range(3):
        before_naive = {'A':0,'B':0} if i==0 else NAIVE[i-1]
        before_guarded = {'A':0,'B':0} if i==0 else GUARDED
        add('RPC_ENTER',index=i+1,sender=client,authority=1,actor=ACTORS[i],axis=AXES[i],naive=before_naive,guarded=before_guarded)
        add('ENQUEUED',index=i+1,actor=ACTORS[i],axis=AXES[i],captured_sender=client)
        add('RPC_END',index=i+1,sender=client)
        add('DEFERRED',index=i+1,captured_sender=client,fresh_sender=0,owners={'A':client,'B':1},authority=1)
        add('DECISION',index=i+1,reason=REASONS[i],before_naive=before_naive,before_guarded=before_guarded,naive=NAIVE[i],guarded=GUARDED,captured_sender=client)
        add('CONTROL_SENT',method='outcome',index=i+1,target=client,return_code=0)
    add('SERVER_FINISH_CONFIRMED',sender=client,last_index=3,naive=NAIVE[-1],guarded=GUARDED)
    return rows

def expected_client(client, connection_order=('PEER_CONNECTED','CONNECTED','WELCOME')):
    rows=startup('client',client)
    def add(kind,**fields): rows.append(row('client',len(rows)+1,kind,**fields))
    fields={'PEER_CONNECTED':dict(peer_id=1), 'CONNECTED':dict(unique_id=client,actual_peers=[1]), 'WELCOME':dict(sender=1,assigned=client,authority=1)}
    require(len(connection_order)==3 and set(connection_order)==set(fields),'connection events')
    for kind in connection_order: add(kind,**fields[kind])
    for i in range(3):
        add('SUBMIT_SENT',index=i+1,actor=ACTORS[i],axis=AXES[i],target=1,return_code=0)
        add('OUTCOME',index=i+1,sender=1,reason=REASONS[i],naive=NAIVE[i],guarded=GUARDED)
    add('CLIENT_RECEIVED_ALL',outcomes=3)
    add('CONTROL_SENT',method='finish',target=1,return_code=0)
    return rows

def payload(role,client,trace):
    return copy.deepcopy(dict(role=role,version=ENGINE,unique_id=1 if role=='server' else client,client_id=client,authority=1,path='/root/Fixture/Endpoint',trace=trace))

def check_payloads(server,client):
    cid=server.get('client_id')
    require(type(cid) is int and 1<cid<2147483648,'client peer ID')
    equal(server,payload('server',cid,expected_server(cid)),'server')
    trace=client.get('trace')
    require(type(trace) is list and len(trace)==13,'client trace count')
    order=[item.get('kind') for item in trace[2:5]]
    equal(client,payload('client',cid,expected_client(cid,order)),'client')
    return {'command_rpc_deliveries':3,'control_rpc_deliveries':5,'server_events':23,'client_events':13}

def parse_stream(stdout, stderr, complete=True):
    require(stderr==b'', 'nonempty stderr')
    text=stdout.decode('utf-8','strict')
    events=[]; results=[]; banners=0
    for line in text.splitlines():
        if line=='': continue
        if line==BANNER:
            banners+=1; require(banners==1,'duplicate banner')
        elif line.startswith('EVENT_JSON='):
            require(not results,'event after final')
            events.append(loads(line[len('EVENT_JSON='):]))
        elif line.startswith('RESULT_JSON='):
            results.append(loads(line[len('RESULT_JSON='):]))
            require(len(results)==1,'duplicate final')
        else: raise ValueError('unexpected stdout line: '+line[:160])
    if complete:
        require(banners==1 and len(results)==1,'missing banner/final')
        equal(results[0]['trace'],events,'raw/parsed trace')
    return events, results
