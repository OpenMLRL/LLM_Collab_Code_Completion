from __future__ import annotations

from typing import Dict, List

from LLM_Collab_Module_Completion.utils.parse_completion import (
    extract_method_snippets,
)
from LLM_Collab_Module_Completion.utils.merge import merge_methods_into_skeleton
from LLM_Collab_Module_Completion.rewards.CE_reward import run_unittests_with_details
from .common import (
    build_agent_context_block,
    build_take_job_context_block,
    join_previous_impls,
)


def _union_state(
    skeleton: str,
    class_name: str,
    method_names: List[str],
    completions: List[str],
):
    mset = set(method_names or [])
    method_to_code: Dict[str, str] = {}
    prev_per_agent: List[List[str]] = []
    implemented: set[str] = set()
    for text in completions:
        parsed = extract_method_snippets(text or "", allowed_methods=mset)
        prev_per_agent.append(list(parsed.values()))
        method_to_code.update(parsed)
        implemented.update(parsed.keys())
    combined = merge_methods_into_skeleton(skeleton, class_name or "", method_to_code)
    return prev_per_agent, combined, implemented


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
    """Compact signals: syntax/test result and implementation coverage."""
    n = int(num_agents)
    prompts: List[str] = [""] * n

    prev_per_agent, combined, implemented = _union_state(
        skeleton, class_name, method_names, agent_completions
    )
    res = run_unittests_with_details(combined, test_code)
    syntax_ok = bool(res.get("syntax_ok", False))
    total = int(res.get("testsRun", 0))
    passed_n = int(res.get("passed", 0))

    impl_sig = f"Implemented {len(implemented)}/{len(method_names)} methods"
    syntax_sig = "Syntax correct" if syntax_ok else "Syntax error"
    if total == 0:
        test_sig = "No tests found"
    elif passed_n == total:
        test_sig = "Passed all tests"
    elif passed_n == 0:
        test_sig = "No tests passed"
    else:
        test_sig = f"Passed {passed_n}/{total} tests"

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
            "Signals:",
            f"- {impl_sig}",
            f"- {syntax_sig}",
            f"- {test_sig}",
            "",
            "Revise ONLY the target methods. Output ONLY the function definition(s); no prose, no fences.",
        ])
        prompts[i] = "\n".join(parts)

    return prompts

