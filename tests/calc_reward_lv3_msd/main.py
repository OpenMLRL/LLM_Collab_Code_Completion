"""
Enumerate alternative lv3 values (MSD-based) for num_agent=3.

Definition (matching the requested design):
    - N = number of agents
    - t = V / N
    - s_i = picks of agent i
    - msd = (1/N) * sum_i (s_i - t)^2
    - msd_max = (1/N) * V^2 * (1 - 1/N)
    - lv3 = 4 * max(0, 1 - msd / (msd_max + eps)) - 2

Range: lv3 in [-2, 2]. Higher means better balance around the target V/N.

This script mirrors calc_reward_lv3 (entropy) tool: supports printing sorted
enumerations and CSV export for V=3..8, or a specific V.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple, Dict
import argparse
import csv
import math
import os


def CalcMSD(V: int, counts: Iterable[int], num_agents: int = 3) -> float:
    """Compute lv3 by MSD-based formula.

    Args:
        V: total functions in class
        counts: iterable of agent pick counts (e.g., [s1, s2, s3])
        num_agents: number of agents (default 3)

    Returns:
        lv3 value in [-2, 2].
    """
    s_list = [float(int(x)) for x in counts]
    N = int(num_agents) if num_agents > 0 else 1
    t = float(V) / float(N)
    msd = (sum((si - t) ** 2 for si in s_list) / float(N)) if N > 0 else 0.0
    msd_max = (1.0 / float(N)) * (float(V) ** 2) * (1.0 - 1.0 / float(N)) if N > 0 else 0.0
    eps = 1e-8
    ratio = 0.0 if msd_max <= 0 else (msd / (msd_max + eps))
    lv3 = 4.0 * max(0.0, 1.0 - ratio) - 2.0
    # Clamp to [-2, 2]
    if lv3 > 2.0:
        lv3 = 2.0
    if lv3 < -2.0:
        lv3 = -2.0
    return lv3


def enumerate_lv3_msd_for_three_agents(V: int) -> List[Tuple[Tuple[int, int, int], float]]:
    out: List[Tuple[Tuple[int, int, int], float]] = []
    for s1 in range(1, V + 1):
        for s2 in range(1, V + 1):
            for s3 in range(1, V + 1):
                lv3 = CalcMSD(V, [s1, s2, s3], num_agents=3)
                out.append(((s1, s2, s3), lv3))
    return out


def summarize_by_sum(V: int, rows: List[Tuple[Tuple[int, int, int], float]]) -> Dict[int, Dict[str, float]]:
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
    for S, e in summary.items():
        cnt = int(e["count"])  # type: ignore[arg-type]
        e["lv3_avg"] = e["lv3_sum"] / cnt if cnt > 0 else float("nan")
    return summary


def main():
    parser = argparse.ArgumentParser(description="Enumerate lv3 (MSD-based) for num_agent=3 over [1..V]")
    parser.add_argument("-V", type=int, default=6, help="Total function count V (upper bound for each agent's picks; default: 6)")
    parser.add_argument("--print-all", action="store_true", help="Print every (s1,s2,s3) with lv3, sorted by lv3 descending")
    parser.add_argument("--csv", type=str, default=None, help="Write all cases to CSV at given path")
    parser.add_argument("--export-range", action="store_true", help="If set with --csv, export for V=3..8 inclusive")
    args = parser.parse_args()

    V = args.V
    rows = enumerate_lv3_msd_for_three_agents(V)

    if args.print_all:
        def _row_key(item):
            (s1, s2, s3), lv3 = item
            return (-lv3, (s1 + s2 + s3), (s1, s2, s3))

        for (s1, s2, s3), lv3 in sorted(rows, key=_row_key):
            print(f"V={V} s=({s1},{s2},{s3}) S={s1+s2+s3} lv3={lv3:.6f}")

    summary = summarize_by_sum(V, rows)
    print("-- Summary by total S (num_agent=3) --")

    def _sum_key(item):
        S, e = item
        return (-float(e["lv3_max"]), S)

    for S, e in sorted(summary.items(), key=_sum_key):
        cnt = int(e["count"])  # type: ignore[arg-type]
        print(
            f"S={S:2d}: {cnt} combos, lv3_min={e['lv3_min']:.6f}, lv3_max={e['lv3_max']:.6f}, lv3_avg={e['lv3_avg']:.6f}"
        )

    if args.csv:
        vs_list = list(range(3, 9)) if args.export_range else [V]
        out_path = os.path.abspath(args.csv)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["V", "s1", "s2", "s3", "S", "lv3_msd"])  # lv3 (MSD-based)
            for v in vs_list:
                for (s1, s2, s3), lv3 in enumerate_lv3_msd_for_three_agents(v):
                    S = s1 + s2 + s3
                    w.writerow([v, s1, s2, s3, S, f"{lv3:.9f}"])
        print(f"CSV written: {out_path}")


if __name__ == "__main__":
    main()

