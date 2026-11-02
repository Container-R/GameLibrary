"""PROPOSAL ONLY. One sandboxed browser invocation; separate authorization required."""
import hashlib
import json
import math
import os
from pathlib import Path
import shutil
import signal
import subprocess
import sys
import time
from isolation import prepare_environment, validate_environment

INPUTS = ('PROTOCOL.md', 'fixture.html', 'runner.py', 'isolation.py')
CASES = (('he-raw', '\u05d0\u05d1\u05d2', False, 'left'),
         ('he-bdi', '\u05d0\u05d1\u05d2', True, 'right'),
         ('ascii-raw', 'Alex', False, 'right'),
         ('ascii-bdi', 'Alex', True, 'right'))

class Stop(Exception):
    pass

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

def publish(root, name, data):
    pending = root / (name + '.pending')
    final = root / name
    if os.path.lexists(final):
        raise Stop('result_exists')
    with pending.open('x', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2, allow_nan=False)
        f.write('\n')
    os.replace(pending, final)

def worker(base, root, executable):
    # Import only after supervisor has prepared this process's five locations.
    from playwright.sync_api import sync_playwright
    from importlib.metadata import version
    phase = root / 'environment'
    validate_environment(os.environ, phase)
    profile = phase / 'profile'
    cache = phase / 'browser-cache'
    profile.mkdir(exist_ok=False)
    cache.mkdir(exist_ok=False)
    data = {'schema': 1, 'status': 'INCOMPLETE', 'rows': [], 'page_request_count': 0}
    failure = None
    context = None
    try:
        with sync_playwright() as pw:
            validate_environment(os.environ, phase)
            context = pw.chromium.launch_persistent_context(
                str(profile), executable_path=executable,
                chromium_sandbox=True, headless=True, timeout=20000,
                env=dict(os.environ), viewport={'width': 1000, 'height': 500},
                device_scale_factor=1, locale='en-US', timezone_id='UTC',
                offline=True, service_workers='block', accept_downloads=False,
                args=['--disk-cache-dir=' + str(cache)])
            try:
                def abort(route):
                    data['page_request_count'] += 1
                    route.abort()
                context.route('**/*', abort)
                page = context.pages[0] if context.pages else context.new_page()
                page.set_default_timeout(10000)
                errors = []
                page.on('pageerror', lambda error: errors.append('PAGE_ERROR'))
                page.set_content((base / 'fixture.html').read_text(encoding='utf-8'))
                for ident, name, isolated, expected in CASES:
                    page.evaluate('''({id,name,isolated}) => {
                      const row=document.getElementById(id);
                      row.replaceChildren(document.createTextNode('Player '));
                      const nick=document.createElement(isolated?'bdi':'span');
                      nick.className='nick'; if(isolated) nick.dir='auto';
                      nick.textContent=name; row.append(nick);
                      const tail=document.createElement('span'); tail.className='tail';
                      tail.textContent=': 12 points'; row.append(tail);
                    }''', {'id': ident, 'name': name, 'isolated': isolated})
                page.evaluate('document.fonts.ready')
                data['browser_version'] = context.browser.version
                data['playwright_version'] = version('playwright')
                data['rows'] = page.evaluate('''() => Array.from(document.querySelectorAll('.row')).map(row => {
                  function rect(node,start,end) {
                    const range=document.createRange(); range.setStart(node,start); range.setEnd(node,end);
                    const r=range.getBoundingClientRect();
                    return {left:r.left,right:r.right,top:r.top,bottom:r.bottom};
                  }
                  const n=row.querySelector('.nick'), t=row.querySelector('.tail').firstChild;
                  return {id:row.id,logical:row.textContent,nickname:n.textContent,
                    nickname_rect:rect(n.firstChild,0,n.firstChild.length),
                    colon_rect:rect(t,0,1),digits_rect:rect(t,2,4),
                    row_direction:getComputedStyle(row).direction,
                    nickname_bidi:getComputedStyle(n).unicodeBidi,
                    declared_font:getComputedStyle(row).fontFamily};
                })''')
                page.screenshot(path=str(root / 'four-rows.png'), full_page=True, timeout=10000)
                if errors:
                    raise Stop('page_error')
                if data['page_request_count'] != 0:
                    raise Stop('unexpected_page_request')
                check_rows(data['rows'])
                data['status'] = 'GEOMETRY_MATCH_AWAITING_VISUAL_REVIEW'
            except BaseException as exc:
                failure = str(exc) if type(exc) is Stop else type(exc).__name__
                raise
            finally:
                context.close()
                context = None
    except BaseException as exc:
        if failure is None:
            failure = str(exc) if type(exc) is Stop else type(exc).__name__
        data['status'] = 'FAIL'
        data['error'] = failure
    publish(root, 'observation.json', data)
    return 1 if failure else 0

