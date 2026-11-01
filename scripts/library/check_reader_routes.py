"""Check inventory shelf links, not prose quality or human retrieval success."""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import unquote


def check(root):
    root = root.resolve()
    manifest = json.loads((root / '管理档案/图书目录.json').read_text())
    errors = []
    for item in manifest['entries']:
        shelf = root / 'GameLibrary' / item['floor'] / item['area'] / item['shelf'] / 'README.md'
        target = (root / item['current_read_path']).resolve()
        if not shelf.is_file() or not target.is_file():
            errors.append(f"Missing shelf or article: {item['internal_id']}")
            continue
        targets = [(shelf.parent / unquote(u.split('#')[0])).resolve()
                   for u in re.findall(r'\]\(([^)]+)\)', shelf.read_text())
                   if not u.startswith(('http:', 'https:', '#'))]
        if target not in targets:
            errors.append(f"Inventory entry absent from shelf: {item['internal_id']}")
        canonical = item.get('canonical_reader_path')
        if canonical:
            book = root / canonical
            if not book.is_file() or book.read_text().splitlines()[0] != '# ' + item['reader_title']:
                errors.append(f"Canonical article title mismatch: {item['internal_id']}")
    return {'inventory_entries_checked': len(manifest['entries']), 'errors': errors,
            'scope': 'Shelf coverage and canonical titles only; not editorial acceptance'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('root', type=Path)
    result = check(parser.parse_args().root)
    print(json.dumps(result, ensure_ascii=False))
    raise SystemExit(bool(result['errors']))
