from __future__ import annotations

import re
from typing import Dict, List, Tuple, Iterable, Set
import random
import ast
try:
    # Optional formatting to normalize tabs/whitespace and optionally autopep8
    from LLM_Collab_Code_Completion.utils.formatting import (
        normalize_code_for_syntax,
    )
except Exception:  # pragma: no cover
    normalize_code_for_syntax = None  # type: ignore


def _find_class_block(lines: List[str], class_name: str) -> Tuple[int, int, int]:
    """Locate the class block by name.

    Returns (class_start_index, class_end_index_exclusive, class_indent_spaces)
    class_start_index points to the 'class <name>:' line.
    The end is the first line after the class whose indentation is less than or equal to class indent.
    """
    pat = re.compile(rf"^\s*class\s+{re.escape(class_name)}\s*:\s*")
    start = -1
    for i, line in enumerate(lines):
        if pat.match(line):
            start = i
            break
    if start == -1:
        return -1, -1, 0

    # class indent is indentation of next non-empty line after the class header
    class_indent = None
    for j in range(start + 1, len(lines)):
        s = lines[j]
        if not s.strip():
            continue
        indent = len(s) - len(s.lstrip(" "))
        class_indent = indent
        break
    if class_indent is None:
        class_indent = 4  # assume one indent

    # Find end of class block
    end = len(lines)
    for k in range(start + 1, len(lines)):
        s = lines[k]
        if not s.strip():
            continue
        indent = len(s) - len(s.lstrip(" "))
        # class ends when indentation drops to less than class indent and not a decorator/continuation
        if indent < class_indent and not s.lstrip().startswith("@"):
            end = k
            break
    return start, end, class_indent


def _find_method_region(lines: List[str], class_start: int, class_end: int, class_indent: int, method_name: str) -> Tuple[int, int, int]:
    """Find region of a method inside the class, including contiguous decorators above it.

    Returns (start_idx, end_idx, def_indent_spaces), where start_idx points to the first
    decorator line ("@...") if present, otherwise the 'def <name>(' line. If not found,
    returns (-1, -1, class_indent+4).
    """
    pat = re.compile(r'^\s*def\s+' + re.escape(method_name) + r'\s*\(')
    start = -1
    def_indent = class_indent
    for i in range(class_start + 1, class_end):
        line = lines[i]
        if pat.match(line):
            start = i
            def_indent = len(line) - len(line.lstrip(" "))
            # Extend region upward to include contiguous decorators directly above
            j = i - 1
            while j > class_start:
                s = lines[j]
                if not s.lstrip().startswith("@"):
                    break
                start = j
                j -= 1
            break
    if start == -1:
        return -1, -1, class_indent + 4
    # find end: next def at same indentation or end of class
    end = class_end
    for j in range(start + 1, class_end):
        s = lines[j]
        if re.match(r"^\s*def\s+[A-Za-z_]", s):
            indent = len(s) - len(s.lstrip(" "))
            if indent == def_indent:
                end = j
                break
    return start, end, def_indent


def _indent_block(block: str, indent_spaces: int) -> List[str]:
    pad = " " * indent_spaces
    out: List[str] = []
    for line in block.splitlines():
        if line.strip():
            out.append(pad + line)
        else:
            out.append(line)
    if out and not out[-1].endswith("\n"):
        # ensure trailing newline when joining into code
        pass
    return out


def merge_methods_into_skeleton(skeleton: str, class_name: str, method_to_code: Dict[str, str]) -> str:
    """Replace method stubs in skeleton with provided implementations.

    The provided function sources should start with 'def <name>(' at column 0.
    """
    if not method_to_code:
        return skeleton
    lines = skeleton.splitlines()
    cstart, cend, cindent = _find_class_block(lines, class_name)
    if cstart < 0 or cend < 0:
        return skeleton

    # For deterministic replacements, process methods in the order they appear
    order: List[Tuple[int, str]] = []
    for m in method_to_code.keys():
        s, e, d = _find_method_region(lines, cstart, cend, cindent, m)
        order.append((s if s >= 0 else 10**9, m))
    order.sort()

    offset = 0
    for _, m in order:
        impl = method_to_code.get(m, None)
        if not impl:
            continue
        # Recompute positions on current lines with offset
        cstart2, cend2, cindent2 = _find_class_block(lines, class_name)
        s, e, dindent = _find_method_region(lines, cstart2, cend2, cindent2, m)
        if s < 0:
            # Append at end of class (before class end)
            insert_at = cend2
            new_block = _indent_block(impl.strip(), cindent2 + 4)
            lines[insert_at:insert_at] = new_block + [""]
            continue
        new_block = _indent_block(impl.strip(), dindent)
        lines[s:e] = new_block
    merged = "\n".join(lines)
    # Ensure a trailing newline like original behavior
    if not merged.endswith("\n"):
        merged = merged + "\n"
    # Apply lenient normalization/formatting if available
    if normalize_code_for_syntax is not None:
        formatted = normalize_code_for_syntax(merged, use_autopep8=True)  # type: ignore
        if isinstance(formatted, str) and formatted:
            # Preserve trailing newline
            if not formatted.endswith("\n"):
                formatted = formatted + "\n"
            return formatted
    return merged


def _is_syntax_ok(snippet: str) -> bool:
    """Lightweight syntax check for a standalone function snippet.

    Expects `snippet` to start with 'def <name>(' at column 0.
    """
    try:
        # Using ast.parse avoids executing anything and is sufficient for syntax.
        ast.parse(snippet)
        return True
    except Exception:
        return False


def build_method_map_with_syntax_selection(
    agent_texts: List[str],
    method_names: Iterable[str],
    partition: Dict[str, int],
    self_select: bool,
) -> Dict[str, str]:
    """Collect method snippets from agents and, for duplicates, choose syntactically valid ones.

    - Aggregates candidate snippets per method from each agent according to allowed sets:
        * If self_select is True: each agent may contribute to any method in `method_names`.
        * Otherwise: each agent may only contribute methods assigned to it by `partition`.
    - For a given method, keeps only candidates that pass a syntax check (ast.parse).
    - If multiple syntactically valid candidates exist, picks one uniformly at random.
    - If none are valid for a method, that method is omitted (skeleton stub remains).
    """
    from LLM_Collab_Code_Completion.utils.parse_completion import extract_method_snippets

    mset: Set[str] = set(method_names or [])
    if not agent_texts or not mset:
        return {}

    # Gather candidates: name -> list of code snippets
    candidates: Dict[str, List[str]] = {m: [] for m in mset}

    for agent_idx, comp_text in enumerate(agent_texts):
        try:
            text = comp_text or ""
        except Exception:
            text = ""
        if self_select:
            allowed = set(mset)
        else:
            allowed = {m for m, a in partition.items() if a == agent_idx and m in mset}
        if not allowed:
            continue
        try:
            snippets = extract_method_snippets(text, allowed_methods=allowed)
        except Exception:
            snippets = {}
        for name, code in (snippets or {}).items():
            if name in candidates:
                candidates[name].append(code)

    # Select per method: prefer syntactically valid, random among valids
    selected: Dict[str, str] = {}
    for name, opts in candidates.items():
        if not opts:
            continue
        valid_opts = [s for s in opts if _is_syntax_ok(s)]
        if valid_opts:
            chosen = random.choice(valid_opts)
            selected[name] = chosen
        else:
            # No syntactically valid option; omit to keep skeleton stub
            continue

    return selected