def check_rows(rows):
    if type(rows) is not list or len(rows) != 4:
        raise Stop('row_count')
    for row, (ident, name, isolated, expected) in zip(rows, CASES):
        if row['id'] != ident or row['logical'] != 'Player ' + name + ': 12 points' or row['nickname'] != name:
            raise Stop('logical_content')
        if row['row_direction'] != 'ltr' or row['nickname_bidi'] != ('isolate' if isolated else 'normal'):
            raise Stop('style')
        for key in ('nickname_rect', 'colon_rect', 'digits_rect'):
            r = row[key]
            if any(type(v) not in (int, float) or not math.isfinite(v) for v in r.values()):
                raise Stop('nonfinite_rect')
            if not (r['right'] > r['left'] and r['bottom'] > r['top']):
                raise Stop('empty_rect')
        n, d, c = (row[k] for k in ('nickname_rect', 'digits_rect', 'colon_rect'))
        if max(n['top'], d['top'], c['top']) >= min(n['bottom'], d['bottom'], c['bottom']):
            raise Stop('not_same_line')
        if expected == 'left':
            good = d['right'] <= c['left'] and c['right'] <= n['left']
        else:
            good = n['right'] <= c['left'] and c['right'] <= d['left']
        if not good:
            raise Stop('preregistered_position_mismatch')

def cleanup(proc, record):
    ok = True
    try:
        os.killpg(proc.pid, signal.SIGKILL)
        record['group_cleanup'] = 'SIGNAL_SENT'
    except ProcessLookupError:
        record['group_cleanup'] = 'NO_GROUP'
    except BaseException:
        record['group_cleanup'] = 'FAILED'
        ok = False
    try:
        proc.wait(timeout=10)
        record['leader_cleanup'] = 'REAPED'
    except BaseException:
        record['leader_cleanup'] = 'FAILED'
        ok = False
    # Reaping the leader is not proof that the remaining group disappeared.
    deadline = time.monotonic() + 3.0
    while True:
        try:
            os.killpg(proc.pid, 0)
        except ProcessLookupError:
            record['group_absence'] = 'CONFIRMED_ABSENT'
            break
        except BaseException:
            record['group_absence'] = 'CHECK_FAILED'
            ok = False
            break
        if time.monotonic() >= deadline:
            record['group_absence'] = 'UNCONFIRMED_TIMEOUT'
            ok = False
            break
        time.sleep(0.05)
    return ok

