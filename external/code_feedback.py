from __future__ import annotations

from typing import Dict, List, Optional

import textwrap

from LLM_Collab_Code_Completion.rewards.CE_reward import run_unittests_with_details
from LLM_Collab_Code_Completion.utils.merge import (
    build_method_map_with_syntax_selection,
    merge_methods_into_skeleton,
)
from LLM_Collab_Code_Completion.utils.text_tools import (
    count_new_tokens,
    get_effective_max_new_tokens,
)


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


def _build_combined_code(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    assignments: Dict[int, List[str]] | None,
    agent_completions: List[str],
) -> str:
    partition: Dict[str, int] = {}
    if assignments and any(assignments.values()):
        for aidx, names in assignments.items():
            for name in (names or []):
                partition[name] = int(aidx)

    self_select = not (assignments and any(assignments.values()))

    try:
        method_to_code = build_method_map_with_syntax_selection(
            agent_texts=agent_completions,
            method_names=method_names,
            partition=partition,
            self_select=self_select,
        )
    except Exception:
        method_to_code = {}

    try:
        return merge_methods_into_skeleton(
            skeleton,
            class_name or "",
            method_to_code,
        )
    except Exception:
        return skeleton or ""


def format_followup_prompts(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    assignments: Dict[int, List[str]] | None,
    agent_completions: List[str],
    test_code: str,
    original_prompt_flag: bool = True,
    previous_response_flag: bool = True,  # kept for parity with other modes
    num_agents: int = 2,
    *,
    prompt_history_per_agent: Optional[List[List[str]]] = None,  # unused here
    response_history_per_agent: Optional[List[List[str]]] = None,
) -> List[str]:
    """Plain-simple revision prompt plus basic processed-output feedback."""
    n = int(num_agents)
    prompts: List[str] = [""] * n

    combined_code = _build_combined_code(
        skeleton,
        class_name or "",
        method_names,
        assignments,
        agent_completions,
    )
    run_res = run_unittests_with_details(combined_code, test_code)
    syntax_ok = bool(run_res.get("syntax_ok", False))

    try:
        limit_raw = int(get_effective_max_new_tokens())
    except Exception:
        limit_raw = 512
    limit_ref = max(1, limit_raw - 1)

    skeleton_block = textwrap.dedent(
        f"""
        Class skeleton reference for '{class_name or "unknown"}':
        SKELETON START
        {skeleton.strip()}
        SKELETON END
        """
    ).strip()

    for idx in range(n):
        previous_code = _first_turn_response(
            idx,
            response_history_per_agent,
            agent_completions[idx] if idx < len(agent_completions) else "",
        )
        if not (previous_code or "").strip():
            previous_code = "<no turn-1 code captured>"

        sections: List[str] = []
        sections.append(
            "Modify the turn-1 code below. Keep every method signature unchanged and produce only the improved implementation."
        )
        if original_prompt_flag:
            sections.extend([skeleton_block, ""])

        try:
            used_tokens = count_new_tokens(
                agent_completions[idx] if idx < len(agent_completions) else ""
            )
        except Exception:
            used_tokens = len(
                (agent_completions[idx] or "").split()
            ) if idx < len(agent_completions) else 0
        reached_limit = used_tokens >= limit_ref

        sections.extend(
            [
                "Processed output status:",
                f"- Syntax: {'OK' if syntax_ok else 'ERROR'}",
                f"- New tokens used: {used_tokens}/{limit_ref} (max)",
                f"- Reached max new token limit: {'Yes' if reached_limit else 'No'}",
                "",
            ]
        )

        if previous_response_flag:
            sections.extend(
                [
                    "Your turn-1 code:",
                    "```python",
                    previous_code.strip(),
                    "```",
                    "",
                ]
            )

        sections.extend(
            [
                "Respond with ONLY your revised implementation enclosed in a single ```python ...``` block.",
                "Do not add explanations, tests, or any text outside that fence.",
            ]
        )

        prompts[idx] = "\n".join(sections).strip()

    return prompts
