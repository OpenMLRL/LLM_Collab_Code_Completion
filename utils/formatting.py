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
    try:
        s = s.replace("\r\n", "\n").replace("\r", "\n")
    except Exception:
        pass
    try:
        s = s.expandtabs(4)
    except Exception:
        pass
    try:
        lines = [ln.rstrip() for ln in s.splitlines()]
        s = "\n".join(lines)
    except Exception:
        pass
    if use_autopep8:
        try:
            import autopep8  # type: ignore

            s2 = autopep8.fix_code(s, options={"aggressive": 1})
            if isinstance(s2, str) and s2:
                s = s2
        except Exception:
            # autopep8 not installed or failed — ignore
            pass
    return s

