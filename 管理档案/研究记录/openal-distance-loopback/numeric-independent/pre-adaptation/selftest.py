"""Synthetic byte validation only; no audio library, playback or rendering."""
import base64, copy, hashlib, json, struct
from check_numeric import CASES, PARTS, Invalid, check_cases, read_json_lines, expected_factor

def window(part,value):
    raw=struct.pack('<4800f', *([value]*4800))
    return {'part':part,'frame_count':4800,'byte_count':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'base64':base64.b64encode(raw).decode()}

def fixture():
    return [{'id':name,'parameters':(model,ref,maximum,distance),'windows':[window(part,.03*expected_factor(model,ref,maximum,distance)) for part in PARTS]} for name,model,ref,maximum,distance in CASES]

def mutate_raw(case,part,value):
    case['windows'][part]=window(PARTS[part],value)

def main():
    check_cases(fixture()); passed=['synthetic_valid']
    tests={
        'bad_length':lambda a:a[0]['windows'][0].update(byte_count=1),
        'bad_base64':lambda a:a[0]['windows'][0].update(base64='!'*25600),
        'nan_sample':lambda a:mutate_raw(a[0],0,float('nan')),
        'inf_sample':lambda a:mutate_raw(a[0],1,float('inf')),
        'wrong_case':lambda a:a[1].update(id='linear-max'),
        'wrong_ratio':lambda a:[mutate_raw(a[1],i,.03*.2) for i in (1,2)],
        'missing_window':lambda a:a[1]['windows'].pop(),
        'missing_case':lambda a:a.pop(),
        'bad_digest':lambda a:a[0]['windows'][0].update(sha256='0'*64),
        'bool_frame_count':lambda a:a[0]['windows'][0].update(frame_count=True),
        'weak_baseline':lambda a:[mutate_raw(a[0],i,.0001) for i in (1,2)],
        'unstable_windows':lambda a:mutate_raw(a[2],2,.004),
        'linear_nonzero':lambda a:[mutate_raw(a[4],i,.000002) for i in (1,2)],
    }
    for name,change in tests.items():
        a=fixture();change(a)
        try:check_cases(a)
        except Invalid:passed.append(name);continue
        raise AssertionError(name)
    for name,text in [('duplicate_key','{"seq":0,"seq":0,"event":"x","case":null,"data":{}}'),('json_nan','{"seq":0,"event":"x","case":null,"data":{"x":NaN}}'),('bad_seq','{"seq":true,"event":"x","case":null,"data":{}}')]:
        try:read_json_lines(text)
        except Invalid:passed.append(name);continue
        raise AssertionError(name)
    print(json.dumps({'status':'PASS','scope':'pure synthetic offline selftest; not OpenAL output','checks':passed},sort_keys=True))

if __name__=='__main__':main()
