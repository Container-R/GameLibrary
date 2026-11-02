"""Check current reader path inventory and redundant counts; not content quality."""
import argparse
import json
import math
import os
from pathlib import Path, PurePosixPath


def strict_json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError('duplicate JSON key')
            result[key] = value
        return result
    def constant(_):
        raise ValueError('nonfinite JSON number')
    def number(value):
        result = float(value)
        if not math.isfinite(result):
            raise ValueError('nonfinite JSON number')
        return result
    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant,
                      parse_float=number)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def count_field(obj, key, expected):
    require(type(obj) is dict, 'missing count section')
    value = obj.get(key)
    require(type(value) is int and value == expected, 'count mismatch: ' + key)


def read_json(root, relative):
    path = root / relative
    current = root
    for part in relative.split('/'):
        current = current / part
        require(not current.is_symlink(), 'metadata symlink unsupported')
    return strict_json(path.read_text(encoding='utf-8'))


def check(root, frozen_count):
    require(type(frozen_count) is int and frozen_count > 0,
            'explicit positive frozen count required')
    root = Path(root).resolve(strict=True)
    require(root.is_dir(), 'missing root')
    catalog = read_json(root, '管理档案/图书目录.json')
    state = read_json(root, '.agent/state.json')
    require(type(catalog) is dict and type(state) is dict, 'metadata must be objects')
    entries = catalog.get('entries')
    require(type(entries) is list and len(entries) > 0, 'nonempty entries required')
    paths = set()
    for entry in entries:
        require(type(entry) is dict, 'entry must be object')
        value = entry.get('canonical_reader_path')
        require(type(value) is str and bool(value), 'canonical path required')
        require('\\' not in value and ':' not in value and not any(ord(c) < 32 for c in value),
                'invalid canonical path')
        parts = value.split('/')
        require(not PurePosixPath(value).is_absolute() and
                all(p not in ('', '.', '..') for p in parts), 'unnormalized canonical path')
        require(parts[0] == 'GameLibrary' and len(parts) > 1 and
                parts[-1].endswith('.md') and parts[-1] != 'README.md',
                'canonical must name reader body')
        require(value not in paths, 'duplicate canonical path')
        paths.add(value)
    library = root / 'GameLibrary'
    require(library.is_dir() and not library.is_symlink(), 'missing or linked library')
    actual = set()
    def walk_error(error):
        raise error
    for directory, dirs, files in os.walk(library, followlinks=False, onerror=walk_error):
        for name in dirs + files:
            require(not (Path(directory) / name).is_symlink(), 'library symlink unsupported')
        for name in files:
            if name.endswith('.md') and name != 'README.md':
                target = Path(directory) / name
                require(target.is_file(), 'reader is not regular file')
                actual.add(target.relative_to(root).as_posix())
    require(bool(actual), 'empty reader library')
    require(paths == actual, 'canonical and actual reader path sets differ')
    total = len(actual)
    require(total >= frozen_count, 'total below explicit frozen count')
    post = total - frozen_count
    for section in (catalog, state.get('reader_baseline')):
        count_field(section, 'reader_books_total', total)
        count_field(section, 'rewritten_reader_books', frozen_count)
        count_field(section, 'accounted_for_original_items', frozen_count)
    count_field(catalog, 'post_baseline_research_books', post)
    count_field(state.get('publication'), 'reader_books_total', total)
    count_field(state.get('publication'), 'post_baseline_research_books', post)
    return {'status': 'pass', 'canonical_paths': total, 'actual_reader_bodies': total,
            'frozen_count': frozen_count, 'post_baseline_research_books': post,
            'scope': 'Current path-set and count consistency only; not editorial, source, navigation or historical approval'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, required=True)
    parser.add_argument('--frozen-count', type=int, required=True)
    args = parser.parse_args()
    try:
        result = check(args.root, args.frozen_count)
    except (OSError, ValueError, TypeError, KeyError):
        print(json.dumps({'status': 'fail', 'scope': 'Current reader inventory/count consistency'}))
        return 1
    print(json.dumps(result))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
