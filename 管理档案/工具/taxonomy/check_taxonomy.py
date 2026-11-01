"""Explicit, read-only taxonomy and declared document checks; not editorial QA."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re

LEGACY_IDS = set('PROG NET ENGINE TA ART2D MODEL ANIM VFX GFX SFX MUSIC DESIGN NARR UX QA DATA LIVE PROD PLATFORM BIZ AI ACCESS'.split())
FOLDERS = ('roles', 'knowledge', 'solutions', 'case-studies', 'comparisons')


def require(ok, message):
    if not ok:
        raise ValueError(message)


def read_json(path):
    def pairs(items):
        result = {}
        for key, value in items:
            require(key not in result, 'duplicate JSON key')
            result[key] = value
        return result
    return json.loads(path.read_text(encoding='utf-8'), object_pairs_hook=pairs)


def validate(data):
    require(isinstance(data, dict) and isinstance(data.get('disciplines'), list), 'disciplines must be a list')
    nodes = data['disciplines']
    require(all(isinstance(n, dict) and isinstance(n.get('id'), str) and re.fullmatch('[A-Z][A-Z0-9]*', n['id']) for n in nodes), 'invalid discipline')
    ids = [n['id'] for n in nodes]
    require(len(ids) == len(set(ids)), 'duplicate discipline ID')
    require(LEGACY_IDS <= set(ids), 'legacy discipline ID removed')
    by_id = {n['id']: n for n in nodes}
    for node in nodes:
        targets = node.get('split_into', [])
        require(isinstance(targets, list) and all(isinstance(t, str) for t in targets), 'invalid split list')
        if targets:
            require(len(targets) >= 2 and len(set(targets)) == len(targets), 'split must identify multiple distinct targets')
            require(not node.get('alias_of'), 'split is not a single-target alias')
        require(all(t in by_id for t in targets), 'missing split target')
    done = set()
    def walk(key, ancestors):
        require(key not in ancestors, 'cyclic split')
        if key in done:
            return
        for target in by_id[key].get('split_into', []):
            walk(target, ancestors | {key})
        done.add(key)
    for key in by_id:
        walk(key, set())
    access = by_id['ACCESS']
    require(access.get('name_en') == 'Accessibility and localization' and access.get('split_into') == ['A11Y', 'LOC'] and access.get('state') == 'legacy-umbrella', 'ACCESS compatibility changed')
    return by_id


def within(root, name):
    require(isinstance(name, str) and name and not re.search(r'[\\\x00-\x1f\x7f]', name), 'invalid relative path')
    require(not PurePosixPath(name).is_absolute() and not re.match(r'^[A-Za-z]:', name) and all(p not in ('', '.', '..') for p in name.split('/')), 'non-normalized path')
    path = (root / name).resolve()
    require(path.is_relative_to(root), 'path escapes root')
    return path


def stable_id(value):
    require(isinstance(value, str) and re.fullmatch(r'[A-Z0-9]+(?:-[A-Z0-9]+)+', value), 'invalid stable document ID')
    return value


def check(root, taxonomy, mode, expected_count, manifest=None):
    root = Path(root).resolve(strict=True)
    require(root.is_dir(), 'root must be a directory')
    require(type(expected_count) is int and expected_count > 0, 'expected-count must be positive')
    disciplines = validate(read_json(within(root, taxonomy)))
    records = []
    if mode == 'reader':
        require(manifest is not None, 'reader mode requires manifest')
        data = read_json(within(root, manifest))
        require(isinstance(data, dict) and isinstance(data.get('entries'), list) and data['entries'], 'nonempty manifest entries required')
        for item in data['entries']:
            require(isinstance(item, dict), 'invalid manifest entry')
            ident = stable_id(item.get('internal_id'))
            path_name = item.get('canonical_reader_path')
            require(isinstance(path_name, str) and path_name.startswith('GameLibrary/') and path_name.endswith('.md'), 'canonical reader path required')
            require(item.get('current_read_path') == path_name, 'current/canonical reader path mismatch')
            path = within(root, path_name)
            title = item.get('reader_title')
            require(isinstance(title, str) and title.strip() and '\n' not in title and '\r' not in title, 'invalid reader title')
            lines = path.read_text(encoding='utf-8').splitlines()
            require(lines and lines[0] == '# ' + title, 'reader H1 mismatch: ' + ident)
            records.append((ident, path_name, path))
    elif mode == 'legacy':
        require(manifest is None, 'legacy mode does not consume reader manifest')
        for folder in FOLDERS:
            directory = within(root, folder)
            require(directory.is_dir(), 'expected legacy directory missing: ' + folder)
            for candidate in sorted(directory.rglob('*.md')):
                name = candidate.relative_to(root).as_posix()
                path = within(root, name)
                text = path.read_text(encoding='utf-8')
                match = re.match(r'^---\n(.*?)\n---(?:\n|$)', text, re.S)
                require(match is not None, 'legacy frontmatter missing: ' + name)
                front = match[1]
                def field(key):
                    values = re.findall(r'^' + key + r':\s*([^\n]+)$', front, re.M)
                    require(len(values) == 1, 'missing/duplicate field: ' + key)
                    return values[0].strip()
                ident = stable_id(field('id'))
                require(field('primary_discipline') in disciplines, 'unknown primary discipline')
                related = re.findall(r'^related_disciplines:\s*\[(.*?)\]\s*$', front, re.M)
                require(len(related) <= 1, 'duplicate related discipline list')
                if related:
                    require(all(k.strip() in disciplines for k in related[0].split(',') if k.strip()), 'unknown related discipline')
                records.append((ident, name, path))
    else:
        raise ValueError('unknown mode')
    require(len(records) == expected_count, 'document count mismatch: expected %s, found %s' % (expected_count, len(records)))
    require(len({r[0] for r in records}) == len(records), 'duplicate document ID')
    require(len({r[2] for r in records}) == len(records), 'duplicate resolved document path')
    return {'status': 'PASS', 'mode': mode, 'documents_checked': len(records), 'discipline_nodes_checked': len(disciplines), 'document_ids': sorted(r[0] for r in records), 'scope': 'Declared nonempty set only; reader mode checks IDs/paths/H1, not per-document disciplines, prose quality, supports, runtime or publication.'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--taxonomy', required=True, help='normalized path relative to root')
    parser.add_argument('--mode', required=True, choices=['legacy', 'reader'])
    parser.add_argument('--expected-count', required=True, type=int)
    parser.add_argument('--manifest', help='normalized path relative to root; required for reader mode')
    args = parser.parse_args()
    try:
        result = check(args.root, args.taxonomy, args.mode, args.expected_count, args.manifest)
    except (ValueError, OSError, RecursionError) as exc:
        print(json.dumps({'status': 'FAIL', 'error': str(exc)}, ensure_ascii=False))
        return 1
    print(json.dumps(result, ensure_ascii=False))
    return 0

if __name__ == '__main__':
    raise SystemExit(main())
