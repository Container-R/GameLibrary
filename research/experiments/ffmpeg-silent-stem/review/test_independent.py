"""Pure synthetic checker probes. Author helper supplies receipt scaffolding only;
independent checker never imports it or uses its semantic oracle."""
import sys,tempfile,copy,json
from pathlib import Path
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE/'final-code-copy'))
import test_pure as fixtures
import check_literal as independent
results=[]
with tempfile.TemporaryDirectory() as td:
    root=Path(td);r,out=fixtures.synthetic(root)
    independent.check(root);results.append({'case':'synthetic control','accepted':True})
    for kind in ['shifted-boundary','non-UTC','bool-return','timeout-flag','environment','wrong-library','missing-process','stderr']:
        x=copy.deepcopy(r)
        if kind=='shifted-boundary':
            b=bytes.fromhex('0000803e')*2049+bytes.fromhex('0000003f')*2047
            (out/'short-normalized.hex').write_text(b.hex()+'\n')
            x['outputs']['short-normalized']['archive']={'bytes':len(b),'sha256':independent.digest(b)}
        if kind=='non-UTC':
            for p in x['processes']:
                for k in ['attempted_utc','returned_utc']:p[k]=p[k].replace('+00:00','+01:00')
        if kind=='bool-return':x['processes'][0]['returncode']=False
        if kind=='timeout-flag':x['processes'][1]['timeout']=True
        if kind=='environment':x['processes'][0]['environment']['LD_PRELOAD']='fake'
        if kind=='wrong-library':x['tools_after']['/lib/x86_64-linux-gnu/libavfilter.so.10']='0'*64
        if kind=='missing-process':x['processes'].pop()
        if kind=='stderr':
            b=b'ERROR synthetic\n';(out/'short-unscaled.stderr').write_bytes(b);x['processes'][3]['stderr_sha256']=independent.digest(b)
        fixtures.bind(root,x)
        try:independent.check(root)
        except (ValueError,KeyError) as error:results.append({'case':kind,'rejected':True,'reason':str(error)})
        else:raise RuntimeError('false accepted '+kind)
        (out/'short-normalized.hex').write_text((bytes.fromhex('0000803e')*2048+bytes.fromhex('0000003f')*2048).hex()+'\n')
        (out/'short-unscaled.stderr').write_bytes(b'')
print(json.dumps({'kind':'pure synthetic; no native execution','results':results},indent=2))
