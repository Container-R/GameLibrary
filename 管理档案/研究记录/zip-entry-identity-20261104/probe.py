"""Original finite probe. Execute only through the reviewed-freeze runner."""
import io
import json
import sys
import warnings
import zipfile

A = b'{"damage":1}\n'
B = b'{"damage":2}\n'
N = "weapons/rifle.json"
M = "weapons/pistol.json"
CASES = (
    ("unique", ((N, A), (M, B))),
    ("duplicate_ab", ((N, A), (N, B))),
    ("duplicate_ba", ((N, B), (N, A))),
    ("duplicate_aa", ((N, A), (N, A))),
)


def observe(case_id, entries):
    storage = io.BytesIO()
    with warnings.catch_warnings(record=True) as captured:
        warnings.simplefilter("always")
        with zipfile.ZipFile(storage, "w", compression=zipfile.ZIP_STORED) as writer:
            for name, payload in entries:
                info = zipfile.ZipInfo(name, date_time=(2020, 1, 1, 0, 0, 0))
                info.compress_type = zipfile.ZIP_STORED
                writer.writestr(info, payload)
    write_warnings = [
        {"category": w.category.__name__, "message": str(w.message)}
        for w in captured
    ]
    rows = []
    storage.seek(0)
    with warnings.catch_warnings(record=True) as captured_read:
        warnings.simplefilter("always")
        with zipfile.ZipFile(storage, "r") as reader:
            infos = reader.infolist()
            duplicates = sorted({i.filename for i in infos
                                 if sum(j.filename == i.filename for j in infos) > 1})
            for ordinal, info in enumerate(infos):
                # Retain the exact unmodified member object from this reader.
                by_name = reader.read(info.filename)
                by_entry = reader.read(info)
                selected = reader.getinfo(info.filename)
                rows.append({
                    "ordinal": ordinal,
                    "name": info.filename,
                    "metadata_size": info.file_size,
                    "name_selected_ordinal": next(k for k, x in enumerate(infos)
                                                  if x is selected),
                    "by_name": by_name.decode("utf-8"),
                    "by_entry": by_entry.decode("utf-8"),
                    "by_name_size": len(by_name),
                    "by_entry_size": len(by_entry),
                })
            distinct_entries = len(infos) == 2 and infos[0] is not infos[1]
    return {
        "case": case_id,
        "entry_count": len(rows),
        "distinct_entry_objects": distinct_entries,
        "write_warnings": write_warnings,
        "read_warnings": [
            {"category": w.category.__name__, "message": str(w.message)}
            for w in captured_read
        ],
        "duplicates": duplicates,
        "project_decision": "reject" if duplicates else "accept",
        "rows": rows,
    }


def main():
    try:
        payload = {"schema": 1, "status": "observed",
                   "python": list(sys.version_info[:3]),
                   "cases": [observe(label, entries) for label, entries in CASES]}
        print(json.dumps(payload, ensure_ascii=True, sort_keys=True))
    except Exception as exc:
        # No traceback, local path, process ID or arbitrary exception text.
        print(json.dumps({"schema": 1, "status": "probe_error",
                          "error_type": type(exc).__name__}))
        raise SystemExit(2)


if __name__ == "__main__":
    main()
