import json
from pathlib import Path
import subprocess
import tempfile

here = Path(__file__).resolve().parent
deltas = (-1, 1, -10, 1, 9, 10)
wire = "".join(f"{dx}\n" for dx in deltas)

def reference():
    x = cell = 0
    out = []
    for step, dx in enumerate(deltas, 1):
        x += dx
        next_cell = x // 10
        signal = f"enter:{next_cell}" if cell != next_cell else "-"
        out.append(f"{step},{x},{next_cell},{signal}")
        cell = next_cell
    return out

def rows(exe, mode):
    return subprocess.run([exe, mode], input=wire, text=True,
                          check=True, capture_output=True).stdout.splitlines()

with tempfile.TemporaryDirectory() as td:
    exe = str(Path(td) / "probe")
    subprocess.run(["g++", "-std=c++20", "-O2", "-Wall", "-Wextra",
                    "-Werror", "-fsanitize=undefined", str(here/"engine.cpp"),
                    "-o", exe], check=True)
    trunc, floor = rows(exe, "trunc"), rows(exe, "floor")

expected = reference()
assert floor == expected
assert trunc[-1] == floor[-1] == "6,10,1,enter:1"
i = next(i for i, pair in enumerate(zip(floor, trunc, strict=True))
         if pair[0] != pair[1])
assert i == 0 and trunc[i] == "1,-1,0,-" and floor[i] == "1,-1,-1,enter:-1"
assert [row.split(",")[-1] for row in trunc if not row.endswith(",-")] != [
    row.split(",")[-1] for row in floor if not row.endswith(",-")]

node_result = subprocess.run(
    ["node", "-e", """
const n = JSON.parse('[9007199254740992,9007199254740993]');
const s = JSON.parse('["9007199254740992","9007199254740993"]').map(BigInt);
console.log(JSON.stringify({number_ids_distinct:n[0]!==n[1],
                            decimal_string_ids_distinct:s[0]!==s[1]}));
"""], check=True, text=True, capture_output=True)
ids = json.loads(node_result.stdout)
assert ids == {"number_ids_distinct": False, "decimal_string_ids_distinct": True}

print(json.dumps({"deltas": deltas, "reference_python": expected,
                  "candidate_cpp_trunc": trunc, "candidate_cpp_floor": floor,
                  "first_mismatch_tick": i+1, "identity_node": ids}, indent=2))
