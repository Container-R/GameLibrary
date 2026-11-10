import copy
import json
from pathlib import Path
import unittest
from analyze import analyze

ROOT=Path(__file__).resolve().parent

def read(case):return json.loads((ROOT/'inputs'/('case-'+case+'.json')).read_text())

class ReconciliationTests(unittest.TestCase):
    def test_three_mechanisms(self):
        a,b,c=(analyze(read(k)) for k in ('01','02','03'))
        self.assertEqual(a['groups']['T']['target_N'],4)
        self.assertEqual(a['anchor_not_received_at_snapshot'],[])
        self.assertEqual(b['groups']['T']['target_N'],6)
        self.assertEqual(b['anchor_not_received_at_snapshot'],['T1-2'])
        self.assertEqual(b['parsed_sequence_gaps']['T1/install1'],[2])
        self.assertEqual(c['members_excluded'],['T2'])
        self.assertEqual(c['groups']['T']['assigned'],2)
        self.assertEqual(c['parsed_not_final'],['T2-1','T2-2','T2-3'])
    def test_late_vs_lost_not_identifiable_yet(self):
        a,b=read('02'),read('04')
        a.pop('observation_stream_id');b.pop('observation_stream_id')
        self.assertEqual(a,b)
        self.assertEqual(analyze(read('02')),analyze(read('04')))
        self.assertEqual(analyze(read('05'))['anchor_not_received_at_snapshot'],[])
    def test_duplicate_and_bad_label(self):
        d=analyze(read('06')); e=analyze(read('07'))
        self.assertEqual(d['duplicate_copies_removed'],['T2-3'])
        self.assertEqual(d['groups']['T']['final_observed'],6)
        self.assertEqual(e['received_not_parsed'],[{'id':'T2-3','reason':'assignment_label_conflict'}])
        self.assertEqual(e['groups']['T']['target_N'],6)
        self.assertEqual(e['groups']['C']['final_observed'],6)
    def test_whole_sequence_loss(self):
        d=analyze(read('08'))
        self.assertEqual(d['anchor_not_received_at_snapshot'],['T2-1','T2-2','T2-3'])
        self.assertNotIn('T2/install1',d['parsed_sequence_gaps'])
        self.assertEqual(d['groups']['T']['target_N'],6)
    def test_identical_worlds_unknown_not_zero(self):
        worlds=json.loads((ROOT/'oracle'/'hidden-worlds.json').read_text())
        for a,b in [('09','10'),('11','12')]:
            self.assertNotEqual(worlds[a],worlds[b])
            self.assertEqual(read(a),read(b))
            self.assertEqual(analyze(read(a)),analyze(read(b)))
            self.assertIsNone(analyze(read(a))['groups']['T']['target_N'])
            self.assertTrue(all(p['target_status']=='unknown' for p in analyze(read(a))['players']))
    def test_actual_hidden_world_projection(self):
        from make_fixtures import project_click_world
        worlds=json.loads((ROOT/'oracle'/'click-worlds.json').read_text())
        self.assertNotEqual(worlds['09']['clicks'],worlds['10']['clicks'])
        self.assertEqual(len(worlds['09']['clicks']),12)
        self.assertEqual(len(worlds['10']['clicks']),15)
        for k in ('09','10'):
            self.assertEqual(project_click_world(worlds[k]),read(k))
        self.assertEqual(project_click_world(worlds['09']),project_click_world(worlds['10']))
    def test_future_leak_rejected(self):
        d=read('05');d['contract']['snapshot']=100
        with self.assertRaises(ValueError):analyze(d)
    def test_conflicting_duplicate_rejected(self):
        d=read('06');d['received'][-1]['seq']=999
        with self.assertRaises(ValueError):analyze(d)
    def test_conflicting_payload_quarantined(self):
        d=read('06');d['received'][-1]['start_at']=44
        with self.assertRaises(ValueError):analyze(d)
    def test_mixed_label_duplicate_fails_closed(self):
        d=read('06');d['received'][-1]['arm']='C'
        with self.assertRaises(ValueError):analyze(d)
    def test_sequence_collision(self):
        d=read('01');d['received'][1]['seq']=1
        with self.assertRaises(ValueError):analyze(d)
    def test_snapshot_series_and_parsed_gap_stage(self):
        self.assertEqual(read('04')['observation_stream_id'],read('05')['observation_stream_id'])
        self.assertLess(read('04')['contract']['snapshot'],read('05')['contract']['snapshot'])
        d=read('01')
        next(r for r in d['received'] if r['id']=='C1-2')['arm']='T'
        a=analyze(d)
        self.assertEqual(a['parsed_sequence_gaps']['C1/install1'],[2])
        self.assertEqual(a['anchor_not_received_at_snapshot'],[])
        self.assertEqual(a['received_not_parsed'],[{'id':'C1-2','reason':'assignment_label_conflict'}])
    def test_window_violation_rejected(self):
        d=read('01');d['accepted'][0]['start_at']=60
        with self.assertRaises(ValueError):analyze(d)
    def test_nondefault_complete_zero(self):
        d=read('01');d['accepted']=[r for r in d['accepted'] if r['player']!='T2'];d['received']=[r for r in d['received'] if r['player']!='T2']
        p=next(p for p in analyze(d)['players'] if p['player']=='T2')
        self.assertEqual(p['target_N'],0); self.assertEqual(p['target_status'],'known')

if __name__=='__main__':unittest.main(verbosity=2)
