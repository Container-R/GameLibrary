"""Finite original arithmetic/CPU decoder evidence. Run from any directory."""
import base64
import hashlib
import io
import json
from pathlib import Path
import struct
import sys
import PIL
from PIL import Image, DdsImagePlugin, _imaging
import model

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'results'
OUT.mkdir(exist_ok=True)
(OUT / 'summary.json').unlink(missing_ok=True)
if not __debug__:
    raise SystemExit('optimized invocation rejected')

def require(ok, message):
    if not ok:
        raise RuntimeError(message)

def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

# Manually enumerated, independent of model recurrence; (w,h,blockcount).
EXPECTED = {
    (1,1): [(1,1,1)],
    (4,4): [(4,4,1),(2,2,1),(1,1,1)],
    (8,8): [(8,8,4),(4,4,1),(2,2,1),(1,1,1)],
    (60,40): [(60,40,150),(30,20,40),(15,10,12),(7,5,4),(3,2,1),(1,1,1)],
    (7,5): [(7,5,4),(3,2,1),(1,1,1)],
    (1,8): [(1,8,2),(1,4,1),(1,2,1),(1,1,1)],
    (17,17): [(17,17,25),(8,8,4),(4,4,1),(2,2,1),(1,1,1)],
}
# Literal expected byte offsets/lengths for the full legacy DDS fixture.
CHAIN = [(60,40,128,1200),(30,20,1328,320),(15,10,1648,96),
         (7,5,1744,32),(3,2,1776,8),(1,1,1784,8)]

def check_fixture(blob):
    if len(blob) != 1792:
        raise ValueError('fixture length must be 1792 bytes')
    if blob[:4] != b'DDS ':
        raise ValueError('DDS magic')
    h = struct.unpack('<31I', blob[4:128])
    expected_header = (124, 0xa1007, 40, 60, 1200, 0, 6)
    if h[:7] != expected_header or h[7:18] != (0,)*11:
        raise ValueError('header dimensions/flags/reserved')
    if h[18:26] != (32,4,0x31545844,0,0,0,0,0) or h[26:] != (0x401008,0,0,0,0):
        raise ValueError('format/caps')
    return [blob[offset:offset+size] for _,_,offset,size in CHAIN]

numeric = []
for (w,h), levels in EXPECTED.items():
    for fmt, b in [('BC1',8), ('BC7',16)]:
        rows = model.layout(w,h,fmt)
        require([(r['width'],r['height'],r['size']) for r in rows] ==
                [(x,y,n*b) for x,y,n in levels], f'numeric mismatch {w,h,fmt}')
        require(sum(r['size'] for r in rows) == sum(n for _,_,n in levels)*b,'total')
        numeric.append(dict(width=w,height=h,format=fmt,levels=rows,
                            total_bytes=sum(r['size'] for r in rows)))
invalid = [(True,4,'BC1'),(0,4,'BC1'),(-1,4,'BC1'),(1.5,4,'BC1'),(4,False,'BC1'),(4,4,'BC9')]
for args in invalid:
    try:
        model.layout(*args)
    except ValueError:
        pass
    else:
        raise RuntimeError(f'invalid input accepted {args}')
blob = model.build()
parts = check_fixture(blob)
(OUT/'markers.dds').write_bytes(blob)
(OUT/'markers.dds.base64').write_text(base64.b64encode(blob).decode()+'\n')
require(base64.b64decode((OUT/'markers.dds.base64').read_text(), validate=False)==blob,'base64')
# Save the failed-input artifact, but never present it as a valid DDS.
truncated = blob[:-8]
(OUT/'truncated.dds.base64').write_text(base64.b64encode(truncated).decode()+'\n')
try:
    check_fixture(truncated)
except ValueError as e:
    negative = dict(removed_bytes=8, rejected=True, reason=str(e))
else:
    raise RuntimeError('truncated chain accepted')
decodes = []
for i, ((w,h,offset,size),part) in enumerate(zip(CHAIN,parts,strict=True)):
    wrapper = model.header(w,h,1,size) + part
    (OUT/f'mip-{i}.dds.base64').write_text(base64.b64encode(wrapper).decode()+'\n')
    with Image.open(io.BytesIO(wrapper)) as image:
        image.load()  # actual native codec work, not header inspection only
        require(image.size==(w,h),f'decode size {i}')
        rgb=image.convert('RGB')
        colors=set(rgb.getdata())
        require(colors=={model.MARKERS[i][1]},f'decode colors {i}: {colors}')
        decodes.append(dict(level=i,width=w,height=h,source_offset=offset,payload_bytes=size,
                            decoded_mode=image.mode,pixel_count=w*h,colors=sorted(colors),
                            wrapper_sha256=hashlib.sha256(wrapper).hexdigest()))
summary = dict(status='PASS', scope='finite tight payload model and CPU per-mip wrapped DDS decoding; no GPU',
               python=sys.version, pillow=PIL.__version__, source_sha256={p:sha(ROOT/p) for p in ('model.py','run.py')},
               runtime_files={str(p):sha(p) for p in (Path(sys.executable).resolve(),PIL.__file__,DdsImagePlugin.__file__,_imaging.__file__)},
               numeric_cases=numeric, invalid_cases_rejected=len(invalid),
               artifact=dict(bytes=len(blob),payload_bytes=1664,header_bytes=128,sha256=hashlib.sha256(blob).hexdigest()),
               negative=negative,decoded_mips=decodes)
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n')
print('RESULT_JSON '+json.dumps(summary,sort_keys=True))
