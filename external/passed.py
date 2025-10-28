from __future__ import annotations

from typing import Dict, List

from LLM_Collab_Code_Completion.utils.parse_completion import (
    extract_method_snippets,
)
from LLM_Collab_Code_Completion.utils.merge import merge_methods_into_skeleton
from LLM_Collab_Code_Completion.rewards.CE_reward import run_unittests_with_details
from .common import (
    build_agent_context_block,
    build_take_job_context_block,
    join_previous_impls,
)


def _union_merged_code(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    completions: List[str],
) -> str:
    method_set = set(method_names or [])
    method_to_code: Dict[str, str] = {}
    for text in completions:
        parsed = extract_method_snippets(text or "", allowed_methods=method_set)
        method_to_code.update(parsed)
    return merge_methods_into_skeleton(skeleton, class_name or "", method_to_code)


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
) -> List[str]:
    """Minimal pass/fail signal based on running the unit tests."""
    n = int(num_agents)
    prompts: List[str] = [""] * n

    combined = _union_merged_code(skeleton, class_name, method_names, agent_completions)
    res = run_unittests_with_details(combined, test_code)
    syntax_ok = bool(res.get("syntax_ok", False))
    total = int(res.get("testsRun", 0))
    passed_n = int(res.get("passed", 0))
    signal = (
        "All tests passed" if (syntax_ok and total > 0 and passed_n == total) else "Not all tests passed"
    )

    # collect previous snippets per agent
    method_set = set(method_names or [])
    prev_per_agent: List[List[str]] = []
    for text in agent_completions:
        parsed = extract_method_snippets(text or "", allowed_methods=method_set)
        vals = list(parsed.values())
        if not vals and (text or "").strip():
            vals = [(text or "").strip()]
        prev_per_agent.append(vals)

    for i in range(n):
        assigned = list(assignments.get(i, []) if assignments else [])
        if assignments and any(assignments.values()):
            base = build_agent_context_block(skeleton, class_name, assigned)
        else:
            base = build_take_job_context_block(
                skeleton=skeleton,
                class_name=class_name,
                method_names=list(method_names or []),
                num_agents=n,
            )

        parts: List[str] = []
        if original_prompt_flag:
            parts.extend([base, ""])  # context + blank
        if previous_response_flag:
            parts.extend([
                "Your previous implementation(s):",
                join_previous_impls(prev_per_agent[i]),
                "",
            ])
        parts.extend([
            f"Signal: {signal}",
            "",
        ])

        methods = list(method_names or [])
        total_methods = len(methods)
        target_count = (total_methods + n - 1) // n if total_methods > 0 else 0
        if assigned:
            closing = (
                f"Revise your code. Implement your assigned {len(assigned)} method(s)."
            )
        else:
            closing = (
                f"Revise your code. Aim for ~{max(1, target_count)} method(s)."
            )
        parts.append(closing)
        prompts[i] = "\n".join(parts)

    return prompts
