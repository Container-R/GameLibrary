"""Two arranged real-file traces, not a cloud or crash-safety implementation."""
import hashlib
import json
import multiprocessing as mp
import os
from pathlib import Path
import platform
import subprocess
import sys
import tempfile
from datetime import datetime, timezone


def blob(rev):
    payload = (rev + ':payload:') * 1024
    return json.dumps({'rev': rev, 'payload': payload,
                       'digest': hashlib.sha256(payload.encode()).hexdigest()},
                      sort_keys=True).encode()


def inspect(path):
    raw = path.read_bytes()
    obj = json.loads(raw)
    assert hashlib.sha256(obj['payload'].encode()).hexdigest() == obj['digest']
    assert raw == blob(obj['rev'])
    return {'rev': obj['rev'], 'bytes': len(raw),
            'file_sha256': hashlib.sha256(raw).hexdigest()}


def old_writer(root, checked, release, invalidated, control, result):
    try:
        root = Path(root)
        assert root.joinpath('save.json').read_bytes() == blob('O')
        checked.set()
        if not release.wait(20):
            raise TimeoutError('publication barrier')
        published = False
        # Only the control checks immediately before the publication API call.
        if not (control and invalidated.is_set()):
            os.replace(root / 'A.tmp', root / 'save.json')
            published = True
        result.send({'published': published,
                     'completion_accepted': not invalidated.is_set()})
    except BaseException as exc:
        result.send({'error': repr(exc)})
        raise
    finally:
        result.close()


def trace(control):
    ctx = mp.get_context('spawn')
    checked, release, invalidated = (ctx.Event() for _ in range(3))
    receiver, sender = ctx.Pipe(duplex=False)
    with tempfile.TemporaryDirectory(prefix='save-publication-') as directory:
        root = Path(directory)
        fs = subprocess.check_output(['stat', '-f', '-c', '%T', directory], text=True).strip()
        for name, rev in [('save.json','O'),('A.tmp','A'),('B.tmp','B')]:
            root.joinpath(name).write_bytes(blob(rev))  # closed before publication
        worker = ctx.Process(target=old_writer,
                             args=(directory,checked,release,invalidated,control,sender))
        worker.start(); sender.close()
        try:
            assert checked.wait(20), 'old writer did not confirm baseline'
            os.replace(root / 'B.tmp', root / 'save.json')
            after_b = inspect(root / 'save.json')
            assert after_b['rev'] == 'B'
            invalidated.set()
            release.set()
            assert receiver.poll(20), 'worker did not return'
            outcome = receiver.recv()
            worker.join(20)
            assert not worker.is_alive() and worker.exitcode == 0, 'worker failure'
            assert 'error' not in outcome, outcome
            final = inspect(root / 'save.json')
            expected = 'B' if control else 'A'
            assert final['rev'] == expected
            assert outcome == {'published': not control, 'completion_accepted': False}
            data = {'case': 'arranged_presyscall_recheck' if control else 'stale_replace_counterexample',
                    'filesystem': fs, 'after_B_publication': after_b, 'worker': outcome,
                    'final': final, 'expected_final': expected,
                    'barrier_order': ['old_baseline_checked','B_replace_returned_and_read',
                                      'epoch_invalidated','old_writer_released','worker_joined','final_read']}
        finally:
            release.set()  # no terminate/kill; child wait is bounded
            worker.join(25)
            receiver.close()
        assert not worker.is_alive()
    data['temporary_directory_removed'] = not Path(directory).exists()
    assert data['temporary_directory_removed']
    return data

if __name__ == '__main__':
    report = {'executed_at_utc': datetime.now(timezone.utc).isoformat(),
              'python': sys.version, 'platform': platform.platform(),
              'kernel': platform.release(), 'machine': platform.machine(),
              'publication_api': 'Python os.replace(src, dst), same-directory paths; no syscall tracing',
              'multiprocessing_start_method': 'spawn',
              'code_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'traces': [trace(False),trace(True)]}
    print(json.dumps(report,indent=2))
