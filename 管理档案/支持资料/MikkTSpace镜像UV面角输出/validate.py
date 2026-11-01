"""Finite offline consumer: no compiler, generator, author fixture imports or engine."""
import json
import hashlib
import math
import sys
from pathlib import Path

def require(condition, message):
    if not condition:
        raise ValueError(message)

def pairs(items):
    result = {}
    for key, value in items:
        require(key not in result, "duplicate JSON key")
        result[key] = value
    return result

def reject_constant(value):
    raise ValueError("nonfinite JSON token: " + value)

def read(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=pairs,
                      parse_constant=reject_constant)

def integer(value):
    return type(value) is int

def number(value):
    return type(value) in (int, float) and math.isfinite(value)

def check_rows(actual, expected, tolerance):
    require(type(actual) is list and len(actual) == 6, "six rows required")
    for row, wanted in zip(actual, expected):
        require(type(row) is list and len(row) == 15, "row shape")
        for index, (value, target) in enumerate(zip(row, wanted)):
            if index < 3:
                require(integer(value) and value == target, "identity mismatch")
            else:
                require(number(value), "invalid numeric field")
                limit = tolerance if 11 <= index <= 13 else 0
                require(abs(value-target) <= limit, "attribute mismatch")

def validate(observation):
    oracle_bytes = Path(__file__).with_name("expected.json").read_bytes()
    require(hashlib.sha256(oracle_bytes).hexdigest() ==
            "bb0b71cc525a8f4438a1ddc464e2a42d16aa83055bfc232be129f6139e3a3532",
            "frozen oracle identity mismatch")
    expected = json.loads(oracle_bytes.decode("utf-8"), object_pairs_hook=pairs,
                          parse_constant=reject_constant)
    require(type(observation) is dict and set(observation) == {
        "schema", "generated", "output_count", "callback_order", "raw", "reindexed",
        "new_indices", "forward_readback", "reverse_readback"}, "observation fields")
    for name, value in (("schema", 1), ("generated", 1), ("output_count", 6)):
        require(integer(observation[name]) and observation[name] == value, name)
    order = observation["callback_order"]
    require(type(order) is list and len(order) == 6 and all(integer(x) for x in order)
            and sorted(order) == [0,1,2,3,4,5], "callback coverage")
    indices = observation["new_indices"]
    require(type(indices) is list and len(indices) == 2 and all(
        type(row) is list and len(row) == 3 and all(integer(x) for x in row)
        for row in indices) and indices == expected["new_indices"], "new indices")
    tolerance = expected["tangent_absolute_tolerance"]
    check_rows(observation["raw"], expected["raw"], tolerance)
    check_rows(observation["reindexed"], expected["raw"], tolerance)
    for direction in ("forward", "reverse"):
        rows = [row[:] for row in expected["raw"]]
        for row, sign in zip(rows, expected[direction+"_signs"]):
            row[14] = sign
        check_rows(observation[direction+"_readback"], rows, tolerance)
        mismatches = [row[:2] for row, original in zip(observation[direction+"_readback"],
                      observation["raw"]) if row[14] != original[14]]
        require(mismatches == expected[direction+"_mismatches"], "overwrite witnesses")
    return {"result": "PASS", "expected_fixture_calls": 1, "face_corners": 6,
            "forward_conflicting_corners": 2, "reverse_conflicting_corners": 2,
            "scope": "one fixed input; no rendering, exporter, or general mesh proof"}

if __name__ == "__main__":
    require(len(sys.argv) == 2, "usage: python -B validate.py observation.json")
    print(json.dumps(validate(read(sys.argv[1])),
                     ensure_ascii=False, sort_keys=True))
