"""Build a legacy-route management draft, never a reader entry or canonical catalog."""
import argparse
import html
import json
import os
import tempfile
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import quote

STATUSES={'verified','source-backed','experimental','disputed','outdated','needs-research'}
REQUIRED=('id','title','type','status','primary_discipline')
class Invalid(ValueError): pass

def json_object(pairs):
    result={}
    for key,value in pairs:
        if key in result: raise Invalid('duplicate registry key: '+key)
        result[key]=value
    return result

def registry_load(path):
    return json.loads(path.read_text(encoding='utf-8'),object_pairs_hook=json_object)

def scalar(value):
    # Only explicit text; ambiguous YAML scalar types must be quoted.
    if not value or '\\' in value:
        raise Invalid('unsupported required scalar: '+value)
    if value[0] in "\"'":
        if len(value)<2 or value[-1]!=value[0] or value[0] in value[1:-1]:
            raise Invalid('unsupported quoted scalar')
        value=value[1:-1]
    else:
        if value[0] in '|>&*!{[#' or re.search(r'\s#|:(?:\s|$)',value):
            raise Invalid('unsupported bare scalar syntax')
        if value.lower() in {'null','~','true','false','yes','no','on','off','.nan','.inf','+.inf','-.inf'} or re.match(r'^[+-]?(?:[0-9]|\.[0-9])',value):
            raise Invalid('ambiguous nontext scalar must be quoted')
    if not value.strip(): raise Invalid('empty required scalar')
    return value

def metadata(text):
    match=re.match(r'\A---\n(.*?)\n---(?:\n|$)',text,re.S)
    if not match: raise Invalid('missing frontmatter')
    result={}
    last_key=None
    for line in match.group(1).splitlines():
        if re.match(r'''^\s*(["'])(?:'''+ '|'.join(REQUIRED)+r''')\1\s*:''',line):
            raise Invalid('quoted required key unsupported')
        if line[:1].isspace() and line.strip() and last_key in REQUIRED:
            raise Invalid('multiline required scalar unsupported')
        m=re.match(r'^([a-z_]+):\s*(.*)$',line)
        if line and not line[0].isspace() and not line.startswith('#') and not m:
            raise Invalid('unsupported top-level frontmatter syntax')
        if m: last_key=m[1]
        if m and m[1] in REQUIRED:
            if m[1] in result: raise Invalid('duplicate required key: '+m[1])
            result[m[1]]=scalar(m[2])
        elif re.match(r'^\s+(?:'+'|'.join(REQUIRED)+r'):',line):
            raise Invalid('indented required key unsupported')
    if set(result)!=set(REQUIRED): raise Invalid('missing required metadata')
    if not re.fullmatch(r'[A-Z0-9]+(?:-[A-Z0-9]+)+',result['id']): raise Invalid('invalid document ID')
    if result['status'] not in STATUSES: raise Invalid('unknown status')
    if not re.fullmatch('[A-Z][A-Z0-9]*',result['primary_discipline']): raise Invalid('invalid discipline ID')
    if result['type'] not in {'role','knowledge','solution','case-study','comparison'}: raise Invalid('unknown document type')
    return result

def source_folders(root, source_dirs):
    """Read an explicitly declared, nonempty set of legacy frontmatter folders.

    This does not discover or certify the frontmatter-free reader library.
    Existing symlinks are bounded; hostile concurrent filesystem changes are
    outside this local maintenance tool's threat model.
    """
    root = root.resolve(strict=True)
    if not root.is_dir():
        raise Invalid('repository root must be a directory')
    if not isinstance(source_dirs, (list, tuple)) or not source_dirs:
        raise Invalid('declare at least one legacy source directory')
    folders = []
    for value in source_dirs:
        if not isinstance(value, str) or not value or value != value.strip():
            raise Invalid('source directory must be a normalized repository-relative path')
        pure = PurePosixPath(value)
        if (pure.is_absolute() or re.match(r'^[A-Za-z]:', value)
                or '\\' in value or any(ord(c) < 32 or ord(c) == 127 for c in value)
                or any(x in ('', '.', '..') for x in value.split('/'))):
            raise Invalid('source directory must be a normalized repository-relative path')
        folder = root / value
        if not folder.is_dir():
            raise Invalid('missing declared source directory: ' + value)
        resolved = folder.resolve(strict=True)
        if not resolved.is_relative_to(root):
            raise Invalid('source directory escapes root')
        if any(resolved.is_relative_to(prior) or prior.is_relative_to(resolved)
               for _, prior in folders):
            raise Invalid('duplicate or overlapping source directories')
        folders.append((folder, resolved))
    return folders


def documents(root, source_dirs):
    root = root.resolve(strict=True)
    folders = source_folders(root, source_dirs)
    docs = {}
    for folder, _ in folders:
        paths = sorted(folder.rglob('*.md'))
        if not paths:
            raise Invalid('declared source directory has no Markdown documents: '
                          + folder.relative_to(root).as_posix())
        for path in paths:
            if not path.resolve(strict=True).is_relative_to(root):
                raise Invalid('source path escapes root')
            doc = metadata(path.read_text(encoding='utf-8'))
            if doc['id'] in docs:
                raise Invalid('duplicate document ID')
            doc['path'] = path.relative_to(root).as_posix()
            docs[doc['id']] = doc
    if not docs:
        raise Invalid('no legacy documents scanned')
    return docs


