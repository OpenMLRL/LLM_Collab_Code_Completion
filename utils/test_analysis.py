from __future__ import annotations

import ast
from typing import Dict, Iterable, Set


def methods_called_per_test(test_code: str, candidate_methods: Iterable[str], class_name: str | None) -> Dict[str, Set[str]]:
    """Heuristically extract, for each unittest test method, the set of method names called
    that belong to the target class. Returns a mapping from unittest ID string
    (e.g., 'test_xxx (task_module.TestClass)') to a set of method names.
    """
    methods: Set[str] = set(candidate_methods or [])
    if not test_code or not methods:
        return {}

    try:
        tree = ast.parse(test_code)
    except Exception:
        return {}

    results: Dict[str, Set[str]] = {}

    def _collect_calls(node: ast.AST, acc: Set[str]):
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                func = child.func
                # obj.method(...)
                if isinstance(func, ast.Attribute):
                    name = func.attr
                    if name in methods:
                        acc.add(name)
                # Direct function call unlikely for methods, ignore
        return acc

    for n in tree.body:
        if isinstance(n, ast.ClassDef):
            # Only heuristically accept classes that look like TestCases
            is_test_case = any(
                (getattr(base, "id", None) == "TestCase" or getattr(getattr(base, "attr", None), "attr", None) == "TestCase")
                or (getattr(base, "attr", None) and getattr(base.attr, "id", None) == "TestCase")
                for base in n.bases
            )
            if not is_test_case:
                # also accept class names starting with Test*
                is_test_case = n.name.lower().startswith("test") or n.name.lower().endswith("test")
            if not is_test_case:
                continue

            for item in n.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith("test"):
                    acc: Set[str] = set()
                    _collect_calls(item, acc)
                    unittest_id = f"{item.name} (task_module.{n.name})"
                    results[unittest_id] = acc

    return results

