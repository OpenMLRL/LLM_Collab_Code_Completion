"""
Enumerate lv2 values (as defined in rewards/CE_reward.py) for num_agent=3.

For a given V (number of total functions in the class), each agent i picks
an integer s_i in [1, V] denoting how many functions they generate. We set
S = sum_i s_i and compute

    lv2(S) = 2 - 4 * ((S - V)^2) / V^2,  for 0 <= S <= 2V

If S > 2V, the original reward design terminates the sample early with a
hard penalty, so in this enumeration we mark those cases as "TERMINATE".

Function entry point is named CalcEntropy per request.
"""

from __future__ import annotations

from typing import Iterable, List, Tuple, Dict, Optional
import argparse
import csv
import os


def CalcEntropy(V: int, counts: Iterable[int]) -> Optional[float]:
    """Compute lv2 according to current design in rewards/CE_reward.py.

    - V: total number of functions in the class (V > 0)
    - counts: iterable of agent pick counts (e.g., [s1, s2, s3])
    - Returns lv2 in [-2, 2] when sum(counts) <= 2V; otherwise None to indicate
      early termination in the original reward logic.
    """
    V = int(V)
    s_list = [int(x) for x in counts]
    if V <= 0:
        raise ValueError("V must be positive")
    if any(si < 0 for si in s_list):
        raise ValueError("counts must be non-negative")

    S = sum(s_list)
    if S > 2 * V:
        return None  # early termination in CE_reward

    dv = float(S) - float(V)
    lv2 = 2.0 - 4.0 * (dv * dv) / (float(V) * float(V))
    # numerical guard to keep in [-2, 2]
    if lv2 > 2.0:
        lv2 = 2.0
    if lv2 < -2.0:
        lv2 = -2.0
    return lv2


def enumerate_lv2_for_three_agents(V: int) -> List[Tuple[Tuple[int, int, int], Optional[float]]]:
    """Enumerate (s1, s2, s3) in [1, V]^3 and compute lv2 for each triple.

    Returns a list of ((s1, s2, s3), lv2_or_None) where None denotes
    early termination (S > 2V).
    """
    out: List[Tuple[Tuple[int, int, int], Optional[float]]] = []
    for s1 in range(1, V + 1):
        for s2 in range(1, V + 1):
            for s3 in range(1, V + 1):
                lv2 = CalcEntropy(V, [s1, s2, s3])
                out.append(((s1, s2, s3), lv2))
    return out


def summarize_by_sum(V: int, rows: List[Tuple[Tuple[int, int, int], Optional[float]]]) -> Dict[int, Dict[str, float]]:
    """Aggregate enumeration by total S = s1 + s2 + s3.

    Returns a dict mapping S -> { 'count': int, 'terminates': int, 'lv2': float }
    where 'lv2' is the unique lv2 value for this S (it only depends on S and V).
    """
    summary: Dict[int, Dict[str, float]] = {}
    for (s1, s2, s3), lv2 in rows:
        S = s1 + s2 + s3
        entry = summary.setdefault(S, {"count": 0, "terminates": 0, "lv2": 0.0})
        entry["count"] += 1
        if lv2 is None:
            entry["terminates"] += 1
        else:
            entry["lv2"] = lv2
    return summary


def main():
    parser = argparse.ArgumentParser(description="Enumerate lv2 for num_agent=3 over [1..V]")
    parser.add_argument("-V", type=int, default=6, help="Total function count V (default: 6)")
    parser.add_argument("--print-all", action="store_true", help="Print every (s1,s2,s3) with lv2/TERMINATE")
    parser.add_argument("--csv", type=str, default=None, help="Write all cases to CSV at given path")
    parser.add_argument("--export-range", action="store_true", help="If set with --csv, export for V=3..8 inclusive")
    args = parser.parse_args()

    V = args.V
    rows = enumerate_lv2_for_three_agents(V)

    if args.print_all:
        # Sort detailed rows by lv2 descending; TERMINATE (None) goes last
        def _row_key(item):
            (s1, s2, s3), lv2 = item
            numeric = lv2 if lv2 is not None else float('-inf')
            # Desc by lv2, then asc by S, then lexicographic tuple
            return (-numeric, (s1 + s2 + s3), (s1, s2, s3))

        for (s1, s2, s3), lv2 in sorted(rows, key=_row_key):
            status = "TERMINATE" if lv2 is None else f"{lv2:.6f}"
            print(f"V={V} s=({s1},{s2},{s3}) S={s1+s2+s3} lv2={status}")

    # Always print a compact summary grouped by S
    summary = summarize_by_sum(V, rows)
    print("-- Summary by total S (num_agent=3) --")
    # Sort summary by lv2 descending; S with all-terminate go last
    def _sum_key(item):
        S, info = item
        term = int(info["terminates"])  # type: ignore[arg-type]
        cnt = int(info["count"])        # type: ignore[arg-type]
        if term == cnt:
            numeric = float('-inf')
        else:
            numeric = float(info["lv2"])  # type: ignore[arg-type]
        return (-numeric, S)

    for S, info in sorted(summary.items(), key=_sum_key):
        term = int(info["terminates"])  # type: ignore[arg-type]
        cnt = int(info["count"])        # type: ignore[arg-type]
        if term == cnt:
            print(f"S={S:2d}: all {cnt} combos -> TERMINATE (S>2V)")
        else:
            print(f"S={S:2d}: {cnt} combos, {term} terminate, lv2={info['lv2']:.6f}")

    # Optional CSV export
    if args.csv:
        vs_list = list(range(3, 9)) if args.export_range else [V]
        out_path = os.path.abspath(args.csv)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", newline="", encoding="utf-8") as fh:
            w = csv.writer(fh)
            w.writerow(["V", "s1", "s2", "s3", "S", "lv2", "terminate"])  # terminate: 1 if S>2V
            for v in vs_list:
                for (s1, s2, s3), lv2 in enumerate_lv2_for_three_agents(v):
                    S = s1 + s2 + s3
                    term = 1 if lv2 is None else 0
                    val = "" if lv2 is None else f"{lv2:.9f}"
                    w.writerow([v, s1, s2, s3, S, val, term])
        print(f"CSV written: {out_path}")


if __name__ == "__main__":
    main()