def reader_documents(root, manifest, expected_count):
    """Read declared IDs/titles/paths, not editorial or per-book discipline claims."""
    root = root.resolve(strict=True)
    if not root.is_dir(): raise Invalid('repository root must be a directory')
    if type(expected_count) is not int or expected_count <= 0:
        raise Invalid('reader expected-count must be positive')
    if not isinstance(manifest, str) or not manifest or manifest != manifest.strip():
        raise Invalid('manifest must be normalized root-relative path')
    if (PurePosixPath(manifest).is_absolute() or re.match(r'^[A-Za-z]:', manifest)
            or '\\' in manifest or re.search(r'[\x00-\x1f\x7f]', manifest)
            or any(x in ('', '.', '..') for x in manifest.split('/'))):
        raise Invalid('manifest must be normalized root-relative path')
    manifest_path = (root / manifest).resolve(strict=True)
    if not manifest_path.is_relative_to(root): raise Invalid('manifest escapes root')
    data = registry_load(manifest_path)
    if not isinstance(data, dict) or not isinstance(data.get('entries'), list) or not data['entries']:
        raise Invalid('reader entries must be nonempty')
    docs = {}; paths = set()
    for entry in data['entries']:
        if not isinstance(entry, dict): raise Invalid('invalid reader entry')
        ident = entry.get('internal_id'); title = entry.get('reader_title')
        if not isinstance(ident, str) or not re.fullmatch(r'[A-Z0-9]+(?:-[A-Z0-9]+)+', ident):
            raise Invalid('invalid reader ID')
        plain(title)
        raw = entry.get('current_read_path')
        if (not isinstance(raw, str) or not raw.startswith('GameLibrary/') or not raw.endswith('.md')
                or '\\' in raw or re.search(r'[\x00-\x1f\x7f]',raw)
                or any(x in ('', '.', '..') for x in raw.split('/'))):
            raise Invalid('invalid reader path')
        if entry.get('canonical_reader_path') != raw:
            raise Invalid('current/canonical path mismatch')
        target = (root / raw).resolve(strict=True)
        if not target.is_relative_to(root/'GameLibrary'): raise Invalid('reader path escapes library')
        if ident in docs or target in paths: raise Invalid('duplicate reader ID/path')
        if any(target.samefile(prior) for prior in paths): raise Invalid('duplicate reader file')
        lines = target.read_text(encoding='utf-8').splitlines()
        if not lines or lines[0] != '# ' + title: raise Invalid('reader H1 mismatch')
        paths.add(target)
        docs[ident] = {'id':ident, 'title':title, 'path':raw,
                       'type':'role' if ident.startswith('ROLE-') else 'reader',
                       'status':'declared-reader'}
    if len(docs) != expected_count: raise Invalid('reader document count mismatch')
    return docs


def protect_inputs(output, inputs):
    for item in inputs:
        item = Path(item).resolve(strict=True)
        if output == item or (output.exists() and output.samefile(item)):
            raise Invalid('output overlaps an input file')


def plain(value):
    if not isinstance(value,str) or not value.strip() or '\n' in value or '\r' in value:
        raise Invalid('expected nonempty one-line text')
    # HTML text cannot create Markdown links, headings or raw HTML.
    return html.escape(value,quote=True).replace('[','&#91;').replace(']','&#93;').replace('`','&#96;').replace('*','&#42;').replace('_','&#95;')

def validate(reg,docs):
    if not isinstance(reg,dict) or set(reg)!={'schema_version','routes'} or type(reg['schema_version']) is not int or reg['schema_version']!=1:
        raise Invalid('invalid registry schema')
    routes=reg['routes']
    if not isinstance(routes,list) or not routes: raise Invalid('routes must be nonempty list')
    seen=set()
    for route in routes:
        if not isinstance(route,dict): raise Invalid('route must be object')
        kind=route.get('kind')
        expected={'id','title','kind','entries'}|({'subject_profile_id'} if kind=='role' else set())
        if kind not in {'role','problem'} or set(route)!=expected: raise Invalid('invalid route fields')
        ident=route['id']
        if not isinstance(ident,str) or not re.fullmatch('[a-z][a-z0-9-]*',ident) or ident in seen: raise Invalid('duplicate/invalid route ID')
        seen.add(ident);plain(route['title'])
        if kind=='role':
            if not isinstance(route['subject_profile_id'],str): raise Invalid('invalid subject profile ID')
            profile=docs.get(route['subject_profile_id'])
            if not profile or profile['type']!='role' or profile['status']=='needs-research': raise Invalid('role/profile mismatch')
        if not isinstance(route['entries'],list) or not route['entries']: raise Invalid('empty route entries')
        targets=set()
        for entry in route['entries']:
            if not isinstance(entry,dict) or set(entry)!={'document_id','question','rationale'}: raise Invalid('invalid entry')
            ident=entry['document_id']
            if not isinstance(ident,str) or ident not in docs or ident in targets: raise Invalid('missing/duplicate target ID')
            if docs[ident]['status']=='needs-research': raise Invalid('unfinished target')
            targets.add(ident);plain(entry['question']);plain(entry['rationale'])

