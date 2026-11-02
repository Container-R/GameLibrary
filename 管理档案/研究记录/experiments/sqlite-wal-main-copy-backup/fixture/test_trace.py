"""One literal trace + six rejection mutations; no SQLite or process calls."""
import copy
import importlib.util
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location('review_launcher', HERE / 'launcher.py')
launcher = importlib.util.module_from_spec(spec)
spec.loader.exec_module(launcher)
H = 'a' * 64
pairs = [
    ('begin', {'python': 'synthetic', 'sqlite': 'not-loaded'}),
    ('settings', {'journal_mode': [['wal']], 'wal_autocheckpoint': [[0]], 'isolation_level': None, 'autocommit': -1, 'busy_timeout': 0}),
    ('baseline', {'checkpoint': [[0, 0, 0]], 'rows': [], 'main_sha256': H, 'wal_bytes': 0}),
    ('committed', {'rows': [[1, 7]], 'in_transaction': False, 'main_sha256': H, 'wal_bytes': 100}),
    ('main_copy', {'path': 'plain/save.db', 'sha256': H}),
    ('plain_read', {'rows': []}),
    ('closed', {'role': 'plain'}),
    ('backup_attempt', {'pages': 1, 'name': 'main', 'sleep': 0.0}),
    ('backup_progress', {'status': 0, 'remaining': 1, 'total': 2}),
    ('backup_progress', {'status': 101, 'remaining': 0, 'total': 2}),
    ('backup_return', {'progress_calls': 2}),
    ('closed', {'role': 'backup_writer'}),
    ('backup_read', {'rows': [[1, 7]]}),
    ('closed', {'role': 'backup_reader'}),
    ('source_final', {'rows': [[1, 7]], 'main_sha256': H}),
    ('closed', {'role': 'remaining'}),
    ('success', {'plain_rows': [], 'backup_rows': [[1, 7]], 'source_rows': [[1, 7]]}),
]
base = [dict(seq=i, event=name, data=data) for i, (name, data) in enumerate(pairs, 1)]
launcher.check_events(base)
print('ACCEPT literal-valid')
mutants = []
x = copy.deepcopy(base); del x[5]; mutants.append(('delete-stage', x))
x = copy.deepcopy(base); x[3]['seq'] = 99; mutants.append(('change-seq', x))
x = copy.deepcopy(base); x[5]['data']['rows'] = [[1, 7]]; mutants.append(('change-copy-result', x))
x = copy.deepcopy(base); x[9]['data']['remaining'] = 1; mutants.append(('change-backup-remaining', x))
x = copy.deepcopy(base); x[-1]['data']['backup_rows'] = []; mutants.append(('change-final-success', x))
x = copy.deepcopy(base); x[14]['data']['main_sha256'] = 'b' * 64; mutants.append(('change-source-hash', x))
for label, events in mutants:
    try:
        launcher.check_events(events)
    except ValueError:
        print('REJECT ' + label)
    else:
        raise RuntimeError('false acceptance: ' + label)
if 'sqlite3' in sys.modules or '_sqlite3' in sys.modules:
    raise RuntimeError('unexpected sqlite import')
print('PASS 1 accepted + 6 rejected; 7 consumer calls; no sqlite import; no subprocess launch')
