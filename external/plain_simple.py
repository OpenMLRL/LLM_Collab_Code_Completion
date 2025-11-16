from __future__ import annotations

from typing import List, Optional

import textwrap


def _first_turn_response(
    agent_idx: int,
    response_history_per_agent: Optional[List[List[str]]],
    fallback: str,
) -> str:
    if (
        response_history_per_agent
        and 0 <= agent_idx < len(response_history_per_agent)
        and response_history_per_agent[agent_idx]
    ):
        return response_history_per_agent[agent_idx][0] or ""
    return fallback or ""


def format_followup_prompts(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    assignments,
    agent_completions: List[str],
    original_prompt_flag: bool = True,
    previous_response_flag: bool = True,  # Unused but kept for API parity
    num_agents: int = 2,
    *,
    prompt_history_per_agent: Optional[List[List[str]]] = None,  # Unused
    response_history_per_agent: Optional[List[List[str]]] = None,
) -> List[str]:
    """Simplified follow-up prompt: ask each agent to revise its turn-1 code only."""
    n = int(num_agents)
    prompts: List[str] = [""] * n
    skeleton_block = textwrap.dedent(
        f"""
        Class skeleton reference for '{class_name or "unknown"}':
        SKELETON START
        {skeleton.strip()}
        SKELETON END
        """
    ).strip()

    for idx in range(n):
        previous_code = _first_turn_response(idx, response_history_per_agent, agent_completions[idx])
        if not previous_code.strip():
            previous_code = "<no turn-1 code captured>"

        sections: List[str] = []
        sections.append(
            "Modify the turn-1 code below. Keep every method signature unchanged and produce only the improved implementation."
        )
        if original_prompt_flag:
            sections.extend([skeleton_block, ""])
        sections.extend(
            [
                "Your turn-1 code:",
                "```python",
                previous_code.strip(),
                "```",
                "",
                "Respond with ONLY your revised implementation enclosed in a single ```python ...``` block.",
                "Do not add explanations, tests, or any text outside that fence.",
            ]
        )
        prompts[idx] = "\n".join(sections).strip()

    return prompts