def output_path(root, output):
    root = root.resolve()
    target = output.resolve()
    protected = {root / name for name in ('README.md', 'DISCOVERY.md', 'CATALOG.md')}
    if target in protected:
        raise Invalid('protected reader entry; output must be a management draft')
    draft = root / '管理档案' / '草稿'
    # Resolve the destination, but not the allowed boundary: a symlink cannot
    # redirect the draft directory outside the literal management subtree.
    if not target.is_relative_to(draft) or target.suffix != '.md':
        raise Invalid('output must be a .md file under 管理档案/草稿')
    return target

def render(root,registry,output=None,source_dirs=None,reader_manifest=None,expected_count=None,input_paths=()):
    root = root.resolve()
    output = output_path(root, output or root/'管理档案'/'草稿'/'旧路线候选.md')
    if (source_dirs is not None) == (reader_manifest is not None):
        raise Invalid('choose exactly one legacy source set or reader manifest')
    if reader_manifest is None:
        if expected_count is not None: raise Invalid('expected-count applies only to reader mode')
        for _, source in source_folders(root, source_dirs):
            if output.is_relative_to(source):
                raise Invalid('output overlaps declared source directory')
        docs = documents(root, source_dirs)
    else:
        docs = reader_documents(root, reader_manifest, expected_count)
        protect_inputs(output, [root/reader_manifest])
    protect_inputs(output, list(input_paths) + [root/d['path'] for d in docs.values()])
    def relative(path):
        return quote(Path(os.path.relpath(root/path, output.parent)).as_posix(), safe='/')
    validate(registry,docs)
    def link(ident):
        d=docs[ident]
        if reader_manifest is not None:
            return f'[{plain(d["title"])}]({relative(d["path"])}) — `{d["id"]}`'
        return f'[{plain(d["title"])}]({relative(d["path"])}) — `{d["id"]}` · `{d["status"]}` · `{d["primary_discipline"]}`'
    lines=['# 旧路线维护候选（非读者目录）','',f'本文件仅预览旧元数据中的路线关系，不是当前书目或编辑验收结果。读者请使用 [中文书库]({relative("GameLibrary/README.md")})；规范书目由维护者保留在管理档案中，本工具不读写或重新生成它。链接按本草稿所在位置解析。','']
    if reader_manifest is not None:
        lines = ['# 稳定ID路线维护候选（非读者目录）', '',
                 f'依据显式图书清单解析既有路线ID；不推断正文的学科、证据等级或发表状态，不新增读者导览。读者请使用 [中文书库]({relative("GameLibrary/README.md")})。', '']
    for route in registry['routes']:
        lines += [f'## {plain(route["title"])}',f'路线 ID：`{route["id"]}`','']
        if route['kind']=='role': lines += ['岗位起点：'+link(route['subject_profile_id']),'']
        else: lines += ['问题入口，不代表新增岗位档案。相似的状态边界不意味着可直接共享算法；分别阅读各文适用条件。','']
        for entry in route['entries']:
            lines += ['- '+plain(entry['question'])+' → '+link(entry['document_id']), '  - 关联理由：'+plain(entry['rationale'])]
        lines+=['']
    return '\n'.join(lines)+'\n'

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('root',type=Path);p.add_argument('--registry',type=Path,required=True)
    mode=p.add_mutually_exclusive_group(required=True)
    mode.add_argument('--source-dir',action='append',help='Repeatable explicit legacy input directory')
    mode.add_argument('--reader-manifest',help='Explicit root-relative reader manifest; no YAML scanning')
    p.add_argument('--expected-count',type=int,help='Required positive exact count in reader mode')
    p.add_argument('--output',type=Path,required=True);p.add_argument('--check',action='store_true')
    args=p.parse_args()
    try:
        args.output=output_path(args.root,args.output) # reject protected targets even in --check mode
        content=render(args.root,registry_load(args.registry),args.output,args.source_dir,
                       args.reader_manifest,args.expected_count,input_paths=[args.registry]) # validate before write
        if args.check:
            if not args.output.is_file() or args.output.read_text(encoding='utf-8')!=content:
                print('navigation differs or is missing',file=sys.stderr);return 1
            print('navigation matches');return 0
        temporary=None
        try:
            with tempfile.NamedTemporaryFile(mode='w',encoding='utf-8',dir=args.output.parent,delete=False) as handle:
                temporary=Path(handle.name)
                handle.write(content)
            os.replace(temporary,args.output)
        finally:
            if temporary is not None and temporary.exists(): temporary.unlink()
        return 0
    except (ValueError,KeyError,TypeError,OSError) as exc:
        print('navigation error: '+str(exc),file=sys.stderr);return 2
if __name__=='__main__': raise SystemExit(main())
