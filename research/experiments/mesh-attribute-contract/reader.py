"""Original deliberately restricted glTF data contract; not a full validator."""
import math
import struct

def need(ok, why):
    if not ok: raise ValueError(why)

def integer(x, minimum=0):
    need(type(x) is int and x >= minimum, 'integer domain')
    return x

def read(doc, blob):
    need(doc['asset']['version']=='2.0','version')
    need(not doc.get('extensionsUsed') and not doc.get('extensionsRequired'),'extensions excluded')
    need(len(doc['buffers'])==1 and len(doc['meshes'])==1,'subset cardinality')
    length=integer(doc['buffers'][0]['byteLength'],1)
    need(length==len(blob),'backing buffer length')
    primitives=doc['meshes'][0]['primitives']; need(len(primitives)==1,'one primitive')
    primitive=primitives[0];need(primitive.get('mode',4)==4,'triangles only')
    need(set(primitive['attributes'])=={'POSITION','NORMAL'},'attributes subset')
    def accessor(index, role):
        index=integer(index);need(index<len(doc['accessors']),'accessor index')
        a=doc['accessors'][index]
        need('sparse' not in a and not a.get('normalized',False) and not a.get('extensions'),'accessor subset')
        vi=integer(a['bufferView']);need(vi<len(doc['bufferViews']),'view index')
        v=doc['bufferViews'][vi];need(v['buffer']==0 and not v.get('extensions'),'view subset')
        start=integer(v.get('byteOffset',0));span=integer(v['byteLength'],1)
        need(start+span<=length,'view outside declared buffer')
        vertex=role!='indices'
        need((a['componentType'],a['type'])==((5126,'VEC3') if vertex else (5123,'SCALAR')),'accessor type subset')
        size,component,fmt=(12,4,'<3f') if vertex else (2,2,'<H')
        offset=integer(a.get('byteOffset',0));count=integer(a['count'],1)
        need(offset%component==0 and start%component==0,'component alignment')
        if vertex:need(offset%4==0,'vertex alignment')
        need(v.get('target',34962 if vertex else 34963)==(34962 if vertex else 34963),'target role')
        if 'byteStride' in v:
            stride=integer(v['byteStride'],4)
            need(vertex,'indices must not have stride')
            need(stride<=252 and stride%4==0 and stride<=span and stride>=size,'stride domain')
        else:stride=size
        end=offset+(count-1)*stride+size
        need(end<=span,'accessor outside declared view')
        values=[struct.unpack_from(fmt,blob,start+offset+i*stride) for i in range(count)]
        need(all(math.isfinite(x) for row in values for x in row),'nonfinite attribute')
        if role=='POSITION':
            need(a.get('min')==[min(row[j] for row in values) for j in range(3)] and
                 a.get('max')==[max(row[j] for row in values) for j in range(3)],'position bounds')
        return values,vi
    pos,pv=accessor(primitive['attributes']['POSITION'],'POSITION')
    norm,nv=accessor(primitive['attributes']['NORMAL'],'NORMAL')
    need(len(pos)==len(norm),'attribute count mismatch')
    need(all(abs(sum(x*x for x in n)-1)<1e-6 for n in norm),'normal unit length')
    if pv==nv:need('byteStride' in doc['bufferViews'][pv],'shared attributes need stride')
    raw,iv=accessor(primitive['indices'],'indices');need(iv not in (pv,nv),'mixed view use')
    indices=[x[0] for x in raw]
    need(len(indices)%3==0,'triangle index count')
    need(all(i!=65535 for i in indices),'forbidden maximal index')
    need(all(i<len(pos) for i in indices),'index outside vertices')
    return dict(positions=pos,normals=norm,indices=indices,
                triangles=[[pos[i] for i in indices[j:j+3]] for j in range(0,len(indices),3)])
