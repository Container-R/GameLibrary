import json,hashlib,sys
from pathlib import Path
if sys.flags.optimize: raise SystemExit('optimization unsupported')
root=Path(sys.argv[1]); out={}
expected={'seek_cross':[['single'],['single','single']], 'advance_cross':[['single'],['single']], 'seek_exact':[['single']], 'seek_exact_update_only':[[]], 'seek_two_cross':[['B'],['B','B']], 'advance_two_cross':[['A','B'],['A','B']]}
for case,steps in expected.items():
    lines=(root/(case+'.stdout.txt')).read_text().splitlines()
    cfg=json.loads(next(x[7:] for x in lines if x.startswith('CONFIG ')))
    rows=[json.loads(x[6:]) for x in lines if x.startswith('TRACE ')]
    after=[x for x in rows if x['kind']=='after']
    assert [r['labels'] for r in after]==steps
    assert (cfg['process_mode'],cfg['method_mode'],cfg['loop'])==(2,1,0)
    assert cfg['version']['hash']=='7d41c59c457bd5a245092b4e7eb2d833e3b3f8c3'
    delivered=[]; done=0
    for r in rows:
        if r['kind']=='method':
            assert r['labels'][:-1]==delivered
            delivered.append(r['labels'][-1])
        if r['kind']=='finished': done+=1
        assert r['hits']==len(delivered) and r['labels']==delivered and r['finishes']==done
    assert delivered==steps[-1]
    assert done==int(case.startswith('advance'))
    assert sum(x=='SIGNAL attack_visual' for x in lines)==done
    values=[0.75,1.0] if case.endswith('cross') else [0.5]
    assert all(abs(r['sample']-v)<1e-6 and abs(r['position']-v)<1e-6 for r,v in zip(after,values))
    assert rows[0]['sample']==0 and rows[0]['position']==0 and rows[0]['labels']==[]
    assert not (root/(case+'.stderr.txt')).read_text()
    out[case]={'labels_after':steps,'sample_after':[r['sample'] for r in after],'finished':done,'method_calls':len(delivered)}
print(json.dumps(out,indent=2))
