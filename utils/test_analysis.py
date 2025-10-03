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

    def _is_test_case_base(base: ast.AST) -> bool:
        # Matches: TestCase, unittest.TestCase, pkg.unittest.TestCase, etc.
        if isinstance(base, ast.Name):
            return base.id == "TestCase"
        if isinstance(base, ast.Attribute):
            cur = base
            # Walk rightward attributes: something.something.TestCase
            while isinstance(cur, ast.Attribute):
                if getattr(cur, "attr", None) == "TestCase":
                    return True
                cur = cur.value
            if isinstance(cur, ast.Name) and cur.id == "TestCase":
                return True
        return False

    for n in tree.body:
        if isinstance(n, ast.ClassDef):
            # Robustly accept unittest.TestCase subclasses
            is_test_case = any(_is_test_case_base(base) for base in n.bases)
            if not is_test_case:
                # Fallback: class name contains 'test' (case-insensitive)
                name_l = n.name.lower()
                is_test_case = ("test" in name_l)
            if not is_test_case:
                continue

            for item in n.body:
                if isinstance(item, ast.FunctionDef) and item.name.startswith("test"):
                    acc: Set[str] = set()
                    _collect_calls(item, acc)
                    unittest_id = f"{item.name} (task_module.{n.name})"
                    results[unittest_id] = acc

    return results
