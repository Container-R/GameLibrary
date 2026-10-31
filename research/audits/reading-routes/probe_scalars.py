import sys,json
from pathlib import Path
if len(sys.argv) != 2:
    raise SystemExit('usage: probe_scalars.py NAVIGATION_SOURCE_DIRECTORY')
NAV = Path(sys.argv[1]).resolve()
sys.path.insert(0, str(NAV))
from build_routes import metadata,Invalid
base='---\nid: SOL-A-001\ntitle: VALUE\ntype: solution\nstatus: source-backed\nprimary_discipline: PROG\n---\n'
for value in ['# only comment','foo: bar','null','[a, b]','foo\t# comment']:
    try: print(json.dumps({'value':value,'accepted':metadata(base.replace('VALUE',value))['title']}))
    except Invalid as exc: print(json.dumps({'value':value,'rejected':str(exc)}))
