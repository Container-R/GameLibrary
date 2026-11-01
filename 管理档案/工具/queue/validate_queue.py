"""Additive read-only queue checks. Legacy expected_artifact remains unrestricted."""
import argparse
import json
from pathlib import Path, PurePosixPath
import re
import sys


class Invalid(ValueError):
    pass


def validate(taxonomy, queue, root):
    root = Path(root).resolve(strict=True)
    if not root.is_dir():
        raise Invalid('repository root must be a directory')
    if not isinstance(taxonomy, dict) or not isinstance(taxonomy.get('disciplines'), list):
        raise Invalid('taxonomy disciplines must be an array')
    valid = set()
    for node in taxonomy['disciplines']:
        if not isinstance(node, dict) or not isinstance(node.get('id'), str) or not node['id']:
            raise Invalid('taxonomy ID must be a nonempty string')
        if node['id'] in valid:
            raise Invalid('duplicate taxonomy ID: ' + node['id'])
        valid.add(node['id'])
    if not isinstance(queue, dict) or not isinstance(queue.get('tasks'), list):
        raise Invalid('queue tasks must be an array')
    seen = set()
    paths_checked = 0
    for task in queue['tasks']:
        if not isinstance(task, dict):
            raise Invalid('task must be an object')
        tid = task.get('id')
        if not isinstance(tid, str) or not tid.strip():
            raise Invalid('task ID must be a nonempty string')
        if tid in seen:
            raise Invalid('duplicate task ID: ' + tid)
        seen.add(tid)
        discipline = task.get('discipline')
        if not isinstance(discipline, str) or discipline not in valid:
            raise Invalid(tid + ': unknown discipline: ' + repr(discipline))
        if 'artifact_paths' not in task:
            continue
        paths = task['artifact_paths']
        if not isinstance(paths, list):
            raise Invalid(tid + ': artifact_paths must be an array')
        path_seen = set()
        for raw in paths:
            if not isinstance(raw, str) or not raw or raw != raw.strip() or '\\' in raw or '\x00' in raw or re.search(r'[\x00-\x1f\x7f]', raw):
                raise Invalid(tid + ': invalid artifact path')
            # Use portable repository-relative POSIX spelling, not host-specific coercion.
            p = PurePosixPath(raw)
            if p.is_absolute() or re.match(r'^[A-Za-z]:', raw) or any(x in ('', '.', '..') for x in raw.split('/')):
                raise Invalid(tid + ': artifact path must be normalized repository-relative: ' + raw)
            if raw in path_seen:
                raise Invalid(tid + ': duplicate artifact path: ' + raw)
            path_seen.add(raw)
            target = (root / raw).resolve()
            if not target.is_relative_to(root):
                raise Invalid(tid + ': artifact path escapes repository: ' + raw)
            if task.get('status') == 'published' and not target.exists():
                raise Invalid(tid + ': published artifact missing: ' + raw)
            paths_checked += 1
    return {'tasks_checked': len(seen), 'artifact_paths_checked': paths_checked}


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise Invalid('duplicate JSON key: ' + key)
        result[key] = value
    return result


def read(path):
    return json.loads(Path(path).read_text(encoding='utf-8'), object_pairs_hook=pairs,
                      parse_constant=lambda s: (_ for _ in ()).throw(Invalid('nonstandard JSON constant: '+s)))


def input_path(root, raw):
    """Resolve an explicitly named repository-relative input, without fallback."""
    if (not raw or raw != raw.strip() or '\\' in raw
            or re.search(r'[\x00-\x1f\x7f]', raw)
            or PurePosixPath(raw).is_absolute()
            or re.match(r'^[A-Za-z]:', raw)
            or any(part in ('', '.', '..') for part in raw.split('/'))):
        raise Invalid('input path must be normalized repository-relative POSIX spelling')
    target = (root / raw).resolve()
    if not target.is_relative_to(root):
        raise Invalid('input path escapes repository')
    if not target.is_file():
        raise Invalid('input file missing or not a regular file: ' + raw)
    return target


def positive_count(raw):
    value = int(raw)
    if value <= 0:
        raise argparse.ArgumentTypeError('expected task count must be positive')
    return value


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, help='explicit repository root (relative to cwd or absolute)')
    parser.add_argument('--taxonomy', default='taxonomy/disciplines.json',
                        help='repository-relative taxonomy input; no fallback search')
    parser.add_argument('--queue', default='.agent/queue.json',
                        help='repository-relative queue input; no fallback search')
    parser.add_argument('--expected-task-count', type=positive_count,
                        help='optional positive migration gate; exact count, not an identity baseline')
    args = parser.parse_args()
    try:
        root = args.root.resolve(strict=True)
        if not root.is_dir():
            raise Invalid('repository root must be a directory')
        # Check both locations before reading either file. Tool location is irrelevant.
        taxonomy_path = input_path(root, args.taxonomy)
        queue_path = input_path(root, args.queue)
        result = validate(read(taxonomy_path), read(queue_path), root)
        if args.expected_task_count is not None and result['tasks_checked'] != args.expected_task_count:
            raise Invalid('task count mismatch: expected %s, found %s' %
                          (args.expected_task_count, result['tasks_checked']))
    except (ValueError, OSError, RuntimeError) as exc:
        print('queue contract error: ' + str(exc), file=sys.stderr)
        return 1
    print(json.dumps({'status': 'PASS', **result}, sort_keys=True))
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
