import json,sys
from pathlib import Path
if sys.flags.optimize:raise SystemExit('no -O')
r=Path(sys.argv[1]); expected={'baseline':['One key','Many keys'],'literal_only':['Óné kéy','Mány kéys'],'swapped':['Many keys','One key']};rows={}; libs=[]
for name in ['baseline','naive','literal_only','swapped']:
    text=(r/(name+'.stdout.txt')).read_text(); lines=text.splitlines()
    assert len(lines)==1 and lines[0].startswith('RESULT_JSON=')
    d=json.loads(lines[0][12:]); assert d['case']==name and d['locale']=='en' and d['version']==[76,1,0,0]
    assert d['pattern_utf16_units']==len(d['pattern'].encode('utf-16-le'))//2
    libs.append(d['libraries']); assert not (r/(name+'.stderr.txt')).read_text()
    if name=='naive':
        assert d['open']['code']==65799 and d['open']['name']=='U_PATTERN_SYNTAX_ERROR' and not d['open']['success']
        assert d['open']['handle_nonnull'] and d['format_calls']==[]
    else:
        assert d['open']['code']==0 and d['open']['success'] and d['open']['handle_nonnull']
        calls=d['format_calls']; assert [c['number'] for c in calls]==[1.0,2.0]
        assert [c['output'] for c in calls]==expected[name]
        assert [c['status']['code'] for c in calls]==[-127,0]
        for c in calls:
            assert c['c_argument_type']=='double' and c['status']['success']
            assert c['returned_length']==len(c['output'].encode('utf-16-le'))//2 < c['capacity_utf16']
    rows[name]={'open':d['open'],'format_calls':d['format_calls']}
assert all(libs[0]==x for x in libs)
print(json.dumps({'checks':'passed','cases':rows,'libraries':libs[0]},ensure_ascii=False,indent=2))
