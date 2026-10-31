"""Independent finite artifact oracle; no author module import."""
import base64,hashlib,io,json,struct,sys
from pathlib import Path
from PIL import Image
if sys.flags.optimize: raise SystemExit('Refusing optimized assertions')
r=Path(sys.argv[1]); s=json.loads((r/'summary.json').read_text())
def decode(name):return base64.b64decode((r/name).read_text().strip(),validate=True)
b=decode('markers.dds.base64'); assert len(b)==1792
assert hashlib.sha256(b).hexdigest()=='1e8f263dbf5aafe04b26626ba7b17ef9ec455337d2f8fed3ddcdbcf145e2f20f'
assert s['artifact']==dict(bytes=1792,payload_bytes=1664,header_bytes=128,sha256=hashlib.sha256(b).hexdigest())
if (r/'markers.dds').exists(): assert b==(r/'markers.dds').read_bytes()
assert b[:4]==b'DDS '; assert struct.unpack_from('<I',b,28)[0]==6
rows=[(60,40,128,1200,0xf800,(255,0,0)),(30,20,1328,320,0x07e0,(0,255,0)),(15,10,1648,96,0x001f,(0,0,255)),(7,5,1744,32,0xffe0,(255,255,0)),(3,2,1776,8,0xf81f,(255,0,255)),(1,1,1784,8,0x07ff,(0,255,255))]
observed=[]
for i,(w,h,o,n,c,color) in enumerate(rows):
 part=b[o:o+n]; assert part==struct.pack('<HHI',c,0,0)*(n//8)
 wrapped=decode(f'mip-{i}.dds.base64'); assert len(wrapped)==128+n and wrapped[128:]==part
 assert struct.unpack_from('<II',wrapped,12)==(h,w)
 with Image.open(io.BytesIO(wrapped)) as im:
  im.load(); rgb=im.convert('RGB'); assert im.size==(w,h)
  assert rgb.tobytes()==bytes(color)*(w*h)
 d=s['decoded_mips'][i]; assert (d['source_offset'],d['payload_bytes'],d['colors'],d['pixel_count'])==(o,n,[list(color)],w*h)
 assert hashlib.sha256(wrapped).hexdigest()==d['wrapper_sha256']
 observed.append({'mip':i,'pixels_checked':w*h,'rgb':color})
assert decode('truncated.dds.base64')==b[:-8]
expected={(1,1):[8],(4,4):[8,8,8],(8,8):[32,8,8,8],(60,40):[1200,320,96,32,8,8],(7,5):[32,8,8],(1,8):[16,8,8,8],(17,17):[200,32,8,8,8]}
assert len(s['numeric_cases'])==14
seen=set()
for item in s['numeric_cases']:
 k=(item['width'],item['height']); f=item['format']; assert (k,f) not in seen; seen.add((k,f)); assert f in ('BC1','BC7')
 sizes=[n*(2 if f=='BC7' else 1) for n in expected[k]]
 assert [l['size'] for l in item['levels']]==sizes
 assert [l['payload_offset'] for l in item['levels']]==[sum(sizes[:i]) for i in range(len(sizes))]
 assert item['total_bytes']==sum(sizes)
assert s['invalid_cases_rejected']==6 and s['negative']['rejected'] and s['negative']['removed_bytes']==8
print(json.dumps({'status':'PASS','numeric_cases':14,'payload_bytes':1664,'file_bytes':1792,'independent_decodes':observed,'base64_identity':True},indent=2))
