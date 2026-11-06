#!/usr/bin/env python3
"""Exact arithmetic for a complete player ledger, not an experiment validator.

Usage: python3 compare_player_ratios.py player-ledger.csv
Writes JSON to stdout only. No files are created or replaced by the script.
The caller must independently verify the population, windows, assignment,
identities, observation completeness, and the independent-player model.
"""
import argparse
import csv
from fractions import Fraction
import json
import math
import sys

COLUMNS = {"player", "arm", "successes", "starts", "unknown", "mature", "quality"}


def load_ledger(path):
    with open(path, encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        if reader.fieldnames is None or set(reader.fieldnames) != COLUMNS or len(reader.fieldnames) != len(COLUMNS):
            raise ValueError("CSV must contain exactly the documented columns, once each")
        rows, seen = [], set()
        for line, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise ValueError(f"row {line}: missing or extra CSV fields")
            row = {key: value.strip() for key, value in row.items()}
            player = row["player"]
            if not player or player in seen:
                raise ValueError(f"row {line}: missing or duplicate player")
            seen.add(player)
            if row["arm"] not in {"C", "T"}:
                raise ValueError(f"row {line}: arm must be C or T")
            for key in ("successes", "starts", "unknown"):
                if not row[key].isascii() or not row[key].isdecimal():
                    raise ValueError(f"row {line}: {key} must be a nonnegative integer")
                row[key] = int(row[key])
            if row["successes"] + row["unknown"] > row["starts"]:
                raise ValueError(f"row {line}: successes plus unknown exceeds starts")
            if row["unknown"] or row["mature"] != "yes" or row["quality"] != "verified":
                raise ValueError(f"row {line}: complete, mature, verified observations are required")
            rows.append(row)
    return rows


def summarize(rows):
    k = len(rows)
    if k < 2:
        raise ValueError("each arm needs at least two players for this variance formula")
    successes = sum(row["successes"] for row in rows)
    starts = sum(row["starts"] for row in rows)
    if starts == 0:
        raise ValueError("each arm needs a positive total number of starts")
    mean_s, mean_n = Fraction(successes, k), Fraction(starts, k)
    ratio = Fraction(successes, starts)
    residuals = [row["successes"] - ratio * row["starts"] for row in rows]
    residual_sum = sum(residuals, Fraction())
    residual_ss = sum((u * u for u in residuals), Fraction())
    residual_var = residual_ss / (k - 1)
    variance = residual_var / (k * mean_n * mean_n)
    s_var = sum(((row["successes"] - mean_s) ** 2 for row in rows), Fraction()) / (k - 1)
    n_var = sum(((row["starts"] - mean_n) ** 2 for row in rows), Fraction()) / (k - 1)
    covariance = sum(((row["successes"] - mean_s) * (row["starts"] - mean_n) for row in rows), Fraction()) / (k - 1)
    expanded_var = (s_var - 2 * ratio * covariance + ratio * ratio * n_var) / (k * mean_n * mean_n)
    if residual_sum != 0 or expanded_var != variance:
        raise ArithmeticError("residual and covariance arithmetic disagree")
    return {
        "players": k,
        "total_successes": successes,
        "total_starts": starts,
        "zero_start_players": sum(row["starts"] == 0 for row in rows),
        "zero_start_fraction": Fraction(sum(row["starts"] == 0 for row in rows), k),
        "mean_successes": mean_s,
        "mean_starts": mean_n,
        "ratio": ratio,
        "maximum_player_start_share": Fraction(max(row["starts"] for row in rows), starts),
        "residuals": [{"player": row["player"], "value": u} for row, u in zip(rows, residuals)],
        "residual_sum": residual_sum,
        "residual_sum_squares": residual_ss,
        "residual_sample_variance": residual_var,
        "success_sample_variance": s_var,
        "start_sample_variance": n_var,
        "success_start_sample_covariance": covariance,
        "ratio_variance_plugin": variance,
        "ratio_variance_covariance_check": expanded_var,
    }


def compute(rows):
    groups = {arm: summarize([row for row in rows if row["arm"] == arm]) for arm in ("C", "T")}
    difference = groups["T"]["ratio"] - groups["C"]["ratio"]
    variance = sum((groups[arm]["ratio_variance_plugin"] for arm in ("C", "T")), Fraction())
    return {
        "scope": "Arithmetic only; no coverage calibration, significance test, or launch decision",
        "model_required": "Independent iid player potential-outcome vectors and outcome-independent simple assignment; not finite-population exact randomization variance",
        "groups": groups,
        "comparison": {
            "T_minus_C": difference,
            "difference_percentage_points": 100 * difference,
            "variance_plugin": variance,
            "standard_error_plugin": math.sqrt(float(variance)),
            "standard_error_percentage_points": 100 * math.sqrt(float(variance)),
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("ledger", help="CSV in the documented player-ledger format")
    args = parser.parse_args()
    try:
        output = compute(load_ledger(args.ledger))
        print(json.dumps(output, ensure_ascii=False, indent=2, default=str))
    except (OSError, ValueError, ArithmeticError) as exc:
        print(f"Cannot compute: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
