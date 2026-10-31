import copy
from pathlib import Path
import tempfile
import unittest
from validate_queue import Invalid, validate


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root/'article.md').write_text('original test fixture')
        self.tax = {'disciplines': [{'id': 'GFX'}, {'id': 'PROG'}]}
        self.queue = {'tasks': [{'id': 'T1', 'discipline': 'GFX', 'status': 'published', 'expected_artifact': 'Legacy free prose'}]}
    def test_legacy_optional_and_unknown_status(self):
        self.assertEqual(validate(self.tax,self.queue,self.root), {'tasks_checked':1,'artifact_paths_checked':0})
        self.queue['tasks'][0].update(status='future-project-state', artifact_paths=['future.md'])
        validate(self.tax,self.queue,self.root)
    def test_unknown_discipline(self):
        self.queue['tasks'][0]['discipline']='RENDER'
        with self.assertRaises(Invalid): validate(self.tax,self.queue,self.root)
    def test_duplicate_task(self):
        self.queue['tasks'].append(copy.deepcopy(self.queue['tasks'][0]))
        with self.assertRaises(Invalid): validate(self.tax,self.queue,self.root)
    def test_path_spellings(self):
        for path in ('../outside','/tmp/out','C:/out','a/../b','a//b','./article.md','a\\b','article.md/'):
            with self.subTest(path=path):
                self.queue['tasks'][0]['artifact_paths']=[path]
                with self.assertRaises(Invalid): validate(self.tax,self.queue,self.root)
    def test_published_missing(self):
        self.queue['tasks'][0]['artifact_paths']=['missing.md']
        with self.assertRaises(Invalid): validate(self.tax,self.queue,self.root)
    def test_planned_missing_allowed(self):
        self.queue['tasks'][0].update(status='needs-research',artifact_paths=['future/new.md'])
        self.assertEqual(validate(self.tax,self.queue,self.root)['artifact_paths_checked'],1)
    def test_existing_published_path(self):
        self.queue['tasks'][0]['artifact_paths']=['article.md']
        validate(self.tax,self.queue,self.root)
    def test_symlink_escape(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root/'escape').symlink_to(outside, target_is_directory=True)
            self.queue['tasks'][0].update(status='planned',artifact_paths=['escape/not-created'])
            with self.assertRaises(Invalid): validate(self.tax,self.queue,self.root)
    def test_bad_shapes(self):
        for value in (None,'article.md',[1],['article.md','article.md']):
            self.queue['tasks'][0]['artifact_paths']=value
            with self.subTest(value=value), self.assertRaises(Invalid): validate(self.tax,self.queue,self.root)


if __name__=='__main__': unittest.main(verbosity=2)
