from __future__ import annotations

"""Code formatting and normalization utilities.

Provides a lenient normalization function to reduce common syntax issues like
tab/space mixing and inconsistent trailing whitespace, with an optional
autopep8 pass when available.
"""

from typing import Optional


def normalize_code_for_syntax(text: str, use_autopep8: bool = True) -> str:
    """Best-effort normalization for Python source code.

    - Normalize CRLF/CR to LF
    - Expand tabs to 4 spaces
    - Strip trailing whitespace per line
    - Optionally run autopep8 (aggressive=1) if available
    """
    s = text or ""
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = s.expandtabs(4)
    lines = [ln.rstrip() for ln in s.splitlines()]
    s = "\n".join(lines)
    if use_autopep8:
        import autopep8  # type: ignore

        s2 = autopep8.fix_code(s, options={"aggressive": 1})
        if isinstance(s2, str) and s2:
            s = s2
    return s

