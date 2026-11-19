"""Actual Godot Control focus and synthetic UI action in a disposable project, bounded execution, stdout JSON."""
from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess,os,json
with TemporaryDirectory(prefix='recycled-menu-focus-') as t:
    d=Path(t)
    (d/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Recycled menu focus fixture"\n')
    (d/'probe.gd').write_bytes(Path(__file__).with_name('probe.gd').read_bytes())
    env=dict(os.environ)
    for key in ['CACHE','CONFIG','DATA']:
        p=d/key;p.mkdir();env[f'XDG_{key}_HOME']=str(p)
    try:
        r=subprocess.run([env.get('GODOT','godot'),'--headless','--quit-after','60','--path',str(d),'--script','res://probe.gd'],env=env,capture_output=True,text=True,timeout=60)
    except subprocess.TimeoutExpired as e:
        raise RuntimeError({'timeout':e.timeout,'stdout':str(e.stdout),'stderr':str(e.stderr)}) from e
    if r.returncode or 'ERROR:' in r.stderr or 'SCRIPT ERROR' in r.stderr:
        raise RuntimeError((r.returncode,r.stdout,r.stderr))
    lines=[s[9:] for s in r.stdout.splitlines() if s.startswith('OBSERVED ')]
    assert len(lines)==1,(r.stdout,r.stderr)
    print(json.dumps(json.loads(lines[0]),indent=2,sort_keys=True))
