from __future__ import annotations

from typing import Dict, List, Optional

from LLM_Collab_Code_Completion.utils.prompting import (
    build_take_job_prompt,
    build_agent_prompt,
)
from LLM_Collab_Code_Completion.utils.text_tools import (
    count_new_tokens,
    get_effective_max_new_tokens,
)


def _original_agent_prompt(
    *,
    skeleton: str,
    class_name: str,
    method_names: List[str],
    assignments: Dict[int, List[str]] | None,
    agent_idx: int,
    num_agents: int,
) -> str:
    """Rebuild the original per-agent prompt used at turn 1.

    - If explicit assignments exist, use build_agent_prompt with the agent's methods.
    - Otherwise (TAKE_JOB), use build_take_job_prompt with the full method set and N agents.
    """
    if assignments and any(assignments.values()):
        assigned = list(assignments.get(agent_idx, []) or [])
        return build_agent_prompt(
            skeleton=skeleton,
            class_name=class_name,
            assigned_methods=assigned,
        )
    return build_take_job_prompt(
        skeleton=skeleton,
        class_name=class_name,
        method_names=list(method_names or []),
        num_agents=num_agents,
    )


def format_followup_prompts(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    assignments: Dict[int, List[str]] | None,
    agent_completions: List[str],
    test_code: str,
    original_prompt_flag: bool = True,
    previous_response_flag: bool = True,
    num_agents: int = 2,
    *,
    prompt_history_per_agent: Optional[List[List[str]]] = None,
    response_history_per_agent: Optional[List[List[str]]] = None,
) -> List[str]:
    """Token report mode (per-agent minimal report).

    For each agent i, show only:
    - The original prompt shown to that agent at turn 1.
    - The agent's previous raw output.
    - Whether the previous output likely hit the max new tokens limit (using the same
      token counting and limit source as the reward logic).
    - A short instruction to revise the previous code.
    """
    n = int(num_agents)
    prompts: List[str] = [""] * n

    # Max tokens limit reference (reward clamps to [0, L-1])
    try:
        L = int(get_effective_max_new_tokens())
    except Exception:
        L = 512
    limit_ref = max(1, L - 1)

    for i in range(n):
        parts: List[str] = []

        # 1) Original per-agent prompt
        if original_prompt_flag:
            op = _original_agent_prompt(
                skeleton=skeleton,
                class_name=class_name,
                method_names=method_names,
                assignments=assignments,
                agent_idx=i,
                num_agents=n,
            )
            parts.extend([
                "Original prompt:",
                op,
                "",
            ])

        # 2) This agent's previous raw output only
        if previous_response_flag:
            raw_i = agent_completions[i] if i < len(agent_completions) else ""
            parts.extend([
                "Your previous raw output:",
                (raw_i if (raw_i or "").strip() else "<empty>"),
                "",
            ])

        # 3) Token usage / limit report (mirror reward's counter and limit source)
        try:
            used_tokens = count_new_tokens(agent_completions[i] if i < len(agent_completions) else "")
        except Exception:
            used_tokens = len((agent_completions[i] or "").split()) if i < len(agent_completions) else 0
        reached_limit = used_tokens >= limit_ref
        parts.extend([
            "Token usage:",
            f"- New tokens used: {used_tokens}/{limit_ref} (max)",
            f"- Reached max new token limit: {'Yes' if reached_limit else 'No'}",
            "",
        ])

        # 4) Closing instruction
        parts.append(
            "Revise your previous code. Keep your chosen targets consistent and improve correctness. Output ONLY the function definitions for those targets."
        )

        prompts[i] = "\n".join(parts)

    return prompts

