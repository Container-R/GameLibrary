#!/usr/bin/env python3
"""Run this one reviewed fixture once. Never install, fetch, retry, or overwrite."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import resource
import selectors
import signal
import stat
import subprocess
import tempfile
import time

PROTOCOL = "resampler-stream-linear-v1"
COMMIT = "c96f5e3de9c4488f4e6c97f59f5245f22fda22f7"
VERSION = "libsamplerate-0.2.2 (c) 2002-2008 Erik de Castro Lopo"
FILES = ("PROTOCOL.md", "README.md", "src/probe.c", "run_probe.py",
         "fixtures/oracle.json", "fixtures/source-identity.json",
         ".local/upstream/samplerate.h", ".local/upstream/COPYING")
BLOBS = {".local/upstream/samplerate.h": "a3d5ae1aa0859c41a33371dc1c3b3f65f63cb417",
         ".local/upstream/COPYING": "9f82626e6371ceeb76f8d2c9968748ec1584e10f"}
FAILURES = {"none", "version_mismatch", "create_error", "call_error", "count_mismatch",
            "value_mismatch", "input_changed", "guard_changed", "tail_changed",
            "reset_error", "delete_error", "cross_arm_mismatch", "io_error", "driver_bounds"}
HEX = re.compile(r"(?:-?0x[0-9a-f]+(?:\.[0-9a-f]*)?p[+-][0-9]+|nan|-?inf)\Z")
CALL_IDS = ["W1", "S1", "S2", "R1", "R2", "C1", "C2"]
NORMAL = [("create", "W"), ("call", "W1"), ("delete", "W"),
          ("create", "S"), ("call", "S1"), ("call", "S2"), ("delete", "S"),
          ("create", "R"), ("call", "R1"), ("reset", "R"), ("call", "R2"), ("delete", "R"),
          ("create", "C"), ("call", "C1"), ("call", "C2"), ("delete", "C")]


class GateError(Exception):
    pass


def require(test, code):
    if not test:
        raise GateError(code)


def exact_keys(obj, keys):
    require(type(obj) is dict and set(obj) == set(keys), "schema_keys")


def integer(value, low=-(2**63), high=2**63-1):
    return type(value) is int and low <= value <= high


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        require(key not in result, "duplicate_json_key")
        result[key] = value
    return result


def load_json(data):
    def bad_constant(_):
        raise GateError("json_nonfinite_number")
    try:
        return json.loads(data, object_pairs_hook=unique_object, parse_constant=bad_constant)
    except (UnicodeError, ValueError, RecursionError) as exc:
        raise GateError("invalid_json") from exc


def read_file(root, name, maximum=131072):
    path = root / name
    require(not path.is_symlink() and path.resolve().is_relative_to(root), "unsafe_input_path")
    for parent in path.parents:
        if parent == root:
            break
        require(not parent.is_symlink(), "unsafe_input_path")
    fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW)
    try:
        require(stat.S_ISREG(os.fstat(fd).st_mode), "input_not_regular")
        with os.fdopen(fd, "rb", closefd=False) as handle:
            data = handle.read(maximum + 1)
        require(len(data) <= maximum, "input_too_large")
        return data
    finally:
        os.close(fd)


def directory(path, root):
    try:
        path.mkdir(mode=0o700)
    except FileExistsError:
        pass
    require(path.is_dir() and not path.is_symlink() and path.resolve().is_relative_to(root),
            "unsafe_directory")


def reserve_output(root, requested):
    require(re.fullmatch(r"results/[A-Za-z0-9][A-Za-z0-9._-]{0,63}\.json", requested) is not None,
            "unsafe_output_name")
    directory(root / "results", root)
    dirfd = os.open(root / "results", os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        try:
            fd = os.open(requested.split("/")[1], os.O_RDWR | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                         0o600, dir_fd=dirfd)
        except FileExistsError as exc:
            raise GateError("output_exists") from exc
    finally:
        os.close(dirfd)
    os.write(fd, b'{"status":"incomplete"}\n')
    os.fsync(fd)
    return fd


def identities(root):
    freeze_bytes = read_file(root, "FREEZE.json", 16384)
    freeze = load_json(freeze_bytes)
    exact_keys(freeze, {"schema_version", "protocol_id", "files"})
    require(freeze["schema_version"] == 1 and type(freeze["schema_version"]) is int and
            freeze["protocol_id"] == PROTOCOL, "freeze_schema")
    require(type(freeze["files"]) is dict and set(freeze["files"]) == set(FILES), "freeze_file_set")
    contents = {}
    for name in FILES:
        expected = freeze["files"][name]
        require(type(expected) is str and re.fullmatch(r"[0-9a-f]{64}", expected), "freeze_hash")
        contents[name] = read_file(root, name)
        require(hashlib.sha256(contents[name]).hexdigest() == expected, "frozen_input_changed")
    for name, expected in BLOBS.items():
        data = contents[name]
        blob = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        require(blob == expected, "upstream_blob_mismatch")
    source = load_json(contents["fixtures/source-identity.json"])
    exact_keys(source, {"upstream_repository", "upstream_commit", "expected_reported_version",
                        "local_inputs", "binary_provenance"})
    require(source["upstream_repository"] == "libsndfile/libsamplerate" and
            source["upstream_commit"] == COMMIT and source["expected_reported_version"] == VERSION,
            "source_identity")
    require(source["local_inputs"] == [
        {"path":".local/upstream/samplerate.h", "upstream_path":"include/samplerate.h",
         "git_blob_sha1":BLOBS[".local/upstream/samplerate.h"]},
        {"path":".local/upstream/COPYING", "upstream_path":"COPYING",
         "git_blob_sha1":BLOBS[".local/upstream/COPYING"]}], "source_identity")
    require(source["binary_provenance"] ==
            "Self-reported runtime version only; not authentication of the installed library's source commit or build.",
            "source_identity")
    oracle = load_json(contents["fixtures/oracle.json"])
    exact_keys(oracle, {"protocol_id", "unit_denominator", "input_units", "calls"})
    require(oracle["protocol_id"] == PROTOCOL and type(oracle["unit_denominator"]) is int and
            oracle["unit_denominator"] == 16 and oracle["input_units"] == list(range(0,16,2)) and
            all(type(x) is int for x in oracle["input_units"]), "oracle_header")
    require(type(oracle["calls"]) is list and len(oracle["calls"]) == 7, "oracle_calls")
    for expected_id, call in zip(CALL_IDS, oracle["calls"]):
        exact_keys(call, {"id", "input_offset", "input_frames", "output_capacity", "end_of_input",
                          "used", "generated", "output_units"})
        require(call["id"] == expected_id, "oracle_order")
        for key in ("input_offset", "input_frames", "output_capacity", "end_of_input", "used", "generated"):
            require(integer(call[key], 0, 20), "oracle_integer")
        require(0 < call["input_frames"] <= 8 and call["input_offset"]+call["input_frames"] <= 8 and
                call["end_of_input"] in (0,1) and 0 < call["used"] <= call["input_frames"] and
                0 < call["generated"] <= call["output_capacity"] <= 20, "oracle_bounds")
        require(type(call["output_units"]) is list and len(call["output_units"]) == call["generated"] and
                all(integer(x, 0, 14) for x in call["output_units"]), "oracle_array")
    return contents, oracle, {"freeze_sha256":hashlib.sha256(freeze_bytes).hexdigest(),
                              "input_sha256":freeze["files"], "upstream_commit":COMMIT,
                              "upstream_git_blobs":BLOBS}


def group_signal(process, sig):
    try:
        os.killpg(process.pid, sig)
    except ProcessLookupError:
        pass


def group_alive(process):
    try:
        os.killpg(process.pid, 0)
        return True
    except ProcessLookupError:
        return False


def capture(command, cwd, env, limit, native):
    """Bound retained bytes continuously, including while terminating the group."""
    def limits():
        resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
        if native:
            resource.setrlimit(resource.RLIMIT_CPU, (2, 2))
            resource.setrlimit(resource.RLIMIT_AS, (128*1024*1024, 128*1024*1024))
    buffers = {"stdout":bytearray(), "stderr":bytearray()}
    caps = {"stdout":16384, "stderr":4096}
    selector = None
    reason, term_at, kill_at = None, None, None
    cleanup_ok = True
    process = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.DEVNULL,
                               stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                               start_new_session=True, preexec_fn=limits, close_fds=True)
    try:
        # Ownership starts immediately after Popen, including selector setup errors.
        deadline = time.monotonic() + limit
        selector = selectors.DefaultSelector()
        for name, stream in (("stdout",process.stdout), ("stderr",process.stderr)):
            os.set_blocking(stream.fileno(), False)
            selector.register(stream, selectors.EVENT_READ, name)
        while True:
            now = time.monotonic()
            if reason is None and now >= deadline:
                reason = "timeout"
            if reason is not None and term_at is None:
                group_signal(process, signal.SIGTERM)
                term_at = now
            if term_at is not None and kill_at is None and now >= term_at + 1.0:
                group_signal(process, signal.SIGKILL)
                kill_at = now
            if kill_at is not None and now >= kill_at + 0.5:
                cleanup_ok = process.poll() is not None and not group_alive(process)
                break
            for key, _ in selector.select(0.05):
                try:
                    chunk = os.read(key.fileobj.fileno(), 4096)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(key.fileobj)
                    continue
                name = key.data
                room = caps[name] - len(buffers[name])
                buffers[name].extend(chunk[:room])
                if len(chunk) > room and reason is None:
                    reason = name + "_overflow"
            ended = process.poll() is not None
            if ended and not selector.get_map():
                if not group_alive(process):
                    break
                if reason is None:
                    reason = "unexpected_descendant"
    finally:
        # Reap before closing streams, so a close error cannot abandon a child.
        try:
            group_signal(process, signal.SIGKILL)
        except OSError:
            cleanup_ok = False
        try:
            process.wait(timeout=0.5)
        except (subprocess.TimeoutExpired, OSError):
            cleanup_ok = False
        try:
            if group_alive(process):
                cleanup_ok = False
        except OSError:
            cleanup_ok = False
        for opened in (selector, process.stdout, process.stderr):
            if opened is not None:
                try:
                    opened.close()
                except (OSError, ValueError):
                    cleanup_ok = False
    if not cleanup_ok and reason is None:
        reason = "cleanup_incomplete"
    if reason is None and process.returncode != 0:
        reason = "nonzero_exit"
    summary = {"status":"pass" if reason is None else "fail", "reason":reason or "none",
               "return_code":process.returncode, "stdout_retained_bytes":len(buffers["stdout"]),
               "stderr_retained_bytes":len(buffers["stderr"]), "cleanup_confirmed":cleanup_ok}
    return summary, bytes(buffers["stdout"]), bytes(buffers["stderr"])


def record_schema(event):
    require(type(event) is dict and type(event.get("type")) is str, "record_type")
    kind = event["type"]
    if kind == "header":
        exact_keys(event, {"type","protocol_id","upstream_commit","reported_version","version_match",
                           "numeric_prerequisites","converter","channels","ratio","input_units","unit_denominator"})
        require(event["protocol_id"] == PROTOCOL and event["upstream_commit"] == COMMIT and
                event["reported_version"] in (None, VERSION) and type(event["version_match"]) is bool and
                event["version_match"] == (event["reported_version"] == VERSION) and
                event["numeric_prerequisites"] is True and event["converter"] == "SRC_LINEAR" and
                type(event["channels"]) is int and event["channels"] == 1 and
                type(event["ratio"]) is int and event["ratio"] == 2 and
                type(event["unit_denominator"]) is int and event["unit_denominator"] == 16 and
                event["input_units"] == list(range(0,16,2)) and all(type(x) is int for x in event["input_units"]),
                "header_values")
    elif kind in {"create","reset","delete"}:
        extra = {"create":{"return_code","state_present"}, "reset":{"return_code"}, "delete":{"returned_null"}}[kind]
        exact_keys(event, {"type","arm"} | extra)
        require(type(event["arm"]) is str and event["arm"] in {"W","S","R","C"}, "record_arm")
        if "return_code" in extra:
            require(integer(event["return_code"], -(2**31), 2**31-1), "return_code")
        if "state_present" in extra:
            require(type(event["state_present"]) is bool, "state_present")
        if "returned_null" in extra:
            require(type(event["returned_null"]) is bool, "returned_null")
    elif kind == "call":
        exact_keys(event, {"type","id","input_offset","input_frames","output_capacity","end_of_input",
                           "return_code","input_frames_used","output_frames_gen","arena_hex","checks"})
        require(event["id"] in CALL_IDS, "call_id")
        for key in ("input_offset","input_frames","output_capacity","end_of_input","return_code",
                    "input_frames_used","output_frames_gen"):
            require(integer(event[key]), "call_integer")
        require(type(event["arena_hex"]) is list and len(event["arena_hex"]) == 40, "arena_size")
        for value in event["arena_hex"]:
            require(type(value) is str and len(value) <= 32 and HEX.fullmatch(value), "arena_value")
        exact_keys(event["checks"], {"counts","values","input","guards","tail"})
        require(all(type(x) is bool for x in event["checks"].values()), "check_boolean")
    elif kind == "summary":
        exact_keys(event, {"type","status","failure","states_created","delete_calls","process_calls","reset_calls","cross_arm_ok"})
        require(event["status"] in {"pass","fail"} and event["failure"] in FAILURES and
                type(event["cross_arm_ok"]) is bool, "summary_values")
        for key, maximum in (("states_created",4),("delete_calls",4),("process_calls",7),("reset_calls",1)):
            require(integer(event[key],0,maximum), "summary_count")
    else:
        raise GateError("unknown_record")


def verify_native(data, oracle):
    """Return only schema-whitelisted records; never trust native pass flags alone."""
    safe = []
    try:
        require(data.endswith(b"\n"), "incomplete_native_output")
        lines = data.splitlines()
        require(2 <= len(lines) <= 18, "record_count")
        for line in lines:
            event = load_json(line.decode("ascii"))
            record_schema(event)
            safe.append(event)
        require(safe[0]["type"] == "header" and safe[-1]["type"] == "summary", "record_endpoints")
        require(sum(x["type"] == "header" for x in safe) == 1 and
                sum(x["type"] == "summary" for x in safe) == 1, "record_endpoints")
        expected_calls = {x["id"]:x for x in oracle["calls"]}
        cursor, opened, fatal = 0, None, not safe[0]["version_match"]
        counters = {"states_created":0,"delete_calls":0,"process_calls":0,"reset_calls":0}
        assembled = {x:[] for x in "WSRC"}
        for event in safe[1:-1]:
            kind = event["type"]
            key = (kind, event["id"] if kind == "call" else event["arm"])
            if fatal:
                require(opened is not None and key == ("delete",opened), "work_after_failure")
            else:
                require(cursor < len(NORMAL) and key == NORMAL[cursor], "record_order")
                cursor += 1
            if kind == "create":
                require(opened is None, "overlapping_states")
                if event["state_present"]:
                    opened = event["arm"]
                    counters["states_created"] += 1
                fatal = event["return_code"] != 0 or not event["state_present"]
            elif kind == "delete":
                require(opened == event["arm"], "delete_without_state")
                opened = None
                counters["delete_calls"] += 1
                fatal = fatal or not event["returned_null"]
            elif kind == "reset":
                require(opened == "R", "reset_without_state")
                counters["reset_calls"] += 1
                fatal = event["return_code"] != 0
            elif kind == "call":
                require(opened == event["id"][0], "call_without_state")
                counters["process_calls"] += 1
                exp = expected_calls[event["id"]]
                for name in ("input_offset","input_frames","output_capacity","end_of_input"):
                    require(event[name] == exp[name], "call_parameters")
                try:
                    arena = [float.fromhex(x) for x in event["arena_hex"]]
                except (ValueError, OverflowError) as exc:
                    raise GateError("arena_value") from exc
                u, g, cap = event["input_frames_used"], event["output_frames_gen"], exp["output_capacity"]
                valid_g = 0 <= g <= cap
                checks = {
                    "counts":0 <= u <= exp["input_frames"] and valid_g and u == exp["used"] and g == exp["generated"],
                    "values":valid_g and g == exp["generated"] and arena[16:16+g] == [x/16 for x in exp["output_units"]],
                    "input":arena[:8] == [x/16 for x in oracle["input_units"]],
                    "guards":all(arena[i] == 1234 for i in list(range(8,16))+list(range(36,40))),
                    "tail":valid_g and all(x == 1234 for x in arena[16+g:36])}
                require(event["checks"] == checks, "check_disagreement")
                fatal = event["return_code"] != 0 or not all(checks.values())
                if not fatal:
                    assembled[event["id"][0]].extend(arena[16:16+g])
            else:
                raise GateError("record_order")
        summary = safe[-1]
        require(opened is None, "state_not_released")
        require(all(summary[k] == v for k,v in counters.items()), "summary_count_disagreement")
        if summary["status"] == "pass":
            require(not fatal and cursor == len(NORMAL) and summary["failure"] == "none" and
                    summary["cross_arm_ok"], "false_native_pass")
            require(all(len(x) == 16 for x in assembled.values()) and
                    assembled["W"] == assembled["S"] == assembled["C"] and
                    [assembled["R"][i]-assembled["W"][i] for i in range(16)] ==
                    [2/16 if i == 8 else 1/16 if i == 9 else 0 for i in range(16)], "cross_arm_mismatch")
            return safe, "pass", "none"
        require(summary["failure"] != "none" and not summary["cross_arm_ok"], "false_failure_summary")
        return safe, "fail", "native_assertion"
    except (GateError, UnicodeError, TypeError) as exc:
        # Prior complete whitelisted records remain available; untrusted bytes stay private.
        return safe, "fail", str(exc) if isinstance(exc, GateError) else "native_encoding_or_type"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, help="New relative results/name.json; never overwritten")
    args = parser.parse_args()
    root = Path(__file__).absolute().parent
    report = {"protocol_id":PROTOCOL,"status":"failed","reason":"not_started","identity":None,
              "compile":None,"native":None,"native_records":[],"independent_verification":"not_run"}
    fd = None
    try:
        require(root.resolve() == root and not Path(__file__).is_symlink(), "unsafe_package_root")
        fd = reserve_output(root, args.output)
        contents, oracle, report["identity"] = identities(root)
        directory(root/".local", root)
        directory(root/".local"/"runs", root)
        work = Path(tempfile.mkdtemp(prefix="run-", dir=root/".local"/"runs"))
        require(work.is_dir() and not work.is_symlink() and work.resolve().is_relative_to(root), "unsafe_run_directory")
        os.umask(0o077)
        for name in ("src","fixtures","build","home","cache","config","data","tmp","diagnostics"):
            directory(work/name, work)
        directory(work/"fixtures"/"upstream", work)
        for source, target in (("src/probe.c","src/probe.c"),
                               (".local/upstream/samplerate.h","fixtures/upstream/samplerate.h"),
                               (".local/upstream/COPYING","fixtures/upstream/COPYING")):
            with open(work/target, "xb") as handle:
                handle.write(contents[source])
        env = {"PATH":"/usr/bin:/bin", "LC_ALL":"C", "LANG":"C", "HOME":str(work/"home"),
               "XDG_CACHE_HOME":str(work/"cache"), "XDG_CONFIG_HOME":str(work/"config"),
               "XDG_DATA_HOME":str(work/"data"), "TMPDIR":str(work/"tmp")}
        compile_command = ["cc","-std=c11","-O0","-Wall","-Wextra","-Werror",
                           "-Ifixtures/upstream","src/probe.c","-l:libsamplerate.so.0","-o","build/probe"]
        report["compile"], out, err = capture(compile_command, work, env, 15, False)
        (work/"diagnostics"/"compile.stdout").write_bytes(out)
        (work/"diagnostics"/"compile.stderr").write_bytes(err)
        require(report["compile"]["status"] == "pass", "compile_failed")
        binary = work/"build"/"probe"
        require(binary.is_file() and not binary.is_symlink() and binary.resolve().is_relative_to(work), "unsafe_binary_output")
        report["native"], out, err = capture(["./build/probe"], work, env, 3, True)
        (work/"diagnostics"/"native.stdout").write_bytes(out)
        (work/"diagnostics"/"native.stderr").write_bytes(err)
        records, verified, reason = verify_native(out, oracle)
        report["native_records"] = records
        report["independent_verification"] = verified
        require(report["native"]["status"] == "pass", "native_failed")
        require(not err, "unexpected_native_stderr")
        require(verified == "pass", reason)
        report["status"], report["reason"] = "passed", "none"
    except GateError as exc:
        report["reason"] = str(exc)
    except (OSError, subprocess.SubprocessError, ValueError) as exc:
        # Do not serialize system exception messages, which may contain private paths.
        report["reason"] = "runner_system_error"
    finally:
        if fd is not None:
            encoded = (json.dumps(report, ensure_ascii=True, allow_nan=False, separators=(",",":"))+"\n").encode("ascii")
            # Report size is bounded separately from the two child capture streams.
            if len(encoded) > 65536:
                encoded = b'{"status":"failed","reason":"report_size_limit"}\n'
                report["status"], report["reason"] = "failed", "report_size_limit"
            try:
                os.lseek(fd, 0, os.SEEK_SET)
                os.ftruncate(fd, 0)
                with os.fdopen(fd, "wb") as handle:
                    fd = None
                    handle.write(encoded)
                    handle.flush()
                    os.fsync(handle.fileno())
            except OSError:
                report["status"], report["reason"] = "failed", "report_write_failed"
                if fd is not None:
                    os.close(fd)
        print(json.dumps({"status":report["status"],"reason":report["reason"]}, separators=(",",":")))
    return 0 if report["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
