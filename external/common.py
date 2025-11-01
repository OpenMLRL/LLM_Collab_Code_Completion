from __future__ import annotations

import textwrap
from typing import List, Tuple, Optional


def build_agent_context_block(
    skeleton: str,
    class_name: str,
    assigned_methods: List[str] | None,
) -> str:
    """Base context/instructions block for ClassEval agents.

    - Includes the skeleton
    - Lists methods assigned to this agent (if provided)
    - States strict output rules for ClassEval
    """
    assigned_methods = list(assigned_methods or [])
    assigned_text = "\n".join(f"- {m}" for m in assigned_methods) if assigned_methods else "(none)"

    ctx = textwrap.dedent(
        f"""
        You are collaborating to complete the Python class '{class_name}'.

        Below is the full class skeleton. Your responsibility is to implement ONLY these methods:
        {assigned_text}

        Output rules (strict):
        - Output ONLY Python function definitions for your target methods.
        - Do NOT output the class header or any imports.
        - Do NOT include markdown code fences or extra text.
        - Use the exact signatures from the skeleton (names, parameters, type hints, defaults, and decorators).
        - Implement real, runnable logic; do not leave placeholders.

        SKELETON START
        {skeleton.strip()}
        SKELETON END
        """
    ).strip()
    return ctx


def build_take_job_context_block(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    num_agents: int,
) -> str:
    """Context block for TAKE_JOB strategy (self‑select subset of methods)."""
    mlist = list(method_names or [])
    total = len(mlist)
    brace = "{" + ", ".join(mlist) + "}" if mlist else "{}"
    target = (total + max(1, num_agents) - 1) // max(1, num_agents) if total > 0 else 0
    ctx = textwrap.dedent(
        f"""
        You are one of {num_agents} collaborating agents tasked with implementing methods of class '{class_name}'.

        Choose a non‑empty proper subset of {brace} (not all methods). Aim for ~{target} methods to balance workload.

        Output rules (strict):
        - Output ONLY the chosen methods as Python function definitions, in a single contiguous block (no prose).
        - Do NOT output the class header/imports, do NOT add extra helpers.
        - Use the exact signatures from the skeleton (including decorators).
        - Implement executable logic; no placeholders.

        SKELETON START
        {skeleton.strip()}
        SKELETON END
        """
    ).strip()
    return ctx


def join_previous_impls(snippets: List[str]) -> str:
    if not snippets:
        return "<no implementation found>"
    body = "\n\n".join((s or "").strip() for s in snippets if s and s.strip())
    return body if body else "<no implementation found>"


def render_history_block_for_agent(
    agent_idx: int,
    *,
    prompt_history_per_agent: Optional[List[List[str]]] = None,
    response_history_per_agent: Optional[List[List[str]]] = None,
) -> str:
    """Render a readable history block for one agent.

    - Lists all previous prompts for that agent (Turn 1..T)
    - Lists all previous responses for that agent (Turn 1..T)
    Returns an empty string if there is no history.
    """
    lines: List[str] = []
    if prompt_history_per_agent and 0 <= agent_idx < len(prompt_history_per_agent):
        ph = prompt_history_per_agent[agent_idx] or []
        if ph:
            lines.append("History: previous prompts:")
            for t, p in enumerate(ph, start=1):
                lines.append(f"- Turn {t} prompt:\n{p}")
            lines.append("")
    if response_history_per_agent and 0 <= agent_idx < len(response_history_per_agent):
        rh = response_history_per_agent[agent_idx] or []
        if rh:
            lines.append("History: your previous responses:")
            for t, r in enumerate(rh, start=1):
                lines.append(f"- Turn {t} response:\n{r}")
            lines.append("")
    return "\n".join(lines).rstrip()
