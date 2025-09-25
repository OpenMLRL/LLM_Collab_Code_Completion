#!/usr/bin/env python3
"""
Export the first 10 samples of `FudanSELab/ClassEval` to a Markdown file,
wrapping code-like fields in triple backtick code fences.

Output path: classeval_head.md (same directory as this script)
"""

from __future__ import annotations

import os
import sys
from typing import Any, Mapping, Sequence, Optional


DATASET_NAME = "FudanSELab/ClassEval"
NUM_SAMPLES = 10


def _choose_split(ds_or_dict: Any) -> Any:
    """Return a Dataset object from a DatasetDict by choosing a sensible split.

    Prefers 'train' > 'validation' > 'test' > first available split.
    If `ds_or_dict` is already a Dataset, return it unchanged.
    """
    try:
        keys = list(ds_or_dict.keys())  # type: ignore[assignment]
    except Exception:
        return ds_or_dict

    for k in ("train", "validation", "test"):
        if k in ds_or_dict:
            return ds_or_dict[k]
    return ds_or_dict[keys[0]]


def _write_line(fh, text: str = "") -> None:
    fh.write(text)
    if not text.endswith("\n"):
        fh.write("\n")


def _is_probably_code_field(key: Optional[str]) -> bool:
    if not key:
        return False
    k = key.lower()
    codeish = (
        "code", "skeleton", "test", "import", "statement",
        "snippet", "source", "solution"
    )
    return any(token in k for token in codeish)


def _is_probably_code_content(text: str) -> bool:
    # Heuristic: multiple lines and code-like tokens or indentation
    if not isinstance(text, str):
        return False
    if text.count("\n") >= 1:
        tokens = (
            "def ", "class ", "import ", "return ", "try:", "except",
            "public ", "static ", "void ", "#include", "System.out",
            "printf(", "function ", "=>", "var ", "let ", "package ",
            "fmt.", "{", "}"
        )
        if any(t in text for t in tokens):
            return True
        # Indentation heuristic
        for line in text.splitlines():
            if line.startswith("    ") or line.startswith("\t"):
                return True
    return False


def _write_code_block(fh, text: str, language: str = "") -> None:
    # Write a fenced code block; keep content as-is so real newlines render.
    fence = f"```{language}" if language else "```"
    _write_line(fh, fence)
    fh.write(text)
    if not (text.endswith("\n") or text.endswith("\r\n")):
        fh.write("\n")
    _write_line(fh, "```")


def _render_value_md(fh, value: Any, key: Optional[str] = None, indent: int = 0) -> None:
    pad = " " * indent

    # Strings
    if isinstance(value, str):
        if _is_probably_code_field(key) or _is_probably_code_content(value):
            # _write_code_block(fh, value, language="")
            _write_code_block(fh, value, language="py")  # assume all are python 
        else:
            # Plain text: write as-is, preserving newlines
            for line in value.splitlines(keepends=True):
                fh.write(pad + line)
            if not (value.endswith("\n") or value.endswith("\r\n")):
                fh.write("\n")
        return

    # Mappings
    if isinstance(value, Mapping):
        for k in value:
            _write_line(fh, f"{pad}{k}:")
            _render_value_md(fh, value[k], key=k, indent=indent + 2)
        return

    # Sequences (but not strings handled above)
    if isinstance(value, Sequence):
        for idx, item in enumerate(value):
            _write_line(fh, f"{pad}- item[{idx}]:")
            _render_value_md(fh, item, key=key, indent=indent + 2)
        return

    # Fallback
    _write_line(fh, f"{pad}{value}")


def main() -> int:
    try:
        from datasets import load_dataset  # type: ignore
    except Exception:
        sys.stderr.write(
            "[ERROR] Missing dependency 'datasets'. Install via:\n"
            "  pip install -U datasets\n"
        )
        return 1

    try:
        ds_all = load_dataset(DATASET_NAME)
    except Exception as e:
        sys.stderr.write(f"[ERROR] Failed to load dataset {DATASET_NAME}: {e}\n")
        return 2

    ds = _choose_split(ds_all)

    out_dir = os.path.dirname(os.path.abspath(__file__))
    out_path = os.path.join(out_dir, "classeval_head.md")

    # Determine feature order if available to keep fields consistent
    feature_keys = None
    try:
        feature_keys = list(getattr(ds, "features").keys())  # type: ignore[attr-defined]
    except Exception:
        pass

    n = min(NUM_SAMPLES, len(ds))
    sep_line = "-" * 20

    with open(out_path, "w", encoding="utf-8") as fh:
        _write_line(fh, f"# {DATASET_NAME} — First {n} Samples")
        try:
            split_name = getattr(ds, "split").name  # type: ignore[attr-defined]
        except Exception:
            split_name = "unknown"
        _write_line(fh, f"Split: {split_name}")
        _write_line(fh, f"Total samples in split: {len(ds)}")
        _write_line(fh, "")
        _write_line(fh, sep_line)

        for i in range(n):
            _write_line(fh, f"## Sample {i}")
            example = ds[i]
            keys = feature_keys if feature_keys else list(example.keys())

            for k in keys:
                if k not in example:
                    continue
                _write_line(fh, f"### {k}")
                _render_value_md(fh, example[k], key=k, indent=0)

            if i != n - 1:
                _write_line(fh, sep_line)

    print(f"Wrote {n} samples to: {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

