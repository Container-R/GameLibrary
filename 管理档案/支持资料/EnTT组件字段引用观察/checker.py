"""Strict eleven-line content checker; not a native execution attestation."""
import json
from pathlib import Path

class CheckError(ValueError):
    pass

def need(condition, code):
    if not condition:
        raise CheckError(code)

def pairs(items):
    result = {}
    for key, value in items:
        need(key not in result, 'duplicate_json_key')
        result[key] = value
    return result

def reject_constant(_):
    raise CheckError('nonfinite_json')

def decode(text):
    return json.loads(text, object_pairs_hook=pairs, parse_constant=reject_constant)

def integer(value, maximum):
    return type(value) is int and 0 <= value <= maximum

def exact(left, right):
    if type(left) is not type(right):
        return False
    if type(left) is dict:
        return left.keys() == right.keys() and all(exact(left[k], right[k]) for k in left)
    if type(left) is list:
        return len(left) == len(right) and all(exact(a, b) for a, b in zip(left, right))
    return left == right

def keys(record, names):
    need(type(record) is dict and list(record) == names.split(), 'record_fields_or_order')

def handle(record):
    keys(record, 'full index version')
    need(integer(record['full'], 0xffffffff), 'handle_full')
    need(integer(record['index'], 0xfffff), 'handle_index')
    need(integer(record['version'], 0xfff), 'handle_version')
    need(record['index'] == (record['full'] & 0xfffff), 'handle_index_split')
    need(record['version'] == (record['full'] >> 20), 'handle_version_split')

def check(raw, oracle_path):
    need(type(raw) is bytes and len(raw) <= 65536, 'output_size')
    text = raw.decode('utf-8', errors='strict')
    need(text.endswith('\n') and '\r' not in text, 'line_endings')
    lines = text.splitlines()
    need(len(lines) == 11 and all(lines), 'eleven_records')
    records = [decode(line) for line in lines]
    oracle = decode(Path(oracle_path).read_text(encoding='utf-8'))
    need(exact(oracle.get('success_line_count'),11) and len(oracle['stages'])==3 and len(oracle['tokens'])==7,'oracle_shape')
    d=records[0]
    keys(d,'kind schema cplusplus gcc clang entt entity_mask version_mask')
    need(d['kind']=='declaration' and exact(d['schema'],1),'declaration')
    need(integer(d['cplusplus'],2**64-1) and d['cplusplus']>=oracle['declaration']['cplusplus_min'],'cplusplus')
    for n in ['gcc','clang']:
        v=d[n]; need(v is None or (type(v) is list and len(v)==3 and all(integer(x,2**32-1) for x in v)),'macro')
    for n in ['entt','entity_mask','version_mask']: need(exact(d[n],oracle['declaration'][n]),'declaration_'+n)
    stages=records[8:]
    names='kind stage remote_box remote_holder local_seed mapped_box mapped_holder source_target archive_target input_target loaded_target source_box_valid source_holder_valid seed_valid box_contains holder_contains mapped_box_valid mapped_holder_valid holder_has_link target_active_count target_link_count entity_written link_written entity_read link_read loaded_target_in_local_valid loaded_target_equals_seed'
    for row,e in zip(stages,oracle['stages']):
        keys(row,names); need(row['kind']=='stage' and row['stage']==e['name'],'stage_identity')
        for f in ['remote_box','remote_holder','local_seed','mapped_box','mapped_holder','source_target','archive_target']: handle(row[f])
        for f in ['input_target','loaded_target']:
            if row[f] is not None: handle(row[f])
        for f in ['source_box_valid','source_holder_valid','seed_valid']:need(exact(row[f],True),'live_source')
        literal={'box_contains':e['contains'][0],'holder_contains':e['contains'][1],'mapped_box_valid':e['mapped_valid'][0],'mapped_holder_valid':e['mapped_valid'][1],'holder_has_link':e['holder_has_link'],'target_active_count':e['active'],'target_link_count':e['links'],'entity_read':e['read_counts'][0],'link_read':e['read_counts'][1],'entity_written':oracle['writer_calls']['entities'],'link_written':oracle['writer_calls']['links']}
        for f,v in literal.items():need(exact(row[f],v),'literal_'+f)
    first,mapped,last=stages
    R,H,S=[first[n] for n in ['remote_box','remote_holder','local_seed']]
    need(all(x['full']!=0xffffffff for x in [R,H,S]) and not exact(R,H),'source_identity')
    B,L=mapped['mapped_box'],mapped['mapped_holder']
    # Only known-live identities; prepared map retains canonical null.
    for live in [R,H,S,B,L]:
        need(live['index'] != 0xfffff and live['version'] != 0xfff, 'live_reserved_handle')
    need(len({S['full'],B['full'],L['full']})==3 and B['full']!=0xffffffff and L['full']!=0xffffffff and not exact(B,R),'distinct_mapping')
    for row in stages:
        for f in ['remote_box','remote_holder','local_seed']:need(exact(row[f],first[f]),'stable_identity')
        need(exact(row['source_target'],R) and exact(row['archive_target'],R),'source_archive_target')
    for f in ['mapped_box','mapped_holder']:need(exact(first[f],oracle['types']['null_handle']),'initial_null');need(exact(last[f],mapped[f]),'stable_mapping')
    for row in stages[:2]:
        for f in ['input_target','loaded_target','loaded_target_in_local_valid','loaded_target_equals_seed']:need(row[f] is None,'unobserved')
    need(exact(last['input_target'],R) and exact(last['loaded_target'],R) and not exact(last['loaded_target'],B),'field_not_remapped')
    need(exact(last['loaded_target_equals_seed'],R['full']==S['full']),'equals_seed')
    need(exact(last['loaded_target_in_local_valid'],R['full'] in {S['full'],B['full'],L['full']}),'target_membership')
    for i,(t,e) in enumerate(zip(records[1:8],oracle['tokens'])):
        keys(t,'kind stream index type value');need(t['kind']=='token','token_kind')
        for f in ['stream','index','type']:need(exact(t[f],e[f]),'token_'+f)
        if i in [0,1,4]:need(exact(t['value'],e['value']),'token_count')
        elif i in [2,3,5]:handle(t['value'])
        else:keys(t['value'],'target');handle(t['value']['target']);need(exact(t['value']['target'],R),'token_target')
    need({records[3]['value']['full'],records[4]['value']['full']}=={R['full'],H['full']},'entity_tokens')
    need(exact(records[6]['value'],H),'component_owner')
    return records
