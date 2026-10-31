from pathlib import Path
import json,hashlib,re
root=Path('/workspace/scratch/6d9a354d4cae');base=root/'gamelibrary-publish-rig';new=root/'gamelibrary-publish-applicability';audit=new/'research/audits/evidence-applicability-27'
def req(x,m):
 if not x:raise RuntimeError(m)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
i=json.loads((audit/'inventory.json').read_text());changes=json.loads((audit/'applied-corrections.json').read_text())['changes'];paths=[a['path'] for a in i['articles']];req(len(paths)==len(set(paths))==27,'inventory count')
cat=(base/'CATALOG.md').read_text();catalogpaths=set(re.findall(r'\]\(((?:roles|solutions|case-studies)/[^)#]+\.md)(?:#[^)]*)?\)',cat));req(set(paths)==catalogpaths,'catalog membership')
changed=[]
for a in i['articles']:
 p=a['path'];text=(base/p).read_text();req(sha(base/p)==a['sha256'],'baseline '+p);req(a['verification_method_verbatim'] in text.splitlines(),'verbatim')
 for c in changes:
  if c['path']==p:
   req(text.count(c['before'])==1,'unique replacement');text=text.replace(c['before'],c['after'])
 req(text==(new/p).read_text(),'minimal exact diff '+p)
 if sha(base/p)!=sha(new/p):changed.append(p)
for c in changes:req(sha(new/c['path'])==c['after_article_sha256'],'declared after hash')
oldfiles={str(p.relative_to(base)):sha(p) for p in (base/'research/experiments').rglob('*') if p.is_file()};newfiles={str(p.relative_to(new)):sha(p) for p in (new/'research/experiments').rglob('*') if p.is_file()};req(oldfiles==newfiles,'experiment preservation')
req(sha(new/'research/experiments/audio-lifecycle/model.py')=='435481726ef37bf5c1017ad0e9fdaf2327a1a93958c1afd95c78e41ddf610a25','audio model')
print(json.dumps({'status':'PASS','inventory_count':len(paths),'changed_articles':changed,'exact_replacements':len(changes),'unchanged_experiment_files':len(oldfiles),'current_article_hashes':{p:sha(new/p) for p in changed}},indent=2))