def main():
    if len(sys.argv) != 2:
        raise Stop('usage_runner_NEW_DIRECTORY')
    base = Path(__file__).resolve().parent
    root = Path(sys.argv[1]).absolute()
    for p in (root, *root.parents):
        if p.is_symlink() or '..' in p.parts:
            raise Stop('unsafe_output_path')
    root.mkdir(exist_ok=False)
    record = {'schema': 1, 'status': 'INCOMPLETE', 'sandbox_requested': True}
    phase = root / 'environment'
    proc = None
    owned = False
    cleaned = False
    failure = None
    before = None
    manifest_before = None
    try:
        manifest_before = digest(base / 'INPUT-MANIFEST.json')
        record['manifest_before_sha256'] = manifest_before
        manifest = json.loads((base / 'INPUT-MANIFEST.json').read_text())
        before = {n: digest(base / n) for n in INPUTS}
        if manifest != {'schema': 1, 'files': before}:
            raise Stop('input_binding')
        record['input_before'] = before
        phase.mkdir(exist_ok=False)
        owned = True
        env, _ = prepare_environment({'PATH': os.defpath, 'LANG': 'C.UTF-8', 'LC_ALL': 'C.UTF-8'}, phase)
        executable = shutil.which('chromium', path=os.defpath)
        if executable is None:
            raise Stop('chromium_unavailable')
        validate_environment(env, phase)
        record['environment'] = 'VALIDATED_BEFORE_WORKER_LAUNCH'
        # No inherited secrets, browser logs or environment mapping in public streams.
        proc = subprocess.Popen([sys.executable, str(base / 'runner.py'), '--worker', str(root), executable],
                                cwd=root, env=env, stdout=subprocess.DEVNULL,
                                stderr=subprocess.DEVNULL, start_new_session=True)
        try:
            rc = proc.wait(timeout=70)
        except subprocess.TimeoutExpired:
            raise Stop('worker_timeout')
        record['worker_returncode'] = rc
        if rc != 0:
            raise Stop('worker_failed')
        observation = json.loads((root / 'observation.json').read_text())
        if observation['status'] != 'GEOMETRY_MATCH_AWAITING_VISUAL_REVIEW':
            raise Stop('worker_not_accepted')
        check_rows(observation['rows'])
        record['observation_sha256'] = digest(root / 'observation.json')
        record['screenshot_sha256'] = digest(root / 'four-rows.png')
    except BaseException as exc:
        failure = str(exc) if type(exc) is Stop else type(exc).__name__
    finally:
        cleaned = proc is None or cleanup(proc, record)
        if not cleaned and failure is None:
            failure = 'process_cleanup_failed'
        if before is None:
            record['post_binding'] = 'NOT_STARTED_NO_BEFORE'
        else:
            # Best effort on every outcome; never replace the first failure.
            try:
                record['input_after'] = {n: digest(base / n) for n in INPUTS}
                record['manifest_after_sha256'] = digest(base / 'INPUT-MANIFEST.json')
                changed = (record['input_after'] != before or
                           record['manifest_after_sha256'] != manifest_before)
                record['post_binding'] = 'CHANGED' if changed else 'UNCHANGED'
                if changed and failure is None:
                    failure = 'input_changed'
            except BaseException as exc:
                record['post_binding'] = 'CHECK_FAILED'
                record['post_binding_error_type'] = type(exc).__name__
                if failure is None:
                    failure = 'post_binding_failed'
        if owned and cleaned:
            try:
                shutil.rmtree(phase)
                record['environment_cleanup'] = 'REMOVED'
            except BaseException:
                record['environment_cleanup'] = 'FAILED'
                if failure is None:
                    failure = 'environment_cleanup_failed'
        elif owned:
            record['environment_cleanup'] = 'RETAINED_CLEANUP_UNCONFIRMED'
    record['status'] = 'FAIL' if failure else 'AWAITING_VISUAL_REVIEW'
    record['error'] = failure
    publish(root, 'receipt.json', record)
    return 1 if failure else 0

if __name__ == '__main__':
    try:
        if len(sys.argv) == 4 and sys.argv[1] == '--worker':
            code = worker(Path(__file__).resolve().parent, Path(sys.argv[2]), sys.argv[3])
        else:
            code = main()
    except BaseException as exc:
        # No traceback or exception message containing host locations.
        print('STOP_' + type(exc).__name__, file=sys.stderr)
        code = 1
    sys.exit(code)
