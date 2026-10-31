"""Local Git byte-policy check; no network, no user Git configuration changes."""
import json
from pathlib import Path
import subprocess
import tempfile
root = Path(__file__).resolve().parents[3]
with tempfile.TemporaryDirectory(prefix='evidence-git-bytes-') as temp:
    path = Path(temp)
    def git(*args):
        return subprocess.run(['git', '-c', 'core.hooksPath=/dev/null', '-c', 'commit.gpgSign=false', *args], cwd=path, text=True, capture_output=True, check=True)
    git('init', '-q')
    git('config', 'core.autocrlf', 'true')
    (path / '.gitattributes').write_bytes((root / '.gitattributes').read_bytes())
    original = b'first\nsecond\n'
    (path / 'evidence.txt').write_bytes(original)
    git('add', '.')
    git('-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.invalid', 'commit', '-qm', 'fixture')
    (path / 'evidence.txt').unlink()
    git('checkout', '--', 'evidence.txt')
    if (path / 'evidence.txt').read_bytes() != original:
        raise RuntimeError('checkout changed evidence bytes')
    (path / 'evidence.txt').write_bytes(b'first\nchanged\n')
    diff = git('diff', '--', 'evidence.txt').stdout
    if '-second' not in diff or '+changed' not in diff or 'Binary files' in diff:
        raise RuntimeError('ordinary text diff not observed')
    report = {'scope': 'Linux temporary Git repo, core.autocrlf=true; not Windows OS test',
              'checkout_exact_bytes': True, 'ordinary_text_diff': True,
              'git': git('--version').stdout.strip()}
print(json.dumps(report, indent=2))
