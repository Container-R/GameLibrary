"""Check a declared reader manifest's simple Markdown outlinks, offline.

Not a Markdown renderer, external-source check, or reader-quality certification.
Unsupported link/heading syntax is reported, never interpreted as checked.
"""
import argparse
import json
from pathlib import Path
import re
import unicodedata
from urllib.parse import unquote, urlsplit


def strict_json(text):
    def pairs(items):
        obj = {}
        for k, v in items:
            if k in obj:
                raise ValueError('duplicate JSON key')
            obj[k] = v
        return obj
    def constant(_):
        raise ValueError('nonfinite JSON')
    return json.loads(text, object_pairs_hook=pairs, parse_constant=constant)


def decode(value):
    if re.search(r'%(?![0-9a-fA-F]{2})', value):
        raise ValueError('invalid URL encoding')
    value = unquote(value, errors='strict')
    if any(ord(c) < 32 for c in value) or '\\' in value:
        raise ValueError('invalid local link')
    return value


def within(root, base, value):
    if not value or value.startswith('/') or ':' in value or '\\' in value:
        raise ValueError('invalid relative path')
    result = (base / value).resolve()
    if not result.is_relative_to(root):
        raise ValueError('path escapes root')
    if not result.is_file():
        raise ValueError('missing target')
    return result


def prose(text):
    """Remove supported fenced and inline code; retain ambiguous indentation. Preserve line numbers."""
    lines = []
    fence = None
    previous = ''
    for line in text.splitlines():
        old_previous = previous
        previous = line
        m = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if fence:
            if re.match(r'^ {0,3}' + re.escape(fence[0]) + '{' + str(fence[1]) + r',}\s*$', line):
                fence = None
            lines.append('')
        elif m and m[1][0] == '`' and '`' in line[m.end():]:
            lines.append(line)  # Invalid opener: must not swallow following prose.
        elif m:
            fence = (m[1][0], len(m[1]))
            lines.append('')
        elif line.startswith(('    ', '\t')):
            # Ambiguous with paragraph/list continuation: retain and report below.
            lines.append(line)
        else:
            # Inline code with matching backtick run (no multiline inline code).
            lines.append(re.sub(r'(`+)(?!`)(.*?)\1(?!`)', '', line))
    return lines


def headings(text):
    """GitHub-like slugs for plain-text ATX headings only, with duplicates."""
    slugs = set()
    counts = {}
    unsupported = False
    # Keep inline code visible here so formatted headings aren't mis-certified.
    fence = None
    previous = ''
    for line in text.splitlines():
        old_previous = previous
        previous = line
        m = re.match(r'^ {0,3}(`{3,}|~{3,})', line)
        if fence:
            if re.match(r'^ {0,3}' + re.escape(fence[0]) + '{' + str(fence[1]) + r',}\s*$', line):
                fence = None
            continue
        if m and m[1][0] == '`' and '`' in line[m.end():]:
            unsupported = True
            continue
        if m:
            fence = (m[1][0], len(m[1]))
            continue
        # Do not certify headings through possible raw HTML block context.
        # Deliberately conservative: any literal '<' outside a supported fence
        # makes this whole target unsupported, even if it might be inline text.
        if '<' in line:
            unsupported = True
            continue
        m = re.match(r'^ {0,3}#{1,6}\s+(.+?)\s*$', line)
        if not m:
            if re.match(r'^ {0,3}(?:=+|-+)\s*$', line) and old_previous.strip() and not old_previous.lstrip().startswith('#'):
                unsupported = True  # Setext or thematic break: can't infer a title.
            continue
        title = re.sub(r'\s+#+\s*$', '', m[1])
        if any(c in title for c in '`*[]<>\\&'):
            unsupported = True
            continue
        slug = ''.join(c for c in title.lower() if c in '-_ ' or unicodedata.category(c)[0] in 'LN').replace(' ', '-')
        # Include generated slugs when avoiding collisions (e.g. Foo, Foo, Foo-1).
        base = slug
        n = counts.get(base, 0)
        while slug in slugs:
            n += 1
            slug = base + '-' + str(n)
        counts[base] = n
        slugs.add(slug)
    return slugs, unsupported


