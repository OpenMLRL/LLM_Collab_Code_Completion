from __future__ import annotations

import ast
import re
from typing import Dict, List


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
    sk = _sanitize_python_source(skeleton)
    class_name = extract_class_name(sk)
    if not class_name:
        return []
    try:
        tree = ast.parse(sk)
    except Exception:
        return []
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


def extract_method_param_counts(skeleton: str) -> Dict[str, int]:
    """Return a mapping of method name -> total parameter count within the primary class.

    Counts all explicit parameters including positional-only, positional/kw, kw-only,
    and treats *args/**kwargs as 1 each when present. The count includes "self"/"cls"
    when they appear in the signature.
    """
    sk = _sanitize_python_source(skeleton)
    class_name = extract_class_name(sk)
    if not class_name:
        return {}
    try:
        tree = ast.parse(sk)
    except Exception:
        return {}

    def _count_args(args: ast.arguments) -> int:
        count = len(getattr(args, "posonlyargs", []) or [])
        count += len(getattr(args, "args", []) or [])
        count += len(getattr(args, "kwonlyargs", []) or [])
        if getattr(args, "vararg", None) is not None:
            count += 1
        if getattr(args, "kwarg", None) is not None:
            count += 1
        return int(count)

    counts: Dict[str, int] = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name == class_name:
            for item in node.body:
                if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    counts[item.name] = _count_args(item.args)
            break
    return counts
