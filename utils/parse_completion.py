from __future__ import annotations

import re
from typing import Dict, Iterable, Set


def _strip_code_fences(text: str) -> str:
    s = (text or "").replace("\r\n", "\n").strip()
    if "```" in s:
        # take the first code fence content
        start = s.find("```")
        if start != -1:
            start += 3
            nl = s.find("\n", start)
            if nl == -1:
                return ""
            body_start = nl + 1
            end = s.find("```", body_start)
            if end != -1:
                return s[body_start:end].strip()
            return s[body_start:].strip()
    return s


def extract_method_snippets(text: str, allowed_methods: Iterable[str]) -> Dict[str, str]:
    """Extract 'def <name>(...)' blocks for allowed method names from a free-form text.

    Returns a mapping: method_name -> function_source
    The returned function_source begins with 'def <name>(' at indentation 0.
    """
    allowed: Set[str] = set(allowed_methods or [])
    if not allowed:
        return {}
    s = _strip_code_fences(text or "")
    lines = s.splitlines()

    out: Dict[str, str] = {}
    i = 0
    while i < len(lines):
        line = lines[i]
        m = re.match(r"^\s*def\s+([A-Za-z_][A-Za-z0-9_]*)\s*\(.*", line)
        if not m:
            i += 1
            continue
        name = m.group(1)
        if name not in allowed:
            i += 1
            continue
        # capture until next top-level def or EOF
        start = i
        j = i + 1
        while j < len(lines):
            if re.match(r"^\s*def\s+[A-Za-z_]", lines[j]):
                break
            j += 1
        block = "\n".join(l.rstrip() for l in lines[start:j]).strip()
        # normalize to no leading indentation on the 'def'
        block = re.sub(r"^\s+def", "def", block)
        out[name] = block
        i = j
    return out

