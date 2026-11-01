"""Finite accessor subset, not a glTF validator or URI loader."""
import math
import struct

class Rejected(ValueError):
    pass

def need(ok, code):
    if not ok:
        raise Rejected(code)

def integer(v, low=0, high=44):
    need(type(v) is int, 'unsupported_metadata_number_encoding')
    need(low <= v <= high, 'metadata_range')
    return v

def fields(obj, required, optional=()):
    need(type(obj) is dict, 'unsupported_object')
    need(set(required) <= set(obj) <= set(required) | set(optional), 'unsupported_fields')

def decode(doc, blob):
    fields(doc, ('asset','buffers','bufferViews','accessors'))
    fields(doc['asset'], ('version',))
    need(doc['asset']['version'] == '2.0', 'unsupported_version')
    need(type(blob) is bytes and len(blob) == 44, 'backing_length')
    for key, size in [('buffers',1),('bufferViews',3),('accessors',1)]:
        need(type(doc[key]) is list and len(doc[key]) == size, 'subset_cardinality')
    b = doc['buffers'][0]
    fields(b, ('byteLength','uri'))
    need(integer(b['byteLength']) == len(blob), 'backing_length')
    need(type(b['uri']) is str, 'unsupported_uri')
    views = doc['bufferViews']
    for v in views:
        fields(v, ('buffer','byteLength'), ('byteOffset','byteStride','target'))
        need(integer(v['buffer'], high=0) == 0, 'buffer_index')
        off = integer(v.get('byteOffset',0)); length = integer(v['byteLength'],1)
        need(off + length <= len(blob), 'view_backing_bounds')
    a = doc['accessors'][0]
    fields(a, ('componentType','count','type','sparse'), ('bufferView','byteOffset'))
    need(integer(a['componentType'], high=5126) == 5126 and a['type'] == 'SCALAR', 'unsupported_accessor_type')
    count = integer(a['count'],1,4)
    s = a['sparse']; fields(s, ('count','indices','values'))
    n = integer(s['count'],1,count)
    ix = s['indices']; val = s['values']
    fields(ix, ('bufferView','componentType'), ('byteOffset',))
    fields(val, ('bufferView',), ('byteOffset',))
    need(integer(ix['componentType'], high=5126) == 5123, 'unsupported_index_type')
    def span(ref, size, number, sparse, code):
        vi = integer(ref['bufferView'], high=2); v = views[vi]
        if sparse:
            need('target' not in v and 'byteStride' not in v, 'sparse_view_layout_forbidden')
        else:
            need('target' not in v and 'byteStride' not in v, 'unsupported_base_layout')
        off = integer(ref.get('byteOffset',0)); base = integer(v.get('byteOffset',0))
        need(base % size == 0 and off % size == 0, 'component_alignment')
        need(off + size * number <= v['byteLength'], code)
        return [base + off + j * size for j in range(number)]
    if 'bufferView' in a:
        base_addresses = span(a,4,count,False,'base_view_bounds')
        output = [struct.unpack_from('<f',blob,p)[0] for p in base_addresses]
    else:
        need('byteOffset' not in a, 'unsupported_absent_base_offset')
        base_addresses = [None] * count
        output = [0.0] * count
    need(all(math.isfinite(v) for v in output), 'nonfinite_float')
    index_addresses = span(ix,2,n,True,'sparse_indices_view_bounds')
    value_addresses = span(val,4,n,True,'sparse_values_view_bounds')
    indices = [struct.unpack_from('<H',blob,p)[0] for p in index_addresses]
    need(all(i < count for i in indices), 'sparse_index_out_of_range')
    need(all(x < y for x,y in zip(indices,indices[1:])), 'sparse_indices_not_strictly_increasing')
    values = [struct.unpack_from('<f',blob,p)[0] for p in value_addresses]
    need(all(math.isfinite(v) for v in values), 'nonfinite_float')
    for i,v in zip(indices,values):
        output[i] = v
    return {'values':output,'base_addresses':base_addresses,'index_addresses':index_addresses,
            'value_addresses':value_addresses,'indices':indices,'replacement_values':values}
