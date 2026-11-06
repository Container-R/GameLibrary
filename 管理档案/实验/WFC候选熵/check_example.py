"""Original arithmetic check, not a WFC implementation or generator execution."""
import json
import math

weights = {"P": 1.0, "Q": 1.0, "R": 98.0}
domains = {"X": ["P", "Q"], "Y": ["P", "Q", "R"]}
results = {}
for name, domain in domains.items():
    ws = [weights[t] for t in domain]
    total = sum(ws)
    ps = [w / total for w in ws]
    direct = -sum(p * math.log(p) for p in ps)
    cached_form = math.log(total) - sum(w * math.log(w) for w in ws) / total
    assert math.isclose(direct, cached_form, abs_tol=1e-14)
    results[name] = {
        "candidates": domain,
        "candidate_count": len(domain),
        "normalized_weights": ps,
        "shannon_entropy_nats": direct,
        "model_formula_nats": cached_form,
    }

assert results["X"]["candidate_count"] < results["Y"]["candidate_count"]
assert results["Y"]["shannon_entropy_nats"] < results["X"]["shannon_entropy_nats"]
gap = results["X"]["shannon_entropy_nats"] - results["Y"]["shannon_entropy_nats"]
assert gap > 1e-6
# Equal positive weights reduce the formula to log(candidate count).
for count in [2, 3, 4]:
    p = 1.0 / count
    assert math.isclose(-count * p * math.log(p), math.log(count), abs_tol=1e-14)

print(json.dumps({
    "scope": "Original arithmetic illustration only; no WFC run, adjacency model, seed, or engine tested.",
    "global_weights": weights,
    "positions": results,
    "mrv_first_among_these_two": "X",
    "entropy_first_among_these_two": "Y",
    "entropy_gap_nats": gap,
    "noise_upper_bound_exclusive": 1e-6,
    "checks": "passed",
}, indent=2))
