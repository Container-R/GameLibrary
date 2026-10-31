"""Repository taxonomy compatibility checks, not proof of industry completeness."""
import json
import re
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
LEGACY_IDS = set('PROG NET ENGINE TA ART2D MODEL ANIM VFX GFX SFX MUSIC DESIGN NARR UX QA DATA LIVE PROD PLATFORM BIZ AI ACCESS'.split())


def validate(data):
    nodes = data['disciplines']
    ids = [node['id'] for node in nodes]
    if len(ids) != len(set(ids)):
        raise ValueError('duplicate discipline ID')
    if not LEGACY_IDS <= set(ids):
        raise ValueError('legacy discipline ID removed')
    by_id = {node['id']: node for node in nodes}
    for node in nodes:
        targets = node.get('split_into', [])
        if targets and (len(targets) < 2 or len(set(targets)) != len(targets)):
            raise ValueError('split must identify multiple distinct targets')
        if targets and node.get('alias_of'):
            raise ValueError('split is not a single-target alias')
        if any(target not in by_id for target in targets):
            raise ValueError('missing split target')
    def walk(key, ancestors):
        if key in ancestors:
            raise ValueError('cyclic split')
        for target in by_id[key].get('split_into', []):
            walk(target, ancestors | {key})
    for key in by_id:
        walk(key, set())
    return by_id


class TaxonomyTests(unittest.TestCase):
    def setUp(self):
        self.data = json.loads((ROOT / 'taxonomy/disciplines.json').read_text())
    def test_current_compatibility(self):
        nodes = validate(self.data)
        self.assertEqual(nodes['ACCESS']['name_en'], 'Accessibility and localization')
        self.assertEqual(nodes['ACCESS']['split_into'], ['A11Y', 'LOC'])
        self.assertEqual(nodes['ACCESS']['state'], 'legacy-umbrella')
    def test_document_discipline_references(self):
        ids = set(validate(self.data))
        # Repository convention: single primary and inline related ID list.
        for folder in ('roles', 'knowledge', 'solutions', 'case-studies', 'comparisons'):
            for path in (ROOT / folder).rglob('*.md'):
                with self.subTest(path=str(path.relative_to(ROOT))):
                    text = path.read_text()
                    match = re.match(r'^---\n(.*?)\n---\n', text, re.S)
                    self.assertIsNotNone(match)
                    front = match.group(1)
                    primary = re.search(r'^primary_discipline: ([A-Z0-9]+)$', front, re.M)
                    self.assertIsNotNone(primary)
                    self.assertIn(primary.group(1), ids)
                    related = re.search(r'^related_disciplines: \[(.*?)\]$', front, re.M)
                    if related:
                        for key in related.group(1).split(','):
                            self.assertIn(key.strip(), ids)

    def test_removed_legacy_rejected(self):
        self.data['disciplines'] = [n for n in self.data['disciplines'] if n['id'] != 'ACCESS']
        with self.assertRaises(ValueError): validate(self.data)
    def test_missing_target_rejected(self):
        self.data['disciplines'] = [n for n in self.data['disciplines'] if n['id'] != 'LOC']
        with self.assertRaises(ValueError): validate(self.data)
    def test_duplicate_id_rejected(self):
        self.data['disciplines'].append(self.data['disciplines'][0].copy())
        with self.assertRaises(ValueError): validate(self.data)
    def test_cycle_rejected(self):
        self.data['disciplines'][-1]['split_into'] = ['ACCESS', 'UX']
        with self.assertRaises(ValueError): validate(self.data)
    def test_single_alias_rejected(self):
        node = next(n for n in self.data['disciplines'] if n['id'] == 'ACCESS')
        node['alias_of'] = 'A11Y'
        with self.assertRaises(ValueError): validate(self.data)


if __name__ == '__main__': unittest.main(verbosity=2)
