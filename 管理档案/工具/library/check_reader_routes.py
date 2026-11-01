"""Fail-closed shelf coverage against caller-declared frozen IDs; not prose quality."""
import argparse
import json
import math
from pathlib import Path, PurePosixPath
import re
from urllib.parse import unquote, urlsplit


def strict_json(text):
    def pairs(items):
        result={}
        for key,value in items:
            if key in result:raise ValueError('duplicate JSON key')
            result[key]=value
        return result
    def constant(value):raise ValueError('nonfinite JSON')
    def number(value):
        result=float(value)
        if not math.isfinite(result):raise ValueError('nonfinite JSON')
        return result
    return json.loads(text,object_pairs_hook=pairs,parse_float=number,parse_constant=constant)


def local(root, value):
    if not isinstance(value,str) or not value or '\\' in value or ':' in value or any(ord(c)<32 for c in value):raise ValueError('invalid local path')
    if PurePosixPath(value).is_absolute() or any(p in ('','.','..') for p in value.split('/')):raise ValueError('unnormalized local path')
    p=(root/value).resolve()
    if not p.is_relative_to(root):raise ValueError('path escapes root')
    if not p.is_file():raise ValueError('missing file')
    return p


def check(root, expected_count, expected_ids):
    root=root.resolve()
    if not root.is_dir():raise ValueError('missing root')
    if type(expected_count) is not int or expected_count<=0:raise ValueError('positive expected count required')
    if not isinstance(expected_ids,list) or len(expected_ids)!=expected_count or any(not isinstance(i,str) or not i.strip() for i in expected_ids) or len(set(expected_ids))!=len(expected_ids):raise ValueError('frozen IDs must be unique nonempty and match count')
    manifest=strict_json(local(root,'管理档案/图书目录.json').read_text())
    if not isinstance(manifest,dict):raise ValueError('manifest must be an object')
    entries=manifest.get('entries')
    if not isinstance(entries,list) or len(entries)!=expected_count:raise ValueError('inventory count mismatch')
    ids=[x.get('internal_id') for x in entries if isinstance(x,dict)]
    if len(ids)!=expected_count or any(not isinstance(i,str) for i in ids) or len(set(ids))!=expected_count or set(ids)!=set(expected_ids):raise ValueError('inventory IDs differ from frozen IDs')
    errors=[];seen=set()
    for item in entries:
        ident=item['internal_id']
        try:
            parts=[item[k] for k in ('floor','area','shelf')]
            if any(not isinstance(x,str) or '/' in x or x in ('','.','..') for x in parts):raise ValueError('invalid shelf component')
            shelf=local(root,'/'.join(['GameLibrary',*parts,'README.md']))
            path=item['current_read_path'];canonical=item['canonical_reader_path']
            if path!=canonical or not path.startswith('GameLibrary/') or not path.endswith('.md'):raise ValueError('canonical/current mismatch')
            target=local(root,path)
            if target in seen:raise ValueError('duplicate target')
            seen.add(target)
            title=item['reader_title']
            if not isinstance(title,str) or not title.strip() or target.read_text().splitlines()[:1]!=['# '+title]:raise ValueError('H1 mismatch')
            targets=[]
            for u in re.findall(r'\]\(([^)]+)\)',shelf.read_text()):
                if urlsplit(u).scheme or u.startswith('#'):continue
                p=(shelf.parent/unquote(u.split('#')[0])).resolve()
                if not p.is_relative_to(root):raise ValueError('shelf link escapes root')
                targets.append(p)
            if target not in targets:raise ValueError('entry missing from shelf')
        except (ValueError,KeyError,TypeError,OSError):errors.append({'id':ident,'status':'invalid_shelf_or_article'})
    return {'inventory_entries_checked':len(entries),'errors':errors,'scope':'Frozen-ID shelf coverage and titles only; not editorial quality or source verification'}


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--root',required=True,type=Path);p.add_argument('--expected-count',required=True,type=int);p.add_argument('--expected-ids',required=True,type=Path)
    a=p.parse_args()
    try:r=check(a.root,a.expected_count,strict_json(a.expected_ids.read_text()))
    except (ValueError,KeyError,TypeError,OSError):print('{"status":"configuration_error"}');return 1
    print(json.dumps(r,ensure_ascii=False));return int(bool(r['errors']))

if __name__=='__main__':raise SystemExit(main())
