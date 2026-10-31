"""Read-only finite archive check. No imports of archived code or child launches."""
import ast, hashlib, json, math
from pathlib import Path, PurePosixPath
ROOT=Path(__file__).resolve().parents[4]
A=ROOT/'research/audits/runner-isolation'
KEYS={'HOME','XDG_CACHE_HOME','XDG_CONFIG_HOME','XDG_DATA_HOME','TMPDIR'}
def require(value,message):
    if not value: raise ValueError(message)
def pairs(items):
    result={}
    for k,v in items:
        require(k not in result,'duplicate JSON key');result[k]=v
    return result
def bad(value): raise ValueError('nonfinite JSON')
def floating(value):
    x=float(value);require(math.isfinite(x),'nonfinite float');return x
def parse(text): return json.loads(text,object_pairs_hook=pairs,parse_constant=bad,parse_float=floating)
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
INITIAL={'isolation.py':'1694c02b779462ee84c3e012094764572612a7fa01801380748752a49d3cd36a','protocol.json':'2717199e1cb4800b3e42665307657e8257e39ff90863c1e7dfd82fe18251e712','test_isolation.py':'5c5692cc1dd21f13fcf3f3c40d2c52d16badb442ad093b81bbb78783a0097037'}
FINAL={'isolation.py':'bcade74136ae51643b00c5bac60a05655d76db3765250481dde843cc9d4f3970','protocol.json':'543f5a4b9388dd1bc95350fd78ab284ac31701282e8bfe5a49258bed7f505d26','test_isolation.py':'1a9e1553dbeaacf6cc87e8d90c3c0270b6eb69873d5b6d5ca591704d437d082d'}
groups=[('author/historical-pre-root-guard','author/historical-pre-root-guard',INITIAL),('author','author',FINAL),('review','review/fixture',INITIAL),('review/final','review/final/fixture',FINAL)]
suites=[]
for logs,src,pins in groups:
    actual={name:digest(A/src/name) for name in pins};require(actual==pins,'source pin mismatch')
    tree=ast.parse((A/src/'test_isolation.py').read_text())
    codes=[n.value.value for n in ast.walk(tree) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='code' for t in n.targets) and isinstance(n.value,ast.Constant) and isinstance(n.value.value,str)]
    require(len(codes)==1,'child code ambiguity')
    for opt,name in enumerate(('normal','optimized')):
        lines=(A/logs/(name+'.stdout')).read_text().splitlines()
        require(len(lines)==1 and lines[0].startswith('RESULT_JSON='),'unexpected stdout')
        d=parse(lines[0][12:]);require(d['source_sha256']==actual,'source/result mismatch')
        for key,value in {'status':'PASS','test_methods':5,'optimization':opt,'synthetic_children':1,'engine_processes':0}.items():
            require(type(d[key]) is type(value) and d[key]==value,'suite field '+key)
        stderr=(A/logs/(name+'.stderr')).read_text()
        require('Ran 5 tests in ' in stderr and stderr.rstrip().endswith('OK') and 'FAILED' not in stderr,'suite stderr')
        c=d['child'];require(type(c['returncode']) is int and c['returncode']==0 and c['stderr']=='' and c['timeout_seconds']==5,'child outcome')
        require(len(c['argv'])==4 and c['argv'][1:]==['-I','-c',codes[0]],'child command')
        env=c['selected_environment'];require(set(env)==KEYS and parse(c['stdout'])==env,'selected manifest')
        paths=[PurePosixPath(env[k]) for k in sorted(KEYS)]
        require(all(p.is_absolute() and '..' not in p.parts and p.name==k for k,p in zip(sorted(KEYS),paths)),'path format')
        require(len({p.parent for p in paths})==1 and len(set(paths))==5,'directory mapping')
        suites.append(logs+'/'+name)
for folder in ('review','review/final'):
    for name in ('additional.json','additional-optimized.json'):
        d=parse((A/folder/name).read_text())
        require(d=={'status':'PASS','checks':['ancestor symlink','literal parent traversal','dangling reserved symlink','partial creation propagates and remains caller owned; base unchanged'],'synthetic_children':0,'engine_processes':0},'supplementary record')
require(digest(ROOT/'scripts/evidence/isolation.py')==FINAL['isolation.py'],'production helper identity')
preserved=parse((A/'integration/preserved-files.json').read_text())
require(len(preserved['files'])==preserved['count']==1723,'preservation count')
for p,h in preserved['files'].items():require(digest(ROOT/p)==h,'historical file changed: '+p)
print(json.dumps({'status':'PASS','archived_suites':suites,'archived_synthetic_children':8,'archived_engine_processes':0,'supplementary_unique_scenarios':4,'historical_files_unchanged':1723,'checker_child_processes':0,'scope':'Static consistency only; removed temporary sentinel files are not rechecked; no authenticity or complete isolation claim'},indent=2))
