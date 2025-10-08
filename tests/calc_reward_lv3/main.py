"""
Enumerate lv3 values (as implemented in rewards/CE_reward.py) for num_agent=3.

The current lv3 in CE_reward.py is entropy-based over the distribution of
each agent's picks:

    - Let s_i be the number of functions picked by agent i, N the number of agents
    - Let p_i = s_i / sum_j s_j (only where s_i>0; here we enumerate s_i in [1..V])
    - Entropy H = -sum_i p_i ln p_i, normalized H_norm = H / ln(N) (clamped to [0,1])
    - lv3 = 2.8 * H_norm

We enumerate (s1, s2, s3) with s_i in [1..V] and compute lv3 accordingly.
Outputs are sorted by lv3 descending for easier inspection, similar to calc_reward_lv2.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple, Dict
import argparse
import math
import csv
import os


def CalcEntropy(V: int, counts: Iterable[int]) -> float:
    """Compute lv3 (entropy-based balance) for given picks.

    - V is included for signature symmetry but not used directly in lv3.
    - counts must be positive integers in [1..V].
    - Returns lv3 in [0, 2.8].
    """
    s_list = [int(x) for x in counts]
    if any(si <= 0 for si in s_list):
        raise ValueError("counts must all be positive for lv3 enumeration")
    total = float(sum(s_list))
    if total <= 0:
        # In CE_reward this case returns -INF; not reachable here under [1..V]
        return float("nan")
    ps = [si / total for si in s_list if si > 0]
    N = len(ps)
    if N <= 1:
        return 0.0
    H = -sum(p * math.log(p) for p in ps)
    H_norm = H / math.log(N)
    # Clip to [0,1]
    H_norm = max(0.0, min(1.0, H_norm))
    lv3 = 2.8 * H_norm
    return lv3


def enumerate_lv3_for_three_agents(V: int) -> List[Tuple[Tuple[int, int, int], float]]:
    """Enumerate (s1, s2, s3) in [1, V]^3 and compute lv3 for each triple."""
    out: List[Tuple[Tuple[int, int, int], float]] = []
    for s1 in range(1, V + 1):
        for s2 in range(1, V + 1):
            for s3 in range(1, V + 1):
                lv3 = CalcEntropy(V, [s1, s2, s3])
                out.append(((s1, s2, s3), lv3))
    return out


def summarize_by_sum(V: int, rows: List[Tuple[Tuple[int, int, int], float]]) -> Dict[int, Dict[str, float]]:
    """Aggregate enumeration by total S = s1 + s2 + s3.

    For each S, compute count, lv3_min, lv3_max, lv3_avg.
    """
    summary: Dict[int, Dict[str, float]] = {}
    for (s1, s2, s3), lv3 in rows:
        S = s1 + s2 + s3
        e = summary.setdefault(S, {"count": 0, "lv3_min": float("inf"), "lv3_max": float("-inf"), "lv3_sum": 0.0})
        e["count"] += 1
        if lv3 < e["lv3_min"]:
            e["lv3_min"] = lv3
        if lv3 > e["lv3_max"]:
            e["lv3_max"] = lv3
        e["lv3_sum"] += lv3
    # finalize averages
    for S, e in summary.items():
        cnt = int(e["count"])  # type: ignore[arg-type]
        e["lv3_avg"] = e["lv3_sum"] / cnt if cnt > 0 else float("nan")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Enumerate lv3 (entropy) for num_agent=3 over [1..V]")
    parser.add_argument("-V", type=int, default=6, help="Total function count V (upper bound for each agent's picks; default: 6)")
    parser.add_argument("--print-all", action="store_true", help="Print every (s1,s2,s3) with lv3, sorted by lv3 descending")
    parser.add_argument("--csv", type=str, default=None, help="Write all cases to CSV at given path")
    parser.add_argument("--export-range", action="store_true", help="If set with --csv, export for V=3..8 inclusive")
    args = parser.parse_args()

    V = args.V
    rows = enumerate_lv3_for_three_agents(V)

    if args.print_all:
        # Sort by lv3 descending; then by S ascending; then lexicographic
        def _row_key(item):
            (s1, s2, s3), lv3 = item
            return (-lv3, (s1 + s2 + s3), (s1, s2, s3))

        for (s1, s2, s3), lv3 in sorted(rows, key=_row_key):
            print(f"V={V} s=({s1},{s2},{s3}) S={s1+s2+s3} lv3={lv3:.6f}")

    # Always print a compact summary grouped by S
    summary = summarize_by_sum(V, rows)
    print("-- Summary by total S (num_agent=3) --")

    # Sort summary by lv3_max descending (then S asc) for quick view of best-balanced totals
    def _sum_key(item):
        S, e = item
        return (-float(e["lv3_max"]), S)

    for S, e in sorted(summary.items(), key=_sum_key):
        cnt = int(e["count"])  # type: ignore[arg-type]
        print(
            f"S={S:2d}: {cnt} combos, lv3_min={e['lv3_min']:.6f}, lv3_max={e['lv3_max']:.6f}, lv3_avg={e['lv3_avg']:.6f}"
        )

    # Optional CSV export
    if args.csv:
        vs_list = list(range(3, 9)) if args.export_range else [V]
        out_path = os.path.abspath(args.csv)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["V", "s1", "s2", "s3", "S", "lv3"])  # lv3 always defined here
            for v in vs_list:
                for (s1, s2, s3), lv3 in enumerate_lv3_for_three_agents(v):
                    S = s1 + s2 + s3
                    w.writerow([v, s1, s2, s3, S, f"{lv3:.9f}"])
        print(f"CSV written: {out_path}")


if __name__ == "__main__":
    main()
