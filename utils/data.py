from __future__ import annotations

import random
import re
from typing import Any, Dict, Iterable, List, Mapping, Sequence, Tuple


def _sanitize_python_source(text: str) -> str:
    """Normalize common Unicode punctuation to ASCII to avoid AST parse failures.

    This handles smart quotes and a few whitespace/punctuation variants often found
    in datasets. It is a conservative transformation and should not change semantics.
    """
    if not isinstance(text, str) or not text:
        return text
    translation = {
        ord("\u201C"): '"',  # left double smart quote
        ord("\u201D"): '"',  # right double smart quote
        ord("\u2018"): "'",  # left single smart quote
        ord("\u2019"): "'",  # right single smart quote
        ord("\u2013"): "-",  # en dash
        ord("\u2014"): "-",  # em dash
        ord("\u2026"): "...",  # ellipsis
        ord("\u00A0"): " ",  # non-breaking space
        ord("\u200B"): None,  # zero width space → remove
    }
    return text.translate(translation)


def dataset_train_eval_split(ds_all: Any, split_ratio: float = 0.8, seed: int = 42):
    """Return (train, eval) Dataset objects from a datasets.Dataset or DatasetDict.

    Strategy:
    - If ds_all is a DatasetDict, prefer a single representative split (train|validation|test|first)
      then perform a random train_test_split based on split_ratio for stability.
    - If ds_all is already a Dataset, split it directly.
    """
    try:
        # DatasetDict path
        keys = list(ds_all.keys())  # type: ignore[attr-defined]
        preferred = None
        for k in ("train", "validation", "test"):
            if k in ds_all:
                preferred = k
                break
        if preferred is None and keys:
            preferred = keys[0]
        base = ds_all[preferred]
    except Exception:
        # Assume already a Dataset
        base = ds_all

    # Use huggingface train_test_split for reproducibility
    test_size = max(0.0, min(1.0, 1.0 - float(split_ratio)))
    try:
        split = base.train_test_split(test_size=test_size or 0.0001, seed=int(seed))
        return split["train"], split["test"]
    except Exception:
        # Fallback: manual slicing
        n = len(base)
        idxs = list(range(n))
        rnd = random.Random(int(seed))
        rnd.shuffle(idxs)
        k = int(n * float(split_ratio))
        train_idx = idxs[:k]
        eval_idx = idxs[k:]
        return base.select(train_idx), base.select(eval_idx)


def extract_class_name(skeleton: str) -> str | None:
    """Extract the first class name from skeleton."""
    sk = _sanitize_python_source(skeleton)
    m = re.search(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)\s*:\s*", sk)
    return m.group(1) if m else None


def extract_incomplete_methods(skeleton: str) -> List[str]:
    """Heuristically extract method names within the primary class that require completion.

    We consider a method incomplete if its body is empty, only has a docstring, contains only 'pass',
    or raises NotImplementedError.
    """
    try:
        import ast
    except Exception:
        # Fallback: simple regex for 'def name(' within the first class block
        methods = []
        in_class = False
        for line in skeleton.splitlines():
            if line.strip().startswith("class "):
                in_class = True
            if in_class and line.lstrip().startswith("def "):
                name = line.strip().split()[1].split("(")[0]
                methods.append(name)
        return methods

    sk = _sanitize_python_source(skeleton)
    class_name = extract_class_name(sk)
    if not class_name:
        return []
    try:
        tree = ast.parse(sk)
    except Exception:
        # Fallback: simple regex for 'def name(' within the first class block
        methods = []
        in_class = False
        for line in sk.splitlines():
            if line.strip().startswith("class ") and class_name in line:
                in_class = True
                continue
            if in_class and line.lstrip().startswith("def "):
                name = line.strip().split()[1].split("(")[0]
                methods.append(name)
        return methods
    targets: List[str] = []
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, ast.FunctionDef):
                    body = item.body or []
                    # Remove leading docstring expr if present
                    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Str):
                        body = body[1:]
                    # Empty body or only 'pass'
                    if not body:
                        targets.append(item.name)
                        continue
                    if len(body) == 1 and isinstance(body[0], ast.Pass):
                        targets.append(item.name)
                        continue
                    # Single raise NotImplementedError
                    if (
                        len(body) == 1
                        and isinstance(body[0], ast.Raise)
                        and isinstance(getattr(body[0], "exc", None), ast.Call)
                        and getattr(body[0].exc.func, "id", None) == "NotImplementedError"
                    ):
                        targets.append(item.name)
                        continue
            break
    return targets


def get_method_partition_for_example(
    mode: str,
    methods: Sequence[str],
    num_agents: int,
    seed: int,
    task_id: str | None = None,
) -> Dict[str, int]:
    """Provide a simple deterministic partition for legacy consumers."""
    return {}
