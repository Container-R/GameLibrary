"""Strict eight-line content checker; not a native execution attestation."""
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
    need(len(lines) == 8 and all(lines), 'eight_records')
    records = [decode(line) for line in lines]
    oracle = decode(Path(oracle_path).read_text(encoding='utf-8'))
    need(type(oracle) is dict and exact(oracle.get('schema'), 1), 'oracle_schema')
    need(type(oracle.get('stages')) is list and len(oracle['stages']) == 4, 'oracle_stages')
    need(type(oracle.get('tokens')) is list and len(oracle['tokens']) == 3, 'oracle_tokens')
    declaration = records[0]
    keys(declaration, 'kind schema cplusplus gcc clang entt entity_mask version_mask')
    need(declaration['kind'] == 'declaration' and exact(declaration['schema'], 1), 'declaration_identity')
    need(integer(declaration['cplusplus'], 0xffffffffffffffff) and declaration['cplusplus'] >= 201703, 'cplusplus')
    for name in ('gcc', 'clang'):
        value = declaration[name]
        need(value is None or (type(value) is list and len(value) == 3 and all(integer(x, 0xffffffff) for x in value)), 'compiler_macro')
    need(exact(declaration['entt'], [3, 13, 2]), 'entt_version')
    need(exact(declaration['entity_mask'], 0xfffff) and exact(declaration['version_mask'], 0xfff), 'traits')
    stages = records[4:]
    names = 'kind stage source seed mapped_now mapped_initial contains mapped_nonnull mapped_valid active_count initial_valid source_valid seed_valid input_consumed'
    for record, expected in zip(stages, oracle['stages']):
        keys(record, names)
        need(record['kind'] == 'stage', 'stage_kind')
        for field, value in expected.items():
            need(exact(record[field], value), 'stage_literal_' + field)
        for field in ('source', 'seed', 'mapped_now'):
            handle(record[field])
        need(record['source']['full'] != 0xffffffff and record['seed']['full'] != 0xffffffff, 'live_identity_not_null')
        if record['mapped_initial'] is not None:
            handle(record['mapped_initial'])
        need(record['mapped_nonnull'] == (record['mapped_now']['full'] != 0xffffffff), 'nonnull_relation')
    before, loaded, destroyed, reloaded = stages
    need(before['mapped_initial'] is None, 'initial_before')
    initial = loaded['mapped_initial']
    need(type(initial) is dict and initial['full'] != 0xffffffff, 'initial_loaded')
    need(exact(loaded['mapped_now'], initial), 'initial_assignment')
    for record in stages:
        need(exact(record['source'], before['source']) and exact(record['seed'], before['seed']), 'stable_source_seed')
    for record in stages[1:]:
        need(exact(record['mapped_initial'], initial), 'stable_initial')
        need(not exact(record['mapped_now'], record['seed']), 'seed_separate')
    need(exact(destroyed['mapped_now'], initial), 'stale_map_preserved')
    need(not exact(reloaded['mapped_now'], initial), 'restored_new_handle')
    for index, (token, expected) in enumerate(zip(records[1:4], oracle['tokens'])):
        keys(token, 'kind index type value')
        desired = dict(expected)
        if index == 2:
            need(desired['value'] == '$source.full', 'oracle_source_marker')
            desired['value'] = before['source']['full']
        need(exact(token, desired), 'archive_literal')
    return records
