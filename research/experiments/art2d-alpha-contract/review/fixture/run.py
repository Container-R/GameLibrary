"""Finite original raw-buffer representation test; not artwork or color management."""
import hashlib,json,sys
from pathlib import Path
from fractions import Fraction
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'results';OUT.mkdir(exist_ok=True)
(OUT/'summary.json').unlink(missing_ok=True)
if sys.flags.optimize:raise SystemExit('optimized invocation rejected')
import PIL
from PIL import Image,_imaging

def need(ok,msg):
    if not ok:raise RuntimeError(msg)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def image(mode,values):return Image.frombytes(mode,(1,1),bytes(values))
def values(im):return list(im.tobytes())
operations=[]
def convert(name,source,mode,want):
    result=source.convert(mode);got=values(result)
    operations.append(dict(name=name,operation='convert',input_mode=source.mode,input_bytes=values(source),output_mode=result.mode,output_bytes=got))
    need(got==list(want) and result.mode==mode,name)
    return result
def over(name,source,want):
    background=image('RGBA',(0,0,0,255));result=Image.alpha_composite(background,source);got=values(result)
    operations.append(dict(name=name,operation='alpha_composite',input_mode=source.mode,input_bytes=values(source),background_bytes=values(background),output_mode=result.mode,output_bytes=got))
    need(got==list(want) and result.mode=='RGBA',name)
    return result
# Exact rational oracle in stored-byte domain, not copied Pillow integer implementation.
def nearest(x):return (2*x.numerator+x.denominator)//(2*x.denominator)
a=Fraction(85,255)
correct=[nearest(Fraction(c)*a) for c in (240,120,60)]+[255]
wrong=[nearest(Fraction(c)*a) for c in (80,40,20)]+[255]
need(correct==[80,40,20,255] and wrong==[27,13,7,255],'frozen rational expectations')
source=image('RGBA',(240,120,60,85))
associated=convert('associate',source,'RGBa',(80,40,20,85))
restored=convert('unassociate-exact-selected-tuple',associated,'RGBA',(240,120,60,85))
over('correct-straight',source,correct);over('correct-converted',restored,correct)
misread=Image.frombytes('RGBA',(1,1),associated.tobytes())
over('misinterpreted-associated-bytes-as-straight',misread,wrong)
opaque=image('RGBA',(240,120,60,255));convert('opaque-associate',opaque,'RGBa',(240,120,60,255));over('opaque-over',opaque,(240,120,60,255))
transparent=image('RGBA',(240,120,60,0));zero=convert('transparent-associate',transparent,'RGBa',(0,0,0,0));zero_restored=convert('transparent-unassociate',zero,'RGBA',(0,0,0,0))
need(zero_restored.tobytes()!=transparent.tobytes(),'hidden color not recovered')
over('transparent-original-over',transparent,(0,0,0,255));over('transparent-converted-over',zero_restored,(0,0,0,255))
summary=dict(status='PASS',scope='five finite raw-buffer groups; stored-byte arithmetic, no color management/PNG/GPU',python=sys.version,pillow=PIL.__version__,
 source_sha256={f:sha(ROOT/f) for f in ('run.py','contract.md')},runtime_files={str(p):sha(p) for p in (Path(sys.executable).resolve(),Path(PIL.__file__),Path(Image.__file__),Path(_imaging.__file__))},
 groups=5,conversion_calls=5,composite_calls=6,rational_alpha=[1,3],operations=operations)
need(len(operations)==11,'finite operation count')
(OUT/'summary.json').write_text(json.dumps(summary,indent=2)+'\n');print('RESULT_JSON '+json.dumps(summary,sort_keys=True))