def links(text):
    found, errors = [], []
    lines = prose(text)
    # Unmatched/multiline inline code makes subsequent link interpretation ambiguous.
    # Do not turn code contents into a claimed broken link. Reject this document's
    # parsing scope instead of trying to implement multiline inline-code parsing.
    for number, line in enumerate(lines, 1):
        if '`' in line and not re.match(r'^ {0,3}`{3,}', line):
            return [], [(number, 'unsupported unmatched or multiline inline code')]
    for number, line in enumerate(lines, 1):
        opener = re.match(r'^ {0,3}(`{3,})(.*)$', line)
        if opener and '`' in opener[2]:
            errors.append((number, 'unsupported invalid code fence opener'))
        html_candidate = re.sub(r'<https?://[^<>\s]+>', '', line)
        if re.search(r'</?[A-Za-z!][^>]*$', html_candidate):
            errors.append((number, 'unsupported multiline HTML syntax'))
        # Bare [1][2] citations are prose; actual reference definitions still fail.
        line = re.sub(r'\[\d+\](?![(:])', '', line)
        if line.startswith(('    ', '\t')) and any(c in line for c in '[<'):
            errors.append((number, 'unsupported ambiguous indented link syntax'))
            continue
        if re.search(r'<(?!https?://)[^>]+>|\]\[|^ {0,3}\[[^]]+\]:|\\[\[\]]', line, re.I):
            errors.append((number, 'unsupported Markdown/HTML link syntax'))
        # Only ordinary one-line inline [text](destination) or image syntax.
        for m in re.finditer(r'\[[^\[\]\n]*\]\(', line):
            tail = line[m.end():]
            end = tail.find(')')
            if end < 0:
                errors.append((number, 'unterminated inline link'))
                continue
            target = tail[:end]
            if '(' in target or any(c.isspace() for c in target) or not target or target.startswith('<') or re.search(r'&(?:#\d+|#x[0-9a-fA-F]+|[A-Za-z][A-Za-z0-9]+);', target):
                errors.append((number, 'unsupported inline destination'))
            else:
                found.append((number, target))
        # Reference-style shortcut labels are ambiguous with prose; explicit report.
        residual = re.sub(r'!?\[[^\[\]\n]*\]\([^\n)]*\)', '', line)
        # Bare numeric citations are ordinary prose in this library, not links.
        residual = re.sub(r'\[\d+\]', '', residual)
        if '[' in residual or '](' in residual:
            errors.append((number, 'unsupported bracket/reference syntax'))
        for m in re.finditer(r'<(https?://[^<>\s]+)>', line):
            found.append((number, m[1]))
    return found, errors


def check(root, manifest_path, expected_count):
    root = Path(root).resolve()
    if not root.is_dir() or type(expected_count) is not int or expected_count <= 0:
        raise ValueError('existing root and positive expected count required')
    manifest_path = within(root, root, manifest_path)
    manifest = strict_json(manifest_path.read_text(encoding='utf-8'))
    if not isinstance(manifest, dict) or not isinstance(manifest.get('entries'), list):
        raise ValueError('manifest object with entries required')
    entries = manifest['entries']
    if len(entries) != expected_count:
        raise ValueError('manifest count mismatch')
    readers = []
    for entry in entries:
        if not isinstance(entry, dict) or not isinstance(entry.get('current_read_path'), str):
            raise ValueError('current_read_path required')
        p = within(root, root, entry['current_read_path'])
        if p.suffix.lower() != '.md' or p in readers:
            raise ValueError('unique Markdown reader paths required')
        if not p.read_text(encoding='utf-8').strip():
            raise ValueError('empty reader Markdown')
        readers.append(p)
    errors = []
    local_count = external_count = fragment_count = 0
    for p in readers:
        found, syntax_errors = links(p.read_text(encoding='utf-8'))
        rel = p.relative_to(root).as_posix()
        errors.extend({'reader': rel, 'line': n, 'reason': reason} for n, reason in syntax_errors)
        for n, value in found:
            try:
                url = urlsplit(value)
                if url.scheme.lower() in ('http', 'https'):
                    external_count += 1
                    continue
                if url.scheme or url.netloc or url.query:
                    raise ValueError('forbidden scheme, authority, or query')
                path = decode(url.path)
                target = within(root, p.parent, path) if path else p
                local_count += 1
                if '#' in value:
                    fragment_count += 1
                    fragment = decode(url.fragment)
                    if not fragment or target.suffix.lower() != '.md':
                        raise ValueError('unsupported empty or non-Markdown fragment')
                    slugs, partial = headings(target.read_text(encoding='utf-8'))
                    if partial:
                        raise ValueError('unsupported target heading syntax')
                    if fragment not in slugs:
                        raise ValueError('missing heading fragment')
            except (ValueError, OSError, UnicodeError) as exc:
                # Only our fixed messages, never OS paths or URL values.
                allowed = {'unsupported target heading syntax', 'missing heading fragment', 'missing target', 'path escapes root', 'forbidden scheme, authority, or query', 'unsupported empty or non-Markdown fragment', 'invalid relative path', 'invalid URL encoding', 'invalid local link'}
                reason = str(exc) if type(exc) is ValueError and str(exc) in allowed else 'invalid local target'
                errors.append({'reader': rel, 'line': n, 'reason': reason})
    unsupported = [e for e in errors if 'unsupported' in e['reason']]
    fragment_errors = [e for e in errors if e['reason'] == 'missing heading fragment']
    target_errors = [e for e in errors if e not in unsupported and e not in fragment_errors]
    status = 'fail' if target_errors or fragment_errors else ('incomplete' if unsupported else 'pass')
    return {'status': status, 'target_errors': target_errors, 'fragment_errors': fragment_errors, 'unsupported': unsupported, 'readers_checked': len(readers),
            'local_links_checked': local_count, 'fragments_checked': fragment_count,
            'external_links_not_checked': external_count, 'errors': errors,
            'scope': 'Offline simple inline Markdown targets and plain ATX heading fragments only; not rendered Markdown, source truth, or reader quality'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True, type=Path)
    parser.add_argument('--manifest', required=True, help='Root-relative manifest file, never absolute')
    parser.add_argument('--expected-count', required=True, type=int)
    a = parser.parse_args()
    try:
        result = check(a.root, a.manifest, a.expected_count)
    except (ValueError, OSError, UnicodeError, TypeError):
        print(json.dumps({'status': 'configuration_error'}))
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if result['errors'] else 0


if __name__ == '__main__':
    raise SystemExit(main())
