"""Synthetic process-control mocks only: no compiler, process or signal is run."""
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock, patch
import runner

class CleanupTests(unittest.TestCase):
    def exercise(self, *, waits, diagnostics=b'', kill_error=None, expected=None):
        with tempfile.TemporaryDirectory(prefix='entt-cleanup-mock-') as folder:
            work = Path(folder)
            proc = Mock()
            proc.pid = 123  # synthetic identifier; never passed to real os.killpg
            proc.wait.side_effect = waits
            proc.poll.side_effect = AssertionError('leader poll must not gate group cleanup')
            receipt = {'processes': []}
            def launch(*args, **kwargs):
                kwargs['stderr'].write(diagnostics)
                return proc
            with patch.object(runner.subprocess, 'Popen', side_effect=launch) as popen, patch.object(runner.os, 'killpg', side_effect=kill_error) as kill:
                if expected is None:
                    self.assertEqual(runner.process(['mock-compiler'], work, 'build', 120, receipt), b'')
                else:
                    with self.assertRaises(runner.Stop) as caught:
                        runner.process(['mock-compiler'], work, 'build', 120, receipt)
                    self.assertEqual(str(caught.exception), expected)
                popen.assert_called_once()
                kill.assert_called_once_with(123, runner.signal.SIGKILL)
                proc.poll.assert_not_called()
                self.assertEqual(proc.wait.call_args_list[-1].kwargs, {'timeout': 10})
            self.assertTrue((work / 'build.stdout').exists())
            self.assertEqual((work / 'build.stderr').read_bytes(), diagnostics)
            return receipt['processes'][0]

    def test_leader_exited_nonzero_still_cleans_group(self):
        event = self.exercise(waits=[7, 7], expected='build_return')
        self.assertEqual(event['returncode'], 7)
        self.assertEqual(event['group_cleanup'], 'SIGNAL_SENT')

    def test_diagnostic_rejection_cleans_exited_leader_group(self):
        event = self.exercise(waits=[0, 0], diagnostics=b'synthetic warning\n', expected='build_diagnostics')
        self.assertEqual(event['group_cleanup'], 'SIGNAL_SENT')

    def test_group_cleanup_error_preserves_nonzero_error(self):
        event = self.exercise(waits=[7, 7], kill_error=PermissionError(), expected='build_return')
        self.assertEqual(event['group_cleanup'], 'FAILED')
        self.assertEqual(event['leader_cleanup'], 'REAPED')

    def test_wait_cleanup_error_preserves_diagnostic_error(self):
        event = self.exercise(waits=[0, RuntimeError()], diagnostics=b'synthetic warning\n', expected='build_diagnostics')
        self.assertEqual(event['leader_cleanup'], 'FAILED')

    def test_timeout_preserved_if_leader_exited_and_group_gone(self):
        event = self.exercise(waits=[runner.subprocess.TimeoutExpired('mock', 120), 0], kill_error=ProcessLookupError(), expected='build_timeout')
        self.assertTrue(event['timeout'])
        self.assertEqual(event['group_cleanup'], 'NO_GROUP')

    def test_success_also_closes_group_before_return(self):
        event = self.exercise(waits=[0, 0], kill_error=ProcessLookupError())
        self.assertEqual(event['group_cleanup'], 'NO_GROUP')

    def test_success_cleanup_failure_is_failure(self):
        event = self.exercise(waits=[0, 0], kill_error=PermissionError(), expected='build_cleanup')
        self.assertEqual(event['group_cleanup'], 'FAILED')

class ReceiptPublicationTests(unittest.TestCase):
    def test_write_failure_never_publishes_formal_pass(self):
        with tempfile.TemporaryDirectory(prefix='entt-receipt-mock-') as folder:
            root = Path(folder)
            def fail_after_parseable_prefix(value, stream, **kwargs):
                stream.write('{"status":"PASS"}')
                raise OSError('synthetic write failure')
            with patch.object(runner.json, 'dump', side_effect=fail_after_parseable_prefix):
                with self.assertRaises(OSError):
                    runner.publish_receipt(root, {'status': 'PASS'})
            self.assertFalse((root / 'receipt.json').exists())
            self.assertTrue((root / 'receipt.pending.json').exists())

    def test_close_failure_never_publishes_formal_pass(self):
        with tempfile.TemporaryDirectory(prefix='entt-receipt-mock-') as folder:
            root = Path(folder)
            original_open = Path.open
            class FailingClose:
                def __init__(self, file):
                    self.file = file
                def __enter__(self):
                    return self.file
                def __exit__(self, *args):
                    self.file.close()
                    raise OSError('synthetic close failure')
            def wrapped_open(path, *args, **kwargs):
                return FailingClose(original_open(path, *args, **kwargs))
            with patch.object(Path, 'open', new=wrapped_open):
                with self.assertRaises(OSError):
                    runner.publish_receipt(root, {'status': 'PASS'})
            self.assertFalse((root / 'receipt.json').exists())
            self.assertTrue((root / 'receipt.pending.json').exists())

    def test_closed_pending_is_only_then_published(self):
        with tempfile.TemporaryDirectory(prefix='entt-receipt-mock-') as folder:
            root = Path(folder)
            runner.publish_receipt(root, {'status': 'SYNTHETIC_ONLY'})
            self.assertFalse((root / 'receipt.pending.json').exists())
            self.assertEqual(runner.json.loads((root / 'receipt.json').read_text()), {'status': 'SYNTHETIC_ONLY'})

if __name__ == '__main__':
    unittest.main()
