"""Runs isolated actual Godot layout; source directory stays free of import cache."""
from pathlib import Path
from tempfile import TemporaryDirectory
import os,subprocess,json
source=Path(__file__).with_name('layout.gd')
with TemporaryDirectory(prefix='safe-area-control-') as tmp:
    d=Path(tmp)
    (d/'project.godot').write_text('config_version=5\n[application]\nconfig/name="Mock safe-area layout"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
    (d/'layout.gd').write_bytes(source.read_bytes())
    env=dict(os.environ)
    for n in ['CACHE','CONFIG','DATA']:
        q=d/n.lower();q.mkdir();env[f'XDG_{n}_HOME']=str(q)
    try:
        p=subprocess.run([env.get('GODOT','godot'),'--headless','--quit-after','120','--path',str(d),'--script','res://layout.gd'],env=env,text=True,capture_output=True,timeout=60)
    except subprocess.TimeoutExpired as e:
        raise RuntimeError({'timeout_seconds':e.timeout,'stdout':str(e.stdout),'stderr':str(e.stderr)}) from e
    if p.returncode or 'SCRIPT ERROR' in p.stderr or 'ERROR:' in p.stderr:
        raise RuntimeError((p.returncode,p.stdout,p.stderr))
    rows=[x[len('OBSERVED '):] for x in p.stdout.splitlines() if x.startswith('OBSERVED ')]
    assert len(rows)==1,(p.stdout,p.stderr)
    print(json.dumps(json.loads(rows[0]),indent=2,sort_keys=True))
