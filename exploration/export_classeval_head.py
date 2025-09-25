#!/usr/bin/env python3
"""
Load the Hugging Face dataset `FudanSELab/ClassEval` and write the first
10 samples to a file in the same directory. Samples are separated by a line
of `=` characters. Strings are written as-is to preserve real newlines.

If the dataset has multiple splits, this script prefers `train`, then
`validation`, then `test`, otherwise the first available split.
"""

from __future__ import annotations

import os
import sys
from typing import Any, Mapping, Sequence


def _choose_split(ds_or_dict: Any) -> Any:
    """Return a Dataset object from a DatasetDict by choosing a sensible split.

    Prefers 'train' > 'validation' > 'test' > first available split.
    If `ds_or_dict` is already a Dataset, return it unchanged.
    """
    try:
        # DatasetDict-like: has `.keys()` and item access
        keys = list(ds_or_dict.keys())  # type: ignore[assignment]
    except Exception:
        return ds_or_dict

    for k in ("train", "validation", "test"):
        if k in ds_or_dict:
            return ds_or_dict[k]
    return ds_or_dict[keys[0]]


def _write_line(fh, text: str = "") -> None:
    """Write a line to file, ensuring newline termination."""
    fh.write(text)
    if not text.endswith("\n"):
        fh.write("\n")


def _render_value(fh, value: Any, indent: int = 0) -> None:
    """Render a value recursively without escaping newlines in strings.

    - Strings: written as-is (so "\n" becomes an actual newline if present).
    - Sequences (lists/tuples): each item on its own line, indented.
    - Mappings (dict-like): key on one line, value below, indented.
    - Others: converted with str().
    """
    pad = " " * indent

    # Avoid treating strings as sequences
    if isinstance(value, str):
        # Write the string as-is so that real newlines render as empty lines.
        # Do not escape newlines, per the user's requirement.
        for line in value.splitlines(keepends=True):
            # Each line may already end with a newline; write directly.
            fh.write(pad + line)
        # Ensure trailing newline if value didn't end with one
        if not (value.endswith("\n") or value.endswith("\r\n")):
            fh.write("\n")
        return

    # Mappings
    if isinstance(value, Mapping):
        for k in value:
            _write_line(fh, f"{pad}{k}:")
            _render_value(fh, value[k], indent=indent + 2)
        return

    # Sequences (but not strings handled above)
    if isinstance(value, Sequence):
        for idx, item in enumerate(value):
            _write_line(fh, f"{pad}- item[{idx}]:")
            _render_value(fh, item, indent=indent + 2)
        return

    # Fallback: plain text
    _write_line(fh, f"{pad}{value}")


def main() -> int:
    dataset_name = "FudanSELab/ClassEval"
    num_samples = 10

    try:
        from datasets import load_dataset  # type: ignore
    except Exception as e:
        sys.stderr.write(
            "[ERROR] Missing dependency 'datasets'. Install via:\n"
            "  pip install -U datasets\n"
        )
        return 1

    try:
        # `trust_remote_code` is no longer supported in recent datasets versions.
        # Load as a standard dataset.
        ds_all = load_dataset(dataset_name)
    except Exception as e:
        sys.stderr.write(f"[ERROR] Failed to load dataset {dataset_name}: {e}\n")
        return 2

    ds = _choose_split(ds_all)

    # Output path in the same directory as this script
    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "classeval_head.txt")

    # Determine feature order if available to keep fields consistent
    feature_keys = None
    try:
        feature_keys = list(getattr(ds, "features").keys())  # type: ignore[attr-defined]
    except Exception:
        pass

    n = min(num_samples, len(ds))
    sep_line = "=" * 80

    with open(out_path, "w", encoding="utf-8") as fh:
        _write_line(fh, f"Dataset: {dataset_name}")
        try:
            split_name = getattr(ds, "split").name  # type: ignore[attr-defined]
        except Exception:
            split_name = "unknown"
        _write_line(fh, f"Split: {split_name}")
        _write_line(fh, f"Total samples in split: {len(ds)}")
        _write_line(fh, sep_line)

        for i in range(n):
            example = ds[i]
            _write_line(fh, f"Index: {i}")

            keys = feature_keys if feature_keys else list(example.keys())
            for k in keys:
                if k not in example:
                    continue
                _write_line(fh, f"{k}:")
                _render_value(fh, example[k], indent=2)

            if i != n - 1:
                _write_line(fh, sep_line)

    print(f"Wrote {n} samples to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
