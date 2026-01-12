from __future__ import annotations

from typing import Dict, List, Optional
import textwrap

from .common import render_history_block_for_agent


def format_followup_prompts(
    *,
    skeleton: str,
    class_name: str,
    method_names: List[str],
    assignments: Dict[int, List[str]] | None,
    agent_completions: List[str],
    num_agents: int = 2,
    prompt_history_per_agent: Optional[List[List[str]]] = None,
    response_history_per_agent: Optional[List[List[str]]] = None,
) -> List[str]:
    """Plain mode: history + skeleton only (no diagnostics)."""
    n = int(num_agents)
    prompts: List[str] = [""] * n

    if prompt_history_per_agent is None:
        prompt_history_per_agent = [[] for _ in range(n)]
    if response_history_per_agent is None:
        response_history_per_agent = [[] for _ in range(n)]

    skeleton_block = textwrap.dedent(
        f"""
        Class skeleton reference for '{class_name or "unknown"}':
        SKELETON START
        {skeleton.strip()}
        SKELETON END
        """
    ).strip()

    for idx in range(n):
        sections: List[str] = []
        sections.append(
            "Review the history below and revise your implementation. Keep every method signature unchanged."
        )
        hist = render_history_block_for_agent(
            idx,
            prompt_history_per_agent=prompt_history_per_agent,
            response_history_per_agent=response_history_per_agent,
        )
        if hist:
            sections.extend([hist, ""])

        sections.extend([skeleton_block, ""])

        sections.extend(
            [
                "Respond with ONLY your revised implementation enclosed in a single ```python ...``` block.",
                "Do not add explanations, tests, or any text outside that fence.",
            ]
        )
        prompts[idx] = "\n".join(sections).strip()

    return prompts
